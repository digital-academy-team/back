import os, json, uuid, traceback
from datetime import datetime
from threading import Lock
from django.http import JsonResponse, Http404
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, ValidationError, Throttled
from django.conf import settings
from pathlib import Path


class GlobalExceptionLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.file_lock = Lock()

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        status_code = self.get_status_code_from_exception(exception)

        # write only 500 errors
        if status_code not in [400, 401, 403, 404, 429]:
            self.log_unhandled_error(exception, request)

        payload = {
            "success": False,
            "error_message": "Error occur in the server!",
            "error_detail": str(exception)
        }
        return JsonResponse(payload, status=status_code, json_dumps_params={"ensure_ascii": False})

    def get_status_code_from_exception(self, exception):
        if isinstance(exception, Http404):
            return 404
        elif isinstance(exception, PermissionDenied):
            return 403
        elif isinstance(exception, (AuthenticationFailed, NotAuthenticated)):
            return 401
        elif isinstance(exception, ValidationError):
            return 400
        elif isinstance(exception, Throttled):
            return 429
        elif hasattr(exception, "status_code") and isinstance(exception.status_code, int):
            return exception.status_code
        return 500  # default

    def log_unhandled_error(self, exception, request):
        log_file = Path(getattr(settings, "UNHANDLED_ERROR_LOG_FILE", "unhandled_errors.json"))
        os.makedirs(log_file.parent or ".", exist_ok=True)

        error_data = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "method": request.method,
            "path": request.get_full_path(),
            "user_id": getattr(request.user, "id", None),
            "error": repr(exception),
            "traceback": traceback.format_exc(),
        }

        with self.file_lock:
            try:
                if log_file.exists():
                    with open(log_file, "r", encoding="utf-8") as f:
                        logs = json.load(f)
                    if not isinstance(logs, list):
                        logs = []
                else:
                    logs = []
            except (FileNotFoundError, json.JSONDecodeError):
                logs = []

            logs.insert(0, error_data)

            tmp_file = log_file.with_suffix(log_file.suffix + ".tmp")
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(logs, f, ensure_ascii=False, indent=4, default=str)
            os.replace(tmp_file, log_file)
