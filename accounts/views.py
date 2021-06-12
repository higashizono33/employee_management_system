from .forms import CustomUserCreateForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from app.models import Employee

User = get_user_model()

class SignUpView(SuccessMessageMixin, CreateView):
    form_class = CustomUserCreateForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
    success_message = 'You are successfully registered. Please Login.'

    def form_valid(self, form):
        new_employee = form.save()
        Employee.objects.create(user=new_employee)
        return super().form_valid(form)

