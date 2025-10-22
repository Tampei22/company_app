from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    """
    Middleware: требует авторизацию для всех страниц,
    кроме логина, выхода и админки.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Пути, доступные без входа
        allowed_urls = [
            reverse('login'),
            reverse('logout'),
            '/admin/',
            '/static/',  # важно для загрузки стилей
        ]

        # Если пользователь не авторизован и страница не разрешена
        if not request.user.is_authenticated:
            path = request.path
            if not any(path.startswith(url) for url in allowed_urls):
                return redirect('login')

        # Если пользователь уже авторизован и заходит на страницу логина → перебросить на главную
        if request.user.is_authenticated and request.path == reverse('login'):
            return redirect('/')

        return self.get_response(request)
