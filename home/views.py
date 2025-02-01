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
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Если форма валидна, можно выполнять логику логина (например, аутентификацию)
            # Здесь вы можете добавить логику для авторизации пользователя
            return HttpResponseRedirect(reverse('home'))  # Перенаправление на главную страницу
        else:
            # Если форма невалидна, она передается в шаблон с ошибками
            return render(request, 'index.html', {'form': form})
    else:
        # Если метод GET, просто показываем пустую форму
        form = LoginForm()
        return render(request, 'index.html', {'form': form})
