
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Institution, Country, Specialty


class InstitutionFilterForm(forms.Form):
    INSTITUTION_TYPE_CHOICES = [('', _('All'))] + Institution.TYPE

    institution_type = forms.ChoiceField(
        choices=INSTITUTION_TYPE_CHOICES,
        required=False,
        label=_('Institution Type'),
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        required=False,
        empty_label=_('All'),
        label=_('Country'),
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
    specialty = forms.ModelChoiceField(
        queryset=Specialty.objects.all(),
        required=False,
        empty_label=_('All'),
        label=_('Specialty'),
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
    search_term = forms.CharField(
        required=False,
        label=_('Search Term'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter institution name or keyword...'),
            'type': 'search',
        })
    )

class InstitutionForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = [
            'name', 'acronym', 'type', 'country', 'city', 'specialties',
            'logo', 'website', 'email', 'phone', 'address', 'description'
        ]
        widgets = {
            'specialties': forms.CheckboxSelectMultiple(),
            'description': forms.Textarea(attrs={'rows': 5}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
