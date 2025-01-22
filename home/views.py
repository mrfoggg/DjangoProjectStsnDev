from django.http import HttpResponse

def home(request):
    print('HOME log')
    return HttpResponse("Hello, world. You're at the polls index.")