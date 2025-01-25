from django.http import HttpResponseRedirect
from django.utils import translation

class CustomLocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language_code = request.path.split('/')[1]
        print('language_code- ', language_code)
        if language_code == 'ua':
            new_url = request.path.replace('/ua/', '/uk/', 1)
            return HttpResponseRedirect(new_url)
        else:
            translation.activate(language_code)
        response = self.get_response(request)
        return response
