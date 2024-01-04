from django.test import TestCase, RequestFactory, Client
from django.core.cache import cache
from rest_framework.test import APIClient
from Notes.utils import DDoSMiddleware
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from accounts.serializers import UserSerializer
from .models import Note
import jwt
from accounts.auth import getUser
from django.conf import settings

User = get_user_model()

class ManageNotesTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {'email': 'test@example.com', 'password': 'test'}
        self.user = UserSerializer().create(self.user_data)
        self.token = jwt.encode({'id': self.user.id}, settings.SECRET_KEY, algorithm='HS256')
        self.client.cookies['jwt'] = str(self.token)

    def test_notes(self):
        with self.subTest('Test POST notes'):
            data = {'title': 'Test Note', 'note': 'Test Content'}
            data2 = {'title': 'Test Note 2', 'note': 'Test Content 2'}

            response = self.client.post('/api/notes', data)
            self.client.post('/api/notes', data2)

            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data['title'], 'Test Note')

            
        with self.subTest('Test GET notes'):
            response = self.client.get('/api/notes')

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data), 2)
            self.assertEqual(response.data[0]['title'], 'Test Note')
            self.assertEqual(response.data[1]['title'], 'Test Note 2')


        with self.subTest('Test GET note by ID'):
            response = self.client.get(f'/api/notes/2')

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['title'], 'Test Note 2')


        with self.subTest('Test PUT notes'):
            data = {'title': 'Updated Note', 'note': 'Test Content 2'}
            response = self.client.put('/api/notes/2', data)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['id'], 2)
            self.assertEqual(response.data['title'], 'Updated Note')


        with self.subTest('Test DELETE notes'):
            response = self.client.delete(f'/api/notes/1')
            self.assertEqual(response.status_code, 200)


    def tearDown(self):
        Note.objects.all().delete()
        User.objects.all().delete()





class DDoSMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = DDoSMiddleware(get_response=None)

    def test_request_limit(self):
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'

        # Simulate 6 requests from the same IP
        for _ in range(6):
            self.middleware.process_request(request)

        # Check that the 6th request is blocked
        response = self.middleware.process_request(request)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 403)

    def tearDown(self):
        cache.clear()