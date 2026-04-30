from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

from exercises.models import Session, Exercise, NoteStats
from exercises.notes import ALL_NOTES, LEVEL_NAMES


@login_required
def dashboard(request):
    """Main progress dashboard."""

    # ── Global stats ─────────────────────────────────────────
    all_exercises = Exercise.objects.filter(part=1)
    total_ex  = all_exercises.count()
    total_ok  = all_exercises.filter(correct=True).count()
    global_rate = round(total_ok / total_ex * 100, 1) if total_ex else 0

    # ── Recent sessions (last 10) ─────────────────────────────
    recent_sessions = Session.objects.all()[:10]

    # ── Per-note stats ────────────────────────────────────────
    note_stats = {
        ns.note: ns
        for ns in NoteStats.objects.all()
    }

    # ── Last 7 days activity ──────────────────────────────────
    week_ago = timezone.now() - timedelta(days=7)
    daily_counts = []
    for i in range(7):
        day = timezone.now() - timedelta(days=6 - i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end   = day_start + timedelta(days=1)
        count = Exercise.objects.filter(
            created_at__gte=day_start,
            created_at__lt=day_end,
            part=1
        ).count()
        correct = Exercise.objects.filter(
            created_at__gte=day_start,
            created_at__lt=day_end,
            part=1, correct=True
        ).count()
        daily_counts.append({
            'day': day.strftime('%a %d/%m'),
            'total': count,
            'correct': correct,
        })

    # ── Notes mastered (≥ 80% success, ≥ 5 attempts) ─────────
    mastered = [
        ns for ns in NoteStats.objects.all()
        if ns.total_attempts >= 5 and ns.success_rate >= 80
    ]

    # ── Hardest notes (≥ 5 attempts, lowest success rate) ────
    hardest = sorted(
        [ns for ns in NoteStats.objects.all() if ns.total_attempts >= 5],
        key=lambda x: x.success_rate
    )[:5]

    context = {
        'total_exercises': total_ex,
        'total_correct':   total_ok,
        'global_rate':     global_rate,
        'recent_sessions': recent_sessions,
        'note_stats':      note_stats,
        'all_notes':       ALL_NOTES,
        'daily_counts':    daily_counts,
        'mastered_count':  len(mastered),
        'mastered_notes':  mastered,
        'hardest_notes':   hardest,
        'level_names':     LEVEL_NAMES,
    }
    return render(request, 'dashboard/dashboard.html', context)


def stats_json(request):
    """Return full stats as JSON (for Chart.js)."""
    note_stats_qs = NoteStats.objects.all()
    data = {
        'notes': [
            {
                'note':         ns.note,
                'attempts':     ns.total_attempts,
                'correct':      ns.correct_count,
                'success_rate': ns.success_rate,
                'confidence':   round(ns.avg_confidence * 100, 1),
            }
            for ns in note_stats_qs
        ]
    }
    return JsonResponse(data)
