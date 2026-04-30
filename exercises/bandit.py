"""
bandit.py — Thompson Sampling Multi-Armed Bandit
Adaptive note selection for Teach Me Music.

Each note = one arm. The bandit selects notes with LOW estimated
success probability more often → focuses practice on weak notes.
Stored as JSON in Django session → zero extra DB table needed.
"""
import numpy as np

NOTES = [
    'DO3','DO#3','RE3','RE#3','MI3','FA3','FA#3','SOL3','SOL#3','LA3','LA#3','SI3',
    'DO4','DO#4','RE4','RE#4','MI4','FA4','FA#4','SOL4','SOL#4','LA4','LA#4','SI4',
    'DO5','DO#5','RE5','RE#5','MI5','FA5','FA#5','SOL5','SOL#5','LA5','LA#5','SI5',
    'DO6',
]


class ThompsonSamplingBandit:
    """
    Multi-Armed Bandit with Thompson Sampling.

    For each note i, success probability is modelled as:
        P(success_i) ~ Beta(alpha_i, beta_i)
    where alpha_i = successes + 1, beta_i = failures + 1 (uniform prior).

    select_note() draws one sample per note and returns the note
    with the LOWEST sample → weakest notes are practiced more.
    """

    def __init__(self, notes=None):
        self.notes  = notes or list(NOTES)
        self.n      = len(self.notes)
        self.alpha  = np.ones(self.n)          # successes + 1
        self.beta   = np.ones(self.n)          # failures  + 1
        self.counts = np.zeros(self.n, dtype=int)
        self.history = []                      # list of (note_idx, success)

    # ── Core methods ──────────────────────────────────────────

    def select_note(self, exclude_last=True, allowed_notes=None):
        """
        Thompson Sampling: sample Beta(alpha_i, beta_i) for every note,
        return the note with the lowest sample (weakest estimated performance).
        Avoids repeating the same note twice in a row.
        allowed_notes: optional list of note names to restrict selection to.
        """
        samples = np.random.beta(self.alpha, self.beta)

        if exclude_last and self.history:
            last_idx = self.history[-1][0]
            samples[last_idx] = 1.0

        # Mask out notes not in allowed set
        if allowed_notes is not None:
            allowed_set = set(allowed_notes)
            for i, note in enumerate(self.notes):
                if note not in allowed_set:
                    samples[i] = 1.0  # push to max so they're never picked

        idx = int(np.argmin(samples))
        return idx, self.notes[idx]

    def update(self, note_idx, success):
        """Update Beta distribution after an exercise result."""
        if success:
            self.alpha[note_idx] += 1
        else:
            self.beta[note_idx] += 1
        self.counts[note_idx] += 1
        self.history.append((note_idx, int(success)))

    def update_by_name(self, note_name, success):
        """Convenience wrapper: update by French note name (e.g. 'SOL#4')."""
        if note_name in self.notes:
            self.update(self.notes.index(note_name), int(success))

    # ── Analysis ──────────────────────────────────────────────

    def get_success_rates(self):
        """Return estimated success rate (Beta mean) for every note."""
        return (self.alpha / (self.alpha + self.beta)).tolist()

    def get_weak_notes(self, threshold=0.65, min_attempts=3):
        """Notes below threshold — need more practice."""
        rates = self.get_success_rates()
        weak = [
            {
                'note':     self.notes[i],
                'rate':     round(rates[i], 3),
                'attempts': int(self.counts[i]),
                'pct':      round(rates[i] * 100, 1),
            }
            for i in range(self.n)
            if rates[i] < threshold and self.counts[i] >= min_attempts
        ]
        return sorted(weak, key=lambda x: x['rate'])

    def get_strong_notes(self, threshold=0.80, min_attempts=3):
        """Notes above threshold — well mastered."""
        rates = self.get_success_rates()
        strong = [
            {
                'note':     self.notes[i],
                'rate':     round(rates[i], 3),
                'attempts': int(self.counts[i]),
                'pct':      round(rates[i] * 100, 1),
            }
            for i in range(self.n)
            if rates[i] >= threshold and self.counts[i] >= min_attempts
        ]
        return sorted(strong, key=lambda x: x['rate'], reverse=True)

    def get_all_stats(self):
        """Full stats for every note — used by dashboard."""
        rates = self.get_success_rates()
        return [
            {
                'note':     self.notes[i],
                'rate':     round(rates[i], 3),
                'pct':      round(rates[i] * 100, 1),
                'attempts': int(self.counts[i]),
                'alpha':    float(self.alpha[i]),
                'beta':     float(self.beta[i]),
                'status':   (
                    'mastered' if rates[i] >= 0.80 and self.counts[i] >= 3
                    else 'weak'    if rates[i] <  0.65 and self.counts[i] >= 3
                    else 'unseen'  if self.counts[i] == 0
                    else 'learning'
                ),
            }
            for i in range(self.n)
        ]

    def total_exercises(self):
        return int(self.counts.sum())

    def overall_success_rate(self):
        if not self.history:
            return 0.0
        return round(sum(s for _, s in self.history) / len(self.history), 3)

    # ── Serialization (stored as JSON in Django session) ──────

    def to_dict(self):
        return {
            'notes':   self.notes,
            'alpha':   self.alpha.tolist(),
            'beta':    self.beta.tolist(),
            'counts':  self.counts.tolist(),
            'history': [(int(idx), int(s)) for idx, s in self.history],
        }

    @classmethod
    def from_dict(cls, d):
        b = cls(d['notes'])
        b.alpha   = np.array(d['alpha'])
        b.beta    = np.array(d['beta'])
        b.counts  = np.array(d['counts'], dtype=int)
        b.history = [(int(x[0]), int(x[1])) for x in d['history']]
        return b


# ── Django session helpers ────────────────────────────────────

def get_bandit(request):
    """Load bandit from DB (per user) or session (anonymous fallback)."""
    if request.user.is_authenticated:
        from .models import BanditState
        import json
        try:
            bs = BanditState.objects.get(user=request.user)
            state = json.loads(bs.state_json)
            if state:
                return ThompsonSamplingBandit.from_dict(state)
        except BanditState.DoesNotExist:
            pass
        return ThompsonSamplingBandit()
    # Anonymous fallback: session
    state = request.session.get('bandit_state')
    if state:
        try:
            return ThompsonSamplingBandit.from_dict(state)
        except Exception:
            pass
    return ThompsonSamplingBandit()


def save_bandit(request, bandit):
    """Persist bandit state to DB (per user) or session (anonymous fallback)."""
    if request.user.is_authenticated:
        from .models import BanditState
        import json
        BanditState.objects.update_or_create(
            user=request.user,
            defaults={'state_json': json.dumps(bandit.to_dict())}
        )
        return
    # Anonymous fallback: session
    request.session['bandit_state'] = bandit.to_dict()
    request.session.modified = True