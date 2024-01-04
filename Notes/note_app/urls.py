from django.urls import path
from .views import manage_notes, share_note, search

urlpatterns = [
    path('notes', view=manage_notes, name='get_notes'),
    path('notes/<int:id>', view=manage_notes, name='get_note_with_id'),
    path('notes/<int:id>/share', view=share_note, name='share_note'),
    path('search', view=search, name='search_notes'),
]