from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from django.core.exceptions import ObjectDoesNotExist
from .models import User
import jwt, datetime
from datetime import datetime,timedelta
from django.conf import settings
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

BLACKLIST = set()   # For convienience, we'll store the tokens in a set. Later, we'll use a persistent caching solution. Maybe Redis?

@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        user_serializer = UserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        return Response(user_serializer.data)


@api_view(['POST'])
def login(request):
    email = request.data['email']
    password = request.data['password']

    try:
        user = User.objects.get(email=email)
    except ObjectDoesNotExist:
        raise AuthenticationFailed("User not found")

    if not user.check_password(password):
        raise AuthenticationFailed("Incorrect password")
    
    payload = {
        'id': user.id,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }

    token = jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm='HS256')
    
    response = Response()

    response.set_cookie(key='jwt', value=token, httponly=True)
    response.data = {
        'jwt': token
    }

    return response

            
@api_view(['GET'])
def user_view(request):
    token = request.COOKIES.get('jwt')

    if not token:
        raise InvalidTokenError('Unauthenticated!')
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except ExpiredSignatureError:
        raise AuthenticationFailed("Unauthenticated request!")
    
    user = User.objects.get(id=payload['id'])
    serializer = UserSerializer(user)

    return Response(serializer.data)


@api_view(['POST'])
def logout(request):
    token = request.COOKIES.get('jwt')
    if token:
        BLACKLIST.add(token)
        print(f"{token} added to blacklist")
    for i in BLACKLIST:
        print(f"\nBlacklist:\n{i}\n\n")
    response = Response()
    response.delete_cookie('jwt')
    response.data = {
        'message': 'User logged out'
    }
    return response

