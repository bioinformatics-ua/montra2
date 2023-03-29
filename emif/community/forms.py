from django import forms
from .models import Community

class HeaderForm(forms.Form):
    display = forms.ChoiceField(choices = Community.HEADER_DISPLAY_TYPES, widget=forms.Select(attrs={
        'class': 'form-control'
    }))
