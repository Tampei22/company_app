from django.shortcuts import redirect
from django.conf import settings

EXEMPT_URLS = [
    "/conturi/login/",
    "/conturi/logout/",
    "/admin/",
    "/static/",
]

class RequireLoginMiddleware:
    """Запрещает доступ ко всем страницам без авторизации"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if not request.user.is_authenticated and not any(path.startswith(u) for u in EXEMPT_URLS):
            return redirect(settings.LOGIN_URL)
        return self.get_response(request)
