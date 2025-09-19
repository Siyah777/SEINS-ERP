from django.contrib.auth.views import LoginView

class CustomAdminLoginView(LoginView):
    template_name = 'registration/login.html'
