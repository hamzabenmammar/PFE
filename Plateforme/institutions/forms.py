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

    # Définir explicitement les champs pour avoir plus de contrôle
    name = forms.CharField(label=_('Nom de l\'institution'), widget=forms.TextInput(attrs={'class': 'form-control', 'required': True}))
    acronym = forms.CharField(label=_('Sigle'), required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    type = forms.ChoiceField(label=_('Type d\'institution'), choices=Institution.TYPE, widget=forms.Select(attrs={'class': 'form-control', 'required': True}))
    country = forms.ModelChoiceField(label=_('Pays'), queryset=Country.objects.all(), widget=forms.Select(attrs={'class': 'form-control', 'required': True}))
    city = forms.CharField(label=_('Ville'), widget=forms.TextInput(attrs={'class': 'form-control', 'required': True}))
    specialties = forms.ModelMultipleChoiceField(
        queryset=Specialty.objects.all(),
        required=False,  # Rendre le champ facultatif
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label=_('Spécialités')
    )
    logo = forms.ImageField(label=_('Logo'), required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    website = forms.URLField(label=_('Site web'), required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label=_('Email'), required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(label=_('Téléphone'), required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(label=_('Adresse'), required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    description = forms.CharField(label=_('Description'), required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))


    class Meta:
        model = Institution
        fields = [
            'name', 'acronym', 'type', 'country', 'city', 'specialties',
            'logo', 'website', 'email', 'phone', 'address', 'description'
        ]
        # Les widgets et required sont définis explicitement ci-dessus
        widgets = {}
        # exclude = ['created_by'] # Peut être nécessaire si created_by n'est pas dans fields

    def clean(self):
        cleaned_data = super().clean()
        website = cleaned_data.get('website')
        email = cleaned_data.get('email')
        phone = cleaned_data.get('phone')

        if not any([website, email, phone]):
            raise forms.ValidationError(
                _("Veuillez fournir au moins un moyen de contact (site web, email ou téléphone).")
            )

        return cleaned_data
