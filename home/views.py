from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from DjangoProjectStsnDev.forms import LoginForm  # Импорт вашей формы
import sys

def index(request):
    request.session['test_key'] = 'test_value'  # Запись в сессию
    request.session.modified = True  # Принудительное обновление сессии
    print("Session Key:", request.session.session_key)  # Вывести session_key в консоль
    sys.stdout.flush()  # Принудительный вывод в консоль
    return render(request, 'index.html', {'form': form})
