from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializers import NoteSerializer
from .models import Note
from accounts.auth import getUser, HasValidToken
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q

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
def share_note(request, id):
    '''
    Share a note with another user using their email.
    '''
    user = getUser(request.COOKIES.get('jwt'))
    note = get_object_or_404(Note, id=id)

    # Check if the user is the owner of the note
    if not user == note.owner:
        return Response({'detail': 'You are not authorized to share this note.'}, status=status.HTTP_401_UNAUTHORIZED)

    share_with_email = request.data.get('share_with', '') # Get the email of the user to share the note with from the request data
    try:
        share_with_user = get_user_model().objects.get(email=share_with_email) # Get the user object from the email
        Note.objects.create(title=note.title, note=note.note, owner=share_with_user) # Create a new note for the user
        return Response({'detail': 'Note shared successfully.'}, status=status.HTTP_200_OK)
    except get_user_model().DoesNotExist:
        return Response({'detail': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)
    


@api_view(['GET'])
@permission_classes([HasValidToken])
def search(request):
    user = getUser(request.COOKIES.get('jwt'))
    query = request.GET.get('q', '')
    print(query)
    if query:
        # Search notes based on keywords for the authenticated user
        notes = Note.objects.filter(Q(owner=user) & (Q(title__icontains=query) | Q(note__icontains=query)))
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)
    else:
        return Response({'detail': 'Please provide a search query.'}, status=status.HTTP_400_BAD_REQUEST)