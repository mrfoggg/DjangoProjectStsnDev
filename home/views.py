from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import LoginForm  # Импорт вашей формы

def index(request):
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
