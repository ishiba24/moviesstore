from django.contrib.auth.forms import UserCreationForm
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from django import forms
from movies.models import Region, UserProfile

class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))

class CustomUserCreationForm(UserCreationForm):
    region = forms.ModelChoiceField(
        queryset=Region.objects.all().order_by('name'),
        empty_label="Select your region",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update( {'class': 'form-control'} )
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Create user profile with selected region
            UserProfile.objects.create(user=user, region=self.cleaned_data['region'])
        return user
