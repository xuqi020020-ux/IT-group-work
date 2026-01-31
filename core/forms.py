from django import forms
from .models import Document


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

