from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.views import View
from .forms import LoginForm


class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            # Already logged in — send editors to dashboard, viewers to site
            if request.user.is_editor_user():
                return redirect('dashboard:index')
            return redirect('/')
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Honour explicit ?next= param; otherwise redirect by role
            next_url = request.GET.get('next')
            if not next_url:
                next_url = '/dashboard/' if user.is_editor_user() else '/'
            return redirect(next_url)
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('accounts:login')
