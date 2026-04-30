from django.contrib import admin
from .models import Session, Exercise, NoteStats

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'started_at', 'level', 'total_exercises',
                    'correct_count', 'success_rate']
    readonly_fields = ['started_at', 'ended_at']

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'note_displayed', 'note_answered',
                    'correct', 'confidence', 'attempts', 'created_at']
    list_filter = ['correct', 'part']
    search_fields = ['note_displayed', 'note_answered']

@admin.register(NoteStats)
class NoteStatsAdmin(admin.ModelAdmin):
    list_display = ['note', 'total_attempts', 'correct_count',
                    'success_rate', 'avg_confidence', 'last_seen']
