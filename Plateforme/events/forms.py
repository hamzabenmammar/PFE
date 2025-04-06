from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    """Form for creating and updating events."""
    
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'event_type', 'domains',
            'location', 'is_virtual', 'start_date', 'end_date',
            'submission_deadline', 'website', 'organizer',
            'contact_email', 'attachment'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'submission_deadline': forms.DateInput(attrs={'type': 'date'}),
        }


class EventSearchForm(forms.Form):
    """Form for searching events."""
    
    keyword = forms.CharField(required=False)
    event_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(Event.TYPE_CHOICES),
        required=False
    )
    domain = forms.ChoiceField(
        choices=[('', 'All Domains')] + list(Event.DOMAIN_CHOICES),
        required=False
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    include_past = forms.BooleanField(required=False, initial=False)
