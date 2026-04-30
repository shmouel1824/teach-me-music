from django.db import models
from django.utils import timezone


class Session(models.Model):
    """One practice session (browser visit)."""
    started_at  = models.DateTimeField(default=timezone.now)
    ended_at    = models.DateTimeField(null=True, blank=True)
    level       = models.PositiveSmallIntegerField(default=1)

    # Computed stats (updated after each exercise)
    total_exercises = models.PositiveIntegerField(default=0)
    correct_count   = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"Session {self.pk} — niveau {self.level} — {self.started_at:%d/%m/%Y %H:%M}"

    @property
    def success_rate(self):
        if self.total_exercises == 0:
            return 0.0
        return round(self.correct_count / self.total_exercises * 100, 1)

    @property
    def duration_seconds(self):
        if self.ended_at:
            return (self.ended_at - self.started_at).seconds
        return (timezone.now() - self.started_at).seconds


class Exercise(models.Model):
    """One note-recognition attempt."""

    PART_CHOICES = [
        (1, 'Partie 1 — Écoute'),
        (2, 'Partie 2 — Dessin'),
    ]

    session         = models.ForeignKey(Session, on_delete=models.CASCADE,
                                        related_name='exercises')
    part            = models.PositiveSmallIntegerField(choices=PART_CHOICES, default=1)
    note_displayed  = models.CharField(max_length=8)   # ex: 'SOL4'
    note_answered   = models.CharField(max_length=8, blank=True)  # what model predicted
    correct         = models.BooleanField(default=False)
    confidence      = models.FloatField(default=0.0)   # model confidence 0–1
    attempts        = models.PositiveSmallIntegerField(default=1)  # tries before correct
    response_time_ms= models.PositiveIntegerField(default=0)       # ms from display to answer
    created_at      = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        status = '✅' if self.correct else '❌'
        return f"{status} {self.note_displayed} → {self.note_answered} (session {self.session_id})"


class NoteStats(models.Model):
    """Cumulative stats per note across all sessions."""
    note            = models.CharField(max_length=8, unique=True)
    total_attempts  = models.PositiveIntegerField(default=0)
    correct_count   = models.PositiveIntegerField(default=0)
    avg_confidence  = models.FloatField(default=0.0)
    last_seen       = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['note']

    def __str__(self):
        return f"{self.note} — {self.success_rate}%"

    @property
    def success_rate(self):
        if self.total_attempts == 0:
            return 0.0
        return round(self.correct_count / self.total_attempts * 100, 1)

    @classmethod
    def record(cls, note, correct, confidence):
        obj, _ = cls.objects.get_or_create(note=note)
        obj.total_attempts += 1
        if correct:
            obj.correct_count += 1
        # Rolling average of confidence
        obj.avg_confidence = (
            (obj.avg_confidence * (obj.total_attempts - 1) + confidence)
            / obj.total_attempts
        )
        obj.last_seen = timezone.now()
        obj.save()


class BanditState(models.Model):
    """Persists Thompson Sampling bandit state per user in the database."""
    user       = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='bandit_state')
    state_json = models.TextField(default='{}')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"BanditState({self.user.username})"
