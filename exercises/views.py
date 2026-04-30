import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import Session, Exercise, NoteStats
from .notes import note_to_vexflow, LEVEL_NAMES, get_notes_for_level
from .bandit import get_bandit, save_bandit


# ── Helpers ──────────────────────────────────────────────────

def get_or_create_session(request):
    """Get active session from Django session, or create one."""
    session_id = request.session.get('exercise_session_id')
    if session_id:
        try:
            return Session.objects.get(pk=session_id)
        except Session.DoesNotExist:
            pass
    session = Session.objects.create(level=1)
    request.session['exercise_session_id'] = session.pk
    return session


# ── Main play view ────────────────────────────────────────────

@login_required
def play(request):
    """Main exercise page."""
    session = get_or_create_session(request)
    bandit  = get_bandit(request)

    _, note_label = bandit.select_note()
    note_vexflow  = note_to_vexflow(note_label)

    context = {
        'session':         session,
        'note_label':      note_label,
        'note_vexflow':    json.dumps(note_vexflow),
        'level':           session.level,
        'level_name':      LEVEL_NAMES.get(session.level, 'Débutant'),
        'available_notes': get_notes_for_level(session.level),
        'level_names':     LEVEL_NAMES,
    }
    return render(request, 'exercises/play.html', context)


# ── API: get next note ────────────────────────────────────────

@require_GET
def next_note(request):
    """Return the next note selected by Thompson Sampling bandit.
    Optional GET params:
      - octave: '1' (DO4-SI4), '2' (DO4-DO6), '3' (DO3-DO6)
      - accidentals: 'natural', 'sharp', 'flat', 'all'
    """
    from .notes import ALL_NOTES

    bandit = get_bandit(request)

    # ── Build allowed note list from filters ──────────────────
    octave_filter      = request.GET.get('octave', '3')
    accidental_filter  = request.GET.get('accidentals', 'natural')

    # Octave range
    octave_ranges = {
        '1': ('DO4', 'SI4'),
        '2': ('DO4', 'DO6'),
        '3': ('DO3', 'DO6'),
    }
    start, end = octave_ranges.get(octave_filter, ('DO3', 'DO6'))
    try:
        i_start = ALL_NOTES.index(start)
        i_end   = ALL_NOTES.index(end)
        octave_notes = set(ALL_NOTES[i_start:i_end + 1])
    except ValueError:
        octave_notes = set(ALL_NOTES)

    # The 5 sharps that have valid flat equivalents (black keys only)
    # FAb=MI and DOb=SI are white keys — excluded from flat mode
    VALID_SHARPS_FOR_FLAT = {'DO#', 'RE#', 'FA#', 'SOL#', 'LA#'}

    # Accidental filter
    if accidental_filter == 'natural':
        allowed = [n for n in octave_notes if '#' not in n]
    elif accidental_filter == 'sharp':
        allowed = list(octave_notes)   # natural + sharp (all notes)
    elif accidental_filter == 'flat':
        # Only: natural notes (white keys) + the 5 sharps that map to real flat names
        # Excludes: MI, FA, SI, DO would give FAb/DOb which are not real black-key flats
        allowed = [n for n in octave_notes
                   if '#' not in n or any(n.startswith(s) for s in VALID_SHARPS_FOR_FLAT)]
    elif accidental_filter == 'all':
        allowed = list(octave_notes)
    else:
        allowed = list(octave_notes)

    if not allowed:
        allowed = list(octave_notes)

    _, note_label = bandit.select_note(allowed_notes=allowed)
    note_vexflow  = note_to_vexflow(note_label)

    return JsonResponse({
        'note_label':  note_label,
        'note_vexflow': note_vexflow,
    })


# ── API: submit answer ────────────────────────────────────────

@csrf_exempt
@require_POST
def submit_answer(request):
    """
    Record the result of a note recognition attempt.
    Updates Thompson Sampling bandit in real time.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    session = get_or_create_session(request)
    bandit  = get_bandit(request)

    note_displayed = data.get('note_displayed', '')
    note_answered  = data.get('note_answered', '')
    correct        = bool(data.get('correct', False))
    confidence     = float(data.get('confidence', 0.0))
    attempts       = int(data.get('attempts', 1))
    response_time  = int(data.get('response_time_ms', 0))

    # ── Update bandit (online learning) ──────────────────────
    bandit.update_by_name(note_displayed, correct)
    save_bandit(request, bandit)

    # ── Save exercise to DB ───────────────────────────────────
    Exercise.objects.create(
        session=session,
        part=1,
        note_displayed=note_displayed,
        note_answered=note_answered,
        correct=correct,
        confidence=confidence,
        attempts=attempts,
        response_time_ms=response_time,
    )

    # ── Update session counters ───────────────────────────────
    session.total_exercises += 1
    if correct:
        session.correct_count += 1
    session.save()

    # ── Update global NoteStats ───────────────────────────────
    NoteStats.record(note_displayed, correct, confidence)

    # ── Bandit analysis for frontend ──────────────────────────
    weak_notes = bandit.get_weak_notes()

    return JsonResponse({
        'ok':              True,
        'session_total':   session.total_exercises,
        'session_correct': session.correct_count,
        'success_rate':    session.success_rate,
        'weak_notes':      [w['note'] for w in weak_notes[:3]],
    })


# ── API: bandit stats (used by dashboard) ────────────────────

@require_GET
def bandit_stats(request):
    """Return full bandit state as JSON for the achievement dashboard."""
    bandit = get_bandit(request)
    return JsonResponse({
        'total_exercises': bandit.total_exercises(),
        'overall_rate':    bandit.overall_success_rate(),
        'all_stats':       bandit.get_all_stats(),
        'weak_notes':      bandit.get_weak_notes(),
        'strong_notes':    bandit.get_strong_notes(),
    })


# ── API: reset session ────────────────────────────────────────

@require_POST
def reset_session(request):
    """Close current session and start fresh (bandit is preserved)."""
    session_id = request.session.get('exercise_session_id')
    if session_id:
        try:
            s = Session.objects.get(pk=session_id)
            s.ended_at = timezone.now()
            s.save()
        except Session.DoesNotExist:
            pass
        del request.session['exercise_session_id']
    return JsonResponse({'ok': True})


@require_POST
@login_required
def reset_bandit(request):
    """Reset the bandit — delete DB state and start learning from scratch."""
    # Clear session fallback
    if 'bandit_state' in request.session:
        del request.session['bandit_state']
    # Clear DB state for this user
    if request.user.is_authenticated:
        from .models import BanditState
        BanditState.objects.filter(user=request.user).delete()
    return JsonResponse({'ok': True})
