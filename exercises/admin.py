from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg
from .models import Session, Exercise, NoteStats


# ── Shared helpers ────────────────────────────────────────────

def pct_bar(value, low=65, high=80):
    """Render a coloured percentage bar for list_display."""
    if value is None:
        return format_html('<span style="color:#6b6b6b">—</span>')
    pct = round(value * 100) if value <= 1 else round(value)
    if pct >= high:
        color = '#3ddc84'   # green — mastered
    elif pct >= low:
        color = '#f0cc78'   # gold  — learning
    else:
        color = '#ff5a5a'   # red   — needs work
    bar = (
        f'<div style="display:flex;align-items:center;gap:6px">'
        f'<div style="flex:1;background:rgba(255,255,255,0.08);'
        f'border-radius:3px;height:6px;width:80px;overflow:hidden">'
        f'<div style="width:{pct}%;height:100%;background:{color};'
        f'border-radius:3px;transition:width .4s"></div></div>'
        f'<span style="color:{color};font-weight:600;min-width:38px">{pct}%</span>'
        f'</div>'
    )
    return format_html(bar)


def bool_badge(value, true_label='✅ Oui', false_label='❌ Non'):
    if value:
        return format_html(
            '<span style="background:rgba(61,220,132,0.15);color:#3ddc84;'
            'padding:2px 10px;border-radius:999px;font-size:0.8rem;'
            'font-weight:600">{}</span>', true_label)
    return format_html(
        '<span style="background:rgba(255,90,90,0.15);color:#ff5a5a;'
        'padding:2px 10px;border-radius:999px;font-size:0.8rem;'
        'font-weight:600">{}</span>', false_label)


def note_badge(note):
    is_sharp = '#' in str(note)
    is_flat  = 'b' in str(note) and not str(note).startswith('b')
    if is_sharp:
        color = '#a78bfa'   # purple for sharps
    elif is_flat:
        color = '#60a5fa'   # blue for flats
    else:
        color = '#d4aa50'   # gold for naturals
    return format_html(
        '<span style="background:rgba(212,170,80,0.1);color:{};'
        'padding:2px 12px;border-radius:6px;font-weight:700;'
        'font-size:0.95rem;letter-spacing:0.04em">{}</span>',
        color, note)


# ══════════════════════════════════════════════════════════════
#  SESSION ADMIN
# ══════════════════════════════════════════════════════════════
@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display  = [
        'id', 'user_display', 'started_at', 'level_badge',
        'total_exercises', 'correct_count', 'success_bar',
    ]
    list_filter   = ['level', 'started_at']
    readonly_fields = ['started_at', 'ended_at']
    ordering      = ['-started_at']
    list_per_page = 25

    @admin.display(description='Utilisateur')
    def user_display(self, obj):
        name = getattr(obj, 'user', None)
        if name:
            return format_html(
                '<span style="color:#f5f0e8;font-weight:600">👤 {}</span>', name)
        return '—'

    @admin.display(description='Niveau')
    def level_badge(self, obj):
        colors = {1:'#3ddc84', 2:'#f0cc78', 3:'#f97316', 4:'#ef4444'}
        c = colors.get(obj.level, '#d4aa50')
        return format_html(
            '<span style="background:rgba(212,170,80,0.1);color:{};'
            'padding:2px 10px;border-radius:999px;font-weight:700">Niv. {}</span>',
            c, obj.level)

    @admin.display(description='Taux de succès')
    def success_bar(self, obj):
        return pct_bar(obj.success_rate)


# ══════════════════════════════════════════════════════════════
#  EXERCISE ADMIN
# ══════════════════════════════════════════════════════════════
@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display  = [
        'id', 'note_displayed_badge', 'note_answered_badge',
        'correct_badge', 'confidence_bar', 'attempts', 'created_at',
    ]
    list_filter   = ['correct', 'part', 'created_at']
    search_fields = ['note_displayed', 'note_answered']
    ordering      = ['-created_at']
    list_per_page = 50
    date_hierarchy = 'created_at'

    @admin.display(description='Note jouée')
    def note_displayed_badge(self, obj):
        return note_badge(obj.note_displayed)

    @admin.display(description='Note reconnue')
    def note_answered_badge(self, obj):
        return note_badge(obj.note_answered)

    @admin.display(description='Correct')
    def correct_badge(self, obj):
        return bool_badge(obj.correct, '✅ Correct', '❌ Raté')

    @admin.display(description='Confiance ML')
    def confidence_bar(self, obj):
        return pct_bar(obj.confidence)


# ══════════════════════════════════════════════════════════════
#  NOTE STATS ADMIN
# ══════════════════════════════════════════════════════════════
@admin.register(NoteStats)
class NoteStatsAdmin(admin.ModelAdmin):
    list_display  = [
        'note_badge_col', 'total_attempts', 'correct_count',
        'success_bar', 'confidence_bar', 'status_badge', 'last_seen',
    ]
    list_filter   = ['last_seen']
    search_fields = ['note']
    ordering      = ['note']
    list_per_page = 40

    @admin.display(description='Note', ordering='note')
    def note_badge_col(self, obj):
        return note_badge(obj.note)

    @admin.display(description='Taux de succès')
    def success_bar(self, obj):
        return pct_bar(obj.success_rate)

    @admin.display(description='Confiance moy.')
    def confidence_bar(self, obj):
        return pct_bar(obj.avg_confidence)

    @admin.display(description='Statut')
    def status_badge(self, obj):
        rate = obj.success_rate
        if obj.total_attempts == 0:
            return format_html(
                '<span style="color:#6b5e48;font-size:0.8rem">Pas vu</span>')
        if rate is None:
            return '—'
        pct = round(rate * 100) if rate <= 1 else round(rate)
        if pct >= 80:
            return format_html(
                '<span style="background:rgba(61,220,132,0.15);color:#3ddc84;'
                'padding:2px 10px;border-radius:999px;font-size:0.8rem;'
                'font-weight:600">✅ Maîtrisé</span>')
        if pct >= 65:
            return format_html(
                '<span style="background:rgba(240,204,120,0.15);color:#f0cc78;'
                'padding:2px 10px;border-radius:999px;font-size:0.8rem;'
                'font-weight:600">📚 En cours</span>')
        return format_html(
            '<span style="background:rgba(255,90,90,0.15);color:#ff5a5a;'
            'padding:2px 10px;border-radius:999px;font-size:0.8rem;'
            'font-weight:600">⚠️ À travailler</span>')


# ── Admin site global customisation ──────────────────────────
admin.site.site_header  = '𝄞 Teach Me Music'
admin.site.site_title   = 'Teach Me Music Admin'
admin.site.index_title  = 'Panneau d\'administration'
