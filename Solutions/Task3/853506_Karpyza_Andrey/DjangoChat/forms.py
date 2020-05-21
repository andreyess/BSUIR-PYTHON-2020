from django import forms
from .models import Comment
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.contrib.auth import (REDIRECT_FIELD_NAME, get_user_model, login as auth_login)

class EmailPostForm(forms.Form):
    to = forms.EmailField()
    comments = forms.CharField(required=False,
                               widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def clean_email(self):
        cd = self.cleaned_data
        emails = User.objects.filter(email=cd['email'])
        if len(emails) > 0:
            raise forms.ValidationError('Email was used previous!')
        return cd['email']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']


class LoginRequiredView(LoginView):

    def form_valid(self, form):
        user = form.get_user()
        if not user.profile.verified:
            return HttpResponseRedirect('/login/')
        else:
            auth_login(self.request, form.get_user())
            return HttpResponseRedirect(self.get_success_url())
