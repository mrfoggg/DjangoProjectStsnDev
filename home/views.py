# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm

def index(request):
    if request.method == 'POST' and not request.user.is_authenticated:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Перенаправление после успешного входа
    else:
        form = LoginForm()  # Пустая форма для отображения
    return render(request, 'index.html', {'form': form})
