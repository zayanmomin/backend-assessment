from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializers import NoteSerializer
from .models import Note
from accounts.auth import getUser, HasValidToken
from rest_framework import status
from django.shortcuts import get_object_or_404

# Create your views here.

'''
GET /api/notes: get a list of all notes for the authenticated user.
GET /api/notes/:id: get a note by ID for the authenticated user.
POST /api/notes: create a new note for the authenticated user.
PUT /api/notes/:id: update an existing note by ID for the authenticated user.
DELETE /api/notes/:id: delete a note by ID for the authenticated user.
POST /api/notes/:id/share: share a note with another user for the authenticated user.
GET /api/search?q=:query: search for notes based on keywords for the authenticated user.
'''


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([HasValidToken])
def manage_notes(request, id=None):
    '''
    CRUD Operations for notes.

    Overview:
        * Check if the user is authenticated.
        * Get the user object from the token.
        * Check for request method.
        * Perform the operation.
    '''
    data = request.data
    token = request.COOKIES.get('jwt')
    user = getUser(token)

    # Getting notes
    if request.method == 'GET':

        # Get a note by ID
        if id:
            try:
                note = Note.objects.get(id=id, owner=user)
                serializer = NoteSerializer(note)
                return Response(serializer.data)
            except Note.DoesNotExist:
                return Response({'detail': 'Note not found.'}, status=status.HTTP_404_NOT_FOUND)
            
        # Get all notes
        notes = Note.objects.filter(owner=user)
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)


    # Creating a new note
    if request.method == 'POST':
        serializer = NoteSerializer(data=data)
        if serializer.is_valid():
            serializer.save(owner=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    # Updating an existing note
    if request.method == 'PUT':
        note = get_object_or_404(Note, id=id, owner=user)
        if note.owner == user:
            serializer = NoteSerializer(note, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            

    # Deleting an existing note
    if request.method == 'DELETE':
        note = get_object_or_404(Note, id=id, owner=user)
        if note.owner == user:
            note.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail': 'You are not authorized to delete this note.'}, status=status.HTTP_401_UNAUTHORIZED)
        



@api_view(['POST'])
@permission_classes([HasValidToken])
def share_note(request):
    pass


