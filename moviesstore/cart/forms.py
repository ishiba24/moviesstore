# cart/forms.py
from django import forms
from .models import CheckoutFeedback

class CheckoutFeedbackForm(forms.ModelForm):
    class Meta:
        model = CheckoutFeedback
        fields = ['name', 'feedback_text']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name (optional - leave blank to remain anonymous)'
            }),
            'feedback_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'How was your checkout experience? Your feedback helps us improve GT Movie Store!',
                'required': True
            }),
        }
        labels = {
            'name': 'Your Name (Optional)',
            'feedback_text': 'Your Checkout Experience'
        }