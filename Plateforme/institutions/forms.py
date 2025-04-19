
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Institution, Country, Specialty

# Use ChoiceField for Institution.TYPE instead of nonexistent InstitutionType model
class InstitutionFilterForm(forms.Form):
    INSTITUTION_TYPE_CHOICES = [('', _('All'))] + Institution.TYPE

    institution_type = forms.ChoiceField(
        choices=INSTITUTION_TYPE_CHOICES,
        required=False,
        label=_('Institution Type')
    )
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        required=False,
        empty_label=_('All'),
        label=_('Country')
    )
    specialty = forms.ModelChoiceField(
        queryset=Specialty.objects.all(),
        required=False,
        empty_label=_('All'),
        label=_('Specialty')
    )
    search_term = forms.CharField(
        required=False,
        label=_('Search Term'),
        widget=forms.TextInput(attrs={
            'placeholder': _('Enter institution name or keyword...')
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
