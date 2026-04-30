from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password


class UserProfile(models.Model):
    """Extends Django User with a musical note password."""
    user          = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    note_password = models.CharField(max_length=255)
    created_at    = models.DateTimeField(auto_now_add=True)

    def set_note_password(self, note_sequence):
        raw = "-".join(note_sequence)
        self.note_password = make_password(raw)

    def check_note_password(self, note_sequence):
        raw = "-".join(note_sequence)
        return check_password(raw, self.note_password)

    def __str__(self):
        return f"Profile({self.user.username})"
