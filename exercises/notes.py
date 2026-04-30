"""
notes.py — All note definitions and progression logic.
French notation: DO, RE, MI, FA, SOL, LA, SI (+ dièses #)
Range: DO3 → DO6
"""
from django.conf import settings

# ── Complete chromatic scale in French notation ──────────────
CHROMATIC = ['DO', 'DO#', 'RE', 'RE#', 'MI', 'FA',
             'FA#', 'SOL', 'SOL#', 'LA', 'LA#', 'SI']

# ── Build all notes DO3 → DO6 ────────────────────────────────
ALL_NOTES = []
for octave in range(3, 7):
    for note in CHROMATIC:
        ALL_NOTES.append(f"{note}{octave}")
        if note == 'DO' and octave == 6:
            break
    else:
        continue
    break

# Natural (non-sharp) notes only — used for beginners
NATURAL_NOTES = [n for n in ALL_NOTES if '#' not in n]

# VexFlow note name mapping: French → VexFlow (English + octave)
FR_TO_VEXFLOW = {
    'DO':   'c', 'DO#':  'c#',
    'RE':   'd', 'RE#':  'd#',
    'MI':   'e',
    'FA':   'f', 'FA#':  'f#',
    'SOL':  'g', 'SOL#': 'g#',
    'LA':   'a', 'LA#':  'a#',
    'SI':   'b',
}

# Clef selection: notes below DO4 → bass, otherwise treble
TREBLE_NOTES = [n for n in ALL_NOTES if int(n[-1]) >= 4]
BASS_NOTES   = [n for n in ALL_NOTES if int(n[-1]) < 4]


def note_to_vexflow(note_fr_str):
    """
    Convert French note string to VexFlow format.
    'SOL4'  -> {'keys': ['g/4'],  'clef': 'treble', 'label': 'SOL4'}
    'DO#5'  -> {'keys': ['c#/5'], 'clef': 'treble', 'label': 'DO#5'}
    """
    import re
    m = re.match(r'^([A-Z]+#?)(\d+)$', note_fr_str)
    if not m:
        return {'keys': ['c/4'], 'clef': 'treble', 'label': note_fr_str}

    name   = m.group(1)
    octave = m.group(2)

    vex_name = FR_TO_VEXFLOW.get(name, 'c')
    clef = 'bass' if int(octave) < 4 else 'treble'

    return {
        'keys':  [f"{vex_name}/{octave}"],
        'clef':  clef,
        'label': note_fr_str,
    }


def get_notes_for_level(level):
    """Return the list of note labels available at a given level."""
    ranges = settings.LEVEL_NOTE_RANGES
    if level not in ranges:
        level = max(ranges.keys())
    start, end = ranges[level]

    try:
        i_start = ALL_NOTES.index(start)
        i_end   = ALL_NOTES.index(end)
        return ALL_NOTES[i_start:i_end + 1]
    except ValueError:
        return NATURAL_NOTES[:8]


def choose_next_note(level, session_stats=None):
    """
    Random note selection across the full available range.
    Weights notes by inverse success rate so weaker notes appear more.
    """
    import random
    available = get_notes_for_level(level)

    if not session_stats:
        return random.choice(available)

    # Weight by inverse success rate — unseen/failed notes get priority
    weights = []
    for note in available:
        stats = session_stats.get(note, {'attempts': 0, 'correct': 0})
        if stats['attempts'] == 0:
            weights.append(3.0)
        else:
            rate = stats['correct'] / stats['attempts']
            weights.append(max(0.1, 1.5 - rate))

    return random.choices(available, weights=weights, k=1)[0]


def should_level_up(session):
    """Check if the student deserves to move to the next level."""
    min_ex = settings.LEVEL_UP_MIN_EXERCISES
    threshold = settings.LEVEL_UP_THRESHOLD

    if session.total_exercises < min_ex:
        return False
    if session.level >= max(settings.LEVEL_NOTE_RANGES.keys()):
        return False

    rate = session.correct_count / session.total_exercises
    return rate >= threshold


LEVEL_NAMES = {
    1: 'Débutant',
    2: 'Élémentaire',
    3: 'Intermédiaire',
    4: 'Avancé',
}
