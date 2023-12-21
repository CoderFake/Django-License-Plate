from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth import logout
class CheckLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and request.path == reverse('main'):
            return HttpResponseRedirect(reverse('not_found'))
        return self.get_response(request)

class LogoutOnBrowserCloseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated and not request.COOKIES.get('sessionid') and not request.session.session_key:
            logout(request)
            return redirect('login')
        return response
