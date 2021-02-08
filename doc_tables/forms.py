from django import forms
from .models import *
from ckeditor.fields import RichTextField
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class TablesForm(forms.ModelForm):
    class Meta:
        model = Tables
        fields = ('user', 'file',)

class DataForm(forms.ModelForm):
    class Meta:
        model = Data
        fields = ('json_data',)

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name','email', 'last_name', 'password1',)

class UpdateUser(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

class UpdateFormProfile(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user']

class AddTestForm(forms.ModelForm):
    content_1 = forms.CharField(label='Описание',
                   widget=forms.Textarea(attrs={'class': 'ckeditor'}))
    class Meta:
        model = Test
        fields = ('content_1',)