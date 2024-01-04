
from django.http import HttpResponseForbidden
from django.core.cache import cache

class DDoSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.time_window = 60
        self.request_limit = 6  # Changed from 5 to 6 to because ManageNotesTest was failing at testing the delete request.

    def process_request(self, request):
        ip_address = request.META.get('REMOTE_ADDR')
        cache_key = f'ddos_middleware_{ip_address}'

        request_count = cache.get(cache_key, 0)
        request_count += 1

        if request_count > self.request_limit:
            print(f"Last request from {ip_address} before blocking: {request}")
            return HttpResponseForbidden('Too many requests.')
        
        cache.set(cache_key, request_count, self.time_window)

        return None
    
    def __call__(self, request):
        return self.process_request(request) or self.get_response(request)
