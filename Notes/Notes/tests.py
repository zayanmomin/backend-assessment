from django.core.cache import cache
from django.test import TestCase, RequestFactory
from Notes.utils import DDoSMiddleware

class DDoSMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = DDoSMiddleware(get_response=None)

    def test_request_limit(self):
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'

        # Simulate n requests from the same IP
        for _ in range(10):
            self.middleware.process_request(request)

        # Check that the nth request is blocked
        response = self.middleware.process_request(request)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 403)

    def tearDown(self):
        cache.clear()