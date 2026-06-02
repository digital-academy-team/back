from rest_framework_simplejwt.tokens import AccessToken

def get_payload(request):
    auth = getattr(request, "auth", None)
    if isinstance(auth, AccessToken):
        return auth.payload
    if isinstance(auth, dict):
        return auth
    return {}
