from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'your@email.com'}))
    role = forms.ChoiceField(
        choices=[('attendee', 'Attendee'), ('organizer', 'Event Organizer')],
        widget=forms.RadioSelect
    )
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Last name'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': '+1 (555) 000-0000'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'role', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        user.phone = self.cleaned_data.get('phone', '')
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username or Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

class ProfileUpdateForm(forms.ModelForm):
    avatar = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last name'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': '+1 (555) 000-0000'}))
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={'placeholder': 'Tell us a bit about yourself...', 'rows': 4}))
    twitter_link = forms.URLField(required=False, widget=forms.URLInput(attrs={'placeholder': 'https://twitter.com/yourusername'}))
    instagram_link = forms.URLField(required=False, widget=forms.URLInput(attrs={'placeholder': 'https://instagram.com/yourusername'}))
    website_link = forms.URLField(required=False, widget=forms.URLInput(attrs={'placeholder': 'https://yourwebsite.com'}))

    class Meta:
        model = CustomUser
        fields = ['avatar', 'first_name', 'last_name', 'phone', 'bio', 'twitter_link', 'instagram_link', 'website_link']
