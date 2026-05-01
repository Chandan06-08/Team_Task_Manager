from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Membership, Project, Task


class SignupForm(UserCreationForm):
    name = forms.CharField(max_length=150, label='Name')
    email = forms.EmailField(label='Email')

    class Meta:
        model = User
        fields = ['name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data.get('email')
        user.username = email
        user.email = email
        user.first_name = self.cleaned_data.get('name')
        if commit:
            user.save()
        return user


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assignee', 'status', 'priority', 'due_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        if project is not None:
            self.fields['assignee'].queryset = project.members.order_by('first_name', 'username')
        self.fields['assignee'].required = False


class TaskStatusForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['status']


class AddMemberForm(forms.Form):
    email = forms.EmailField(label='Member Email')
    role = forms.ChoiceField(choices=Membership.Role.choices, label='Role')


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Email', widget=forms.TextInput(attrs={'autofocus': True}))
