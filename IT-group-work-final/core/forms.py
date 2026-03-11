from django import forms
from .models import Document
from django.contrib.auth.forms import AuthenticationForm
from captcha.fields import CaptchaField
from .models import Document, UserProfile

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["title", "content", "visibility_status"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 12}),
            "visibility_status": forms.Select(attrs={"class": "form-select"}),
        }

class ShareForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username to share with"})
    )

class SuggestionForm(forms.Form):
    proposed_content = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 14}),
        label="Proposed content",
    )

class CommentForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Write a comment..."}),
        label="",
    )

class AttachmentForm(forms.Form):
    file = forms.FileField()

# Add a custom login form
class CustomLoginForm(AuthenticationForm):
    captcha = CaptchaField(label='The verification code', error_messages={'invalid': 'The verification code is incorrect. Please try again.'})

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['nickname', 'bio', 'avatar']
        widgets = {
            'nickname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your nickname'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['page_zoom', 'text_size', 'brightness', 'tts_enabled']
        widgets = {
            'page_zoom': forms.NumberInput(attrs={'type': 'range', 'class': 'form-range', 'min': '50', 'max': '150'}),
            'text_size': forms.NumberInput(attrs={'type': 'range', 'class': 'form-range', 'min': '12', 'max': '32'}),
            'brightness': forms.NumberInput(attrs={'class': 'form-control text-center', 'readonly': 'readonly'}),
            'tts_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }