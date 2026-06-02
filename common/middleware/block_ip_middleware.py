
import time
import threading
from django.conf import settings
from django.http import JsonResponse


class BlockIPMiddleware:

    _lock = threading.Lock()
    _requests = {}

    def __init__(self, get_response):
        self.get_response = get_response

        config = getattr(settings, "BLOCK_IP_CONFIG", {})

        self.TIME_WINDOW = config.get("TIME_WINDOW", 60)          # seconds
        self.DEFAULT_MAX_REQUESTS = config.get("DEFAULT_MAX_REQUESTS", 100)
        self.SPECIAL_URLS = config.get("SPECIAL_URLS", {})        # {"/api/login/": 5}
        self.MAX_IPS = config.get("MAX_IPS", 10000)               # memory protection

    def __call__(self, request):
        ip = self._get_client_ip(request)
        path = request.path

        now = time.time()
        max_requests = self.SPECIAL_URLS.get(path, self.DEFAULT_MAX_REQUESTS)

        with self._lock:
            self._cleanup(now)

            timestamps = self._requests.get(ip, [])
            timestamps = [t for t in timestamps if now - t <= self.TIME_WINDOW]

            if len(timestamps) >= max_requests:
                return JsonResponse(
                    {
                        "detail": "Too many requests. Please try again later.",
                        "retry_after": self.TIME_WINDOW,
                    },
                    status=429,
                )

            timestamps.append(now)
            self._requests[ip] = timestamps

        return self.get_response(request)

    def _get_client_ip(self, request):
        """
        Correct IP detection behind Nginx / proxy
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()

        return request.META.get("REMOTE_ADDR", "unknown")

    def _cleanup(self, now):
        """
        Prevent memory leak by removing old IPs
        """
        expired_ips = [
            ip for ip, times in self._requests.items()
            if not any(now - t <= self.TIME_WINDOW for t in times)
        ]

        for ip in expired_ips:
            self._requests.pop(ip, None)

        if len(self._requests) > self.MAX_IPS:
            self._requests.clear()
