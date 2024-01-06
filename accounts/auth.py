import jwt
from jwt.exceptions import ExpiredSignatureError   
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.conf import settings
import accounts.views as accounts_views
from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()

class TokenBlacklistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.COOKIES.get('jwt')
        if token in accounts_views.BLACKLIST   :
            print(f"{token} is blacklisted")  # Debug print
            response = self.get_response(request)
            response.status_code = 401
            response.data = {'message': 'Token is blacklisted'}
            return response

        response = self.get_response(request)
        return response


class HasValidToken(permissions.BasePermission):
    def has_permission(self, request, view):
        token = request.COOKIES.get('jwt')
        user = getUser(token)
        return user is not None and not isinstance(user, HttpResponse)

def verify_token(token):
    if token in accounts_views.BLACKLIST:
        print("Token is in the blacklist. Access Denied")
        raise PermissionDenied("Token Blacklisted. Access denied.")
    
    try:
        jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except ExpiredSignatureError:
        print("Token has expired. Access denied.")
        raise PermissionDenied("Token has expired")
    

def getUser(token):
    if not token:
        return HttpResponse(status=418)
    
    try:
        verify_token(token)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except ExpiredSignatureError:
        return HttpResponse(status=418)
    
    user = User.objects.get(id=payload['id'])
    return user