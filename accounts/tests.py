from django.test import TestCase, RequestFactory, Client
from django.http import HttpResponse
from accounts.views import BLACKLIST
from rest_framework.test import APIClient
from .auth import TokenBlacklistMiddleware
from .serializers import UserSerializer
import jwt
from django.conf import settings
import time
import json
from django.contrib.auth import get_user_model

class Registration_Test(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "email": "testuser@test.com",
            "password": "testpassword"
        }

    def test_register(self):
        response = self.client.post('/api/auth/signup/', self.user_data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(get_user_model().objects.count(), 1)
    

class JWT_Tests(TestCase):
    '''
    Tests for user registration, login, blacklisting and expiring JWTs.
    '''
    
    def setUp(self):
        '''
        * Create a user.
        * Create a token for the user.
        * Add the token to the client's cookies.
        '''
        self.client = APIClient()
        self.user_data = {'email': 'test@example.com', 'password': 'test'}
        self.user = UserSerializer().create(self.user_data)
        self.token = jwt.encode({'id': self.user.id}, settings.SECRET_KEY, algorithm='HS256')
        self.client.cookies['jwt'] = str(self.token)


    def test_blacklisted_token(self):
        '''
        * Simulate the user logging out, which adds the token to the blacklist.
        * Add the blacklisted token as a cookie.
        * Simulate a GET request to /api/notes with the blacklisted token.
        * Check that the response has a 401 status code.

        - This also tests the logout view.
        '''

        self.client.post('/api/auth/logout/')

        self.assertIn(str(self.token), BLACKLIST)

        self.client.cookies['jwt'] = str(self.token)

        response = self.client.get('/api/notes')

        self.assertEqual(response.status_code, 401)
    

    def test_expired_token(self):
        '''
        * Create a token that expires in 1 second.
        * Add the token to the client's cookies.
        * Wait for the token to expire.
        * Simulate a GET request to /api/notes with the expired token.
        * Check that the response has a 403 status code.
        '''

        self.token = jwt.encode({'id': self.user.id, 'exp': time.time() + 1}, settings.SECRET_KEY, algorithm='HS256')
        self.client.cookies['jwt'] = str(self.token)

        print("Waiting 2 seconds for token to expire...")
        time.sleep(2)

        response = self.client.get('/api/notes')

        self.assertEqual(response.status_code, 403)
