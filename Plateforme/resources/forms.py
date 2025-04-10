from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Fieldset, Submit, Row, Column, HTML , Hidden
from .models import Cours, OutilTAL, Corpus, Document, Article, These, Memoire

class ResourceForm(forms.Form):
    RESOURCE_TYPES = [
        ('cours', _('Cours')),
        ('outil', _('Outil TAL')),
        ('corpus', _('Corpus')),
        ('document', _('Document')),
    ]

    DOCUMENT_TYPES = [
        ('article', _('Article')),
        ('these', _('Thèse')),
        ('memoire', _('Mémoire')),
    ]

    # ==================== CHAMPS COMMUNS ====================
    resource_type = forms.ChoiceField(
        choices=RESOURCE_TYPES,
        label=_("Type de ressource *"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    titre = forms.CharField(
        label=_("Titre *"),
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        label=_("Description *"),
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    type_acces = forms.ChoiceField(
        choices=[
            ('public', _('Public')),
            ('privé', _('Privé')),
            ('restreint', _('Restreint'))
        ],
        initial='public',
        label=_("Type d'accès *"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    auteur = forms.CharField(
        label=_("Auteur *"),
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    mots_cles = forms.CharField(
        label=_("Mots-clés"),
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text=_("Séparés par des virgules")
    )
    lien_acces = forms.URLField(
        label=_("Lien externe"),
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )

    # ==================== CHAMPS SPÉCIFIQUES ====================
    # ----- Cours -----
    domaine_cours = forms.CharField(
        label=_("Domaine d'étude *"),
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    niveau_cours = forms.ChoiceField(
        choices=Cours.Niveau.choices,
        label=_("Niveau académique *"),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    enseignant_cours = forms.CharField(
        label=_("Enseignant *"),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    universite_cours = forms.CharField(
        label=_("Université *"),
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    annee_academique_cours = forms.CharField(
        label=_("Année académique * (AAAA-AAAA)"),
        max_length=9,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text=_("Format: 2023-2024")
    )

    # ----- Outil TAL -----
    type_outil = forms.ChoiceField(
        choices=OutilTAL.TypeOutil.choices,
        label=_("Type d'outil *"),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    version_outil = forms.CharField(
        label=_("Version *"),
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    documentation_outil = forms.URLField(
        label=_("Documentation"),
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )
    langues_outil = forms.CharField(
        label=_("Langues supportées *"),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        initial='arabe'
    )

    # ----- Corpus -----
    langue_corpus = forms.CharField(
        label=_("Langue principale *"),
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        initial='arabe'
    )
    taille_corpus = forms.IntegerField(
        label=_("Taille * (mots/documents)"),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    domaine_corpus = forms.CharField(
        label=_("Domaine *"),
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    format_corpus = forms.CharField(
        label=_("Format * (TXT/CSV/JSON)"),
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # ----- Document + Sous-types -----
    document_type = forms.ChoiceField(
        choices=DOCUMENT_TYPES,
        label=_("Type de document *"),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    format_document = forms.CharField(
        label=_("Format * (PDF/DOCX)"),
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # Article
    doi_article = forms.CharField(
        label=_("DOI"),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text=_("Ex: 10.1234/abcd")
    )
    revue_article = forms.CharField(
        label=_("Revue/Journal *"),
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    date_publication_article = forms.DateField(
        label=_("Date de publication *"),
        required=False,
        widget=forms.DateInput(
            attrs={'class': 'form-control', 'type': 'date'},
            format='%Y-%m-%d'
        )
    )

    # Thèse
    directeur_these = forms.CharField(
        label=_("Directeur de thèse *"),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    universite_these = forms.CharField(
        label=_("Université *"),
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    annee_soutenance_these = forms.IntegerField(
        label=_("Année de soutenance *"),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    # Mémoire
    niveau_memoire = forms.ChoiceField(
        choices=Memoire._meta.get_field('niveau').choices,
        label=_("Niveau académique *"),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    universite_memoire = forms.CharField(
        label=_("Université *"),
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    annee_soutenance_memoire = forms.IntegerField(
        label=_("Année de soutenance *"),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.attrs = {'novalidate': ''}
        
        self.helper.layout = Layout(
            Fieldset(
                _('Informations de base'),
                Row(
                    Column('resource_type', css_class='col-md-6'),
                    Column('type_acces', css_class='col-md-6')
                ),
                'titre',
                'description',
                Row(
                    Column('auteur', css_class='col-md-6'),
                    Column('mots_cles', css_class='col-md-6')
                ),
                'lien_acces',
                HTML("""<hr class="my-4">"""),
                
                
                # ===== Champs Spécifiques =====
                # Cours
                Div(
                    Fieldset(
                        _('Détails du Cours'),
                        Row(
                            Column('domaine_cours', css_class='col-md-6'),
                            Column('niveau_cours', css_class='col-md-6')
                        ),
                        Row(
                            Column('enseignant_cours', css_class='col-md-6'),
                            Column('universite_cours', css_class='col-md-6')
                        ),
                        'annee_academique_cours',
                    ),
                    css_class='specific-field',
                    id='cours-fields'
                ),
                
                # Outil TAL
                Div(
                    Fieldset(
                        _('Détails de l\'Outil TAL'),
                        Row(
                            Column('type_outil', css_class='col-md-6'),
                            Column('version_outil', css_class='col-md-6')
                        ),
                        'documentation_outil',
                        'langues_outil',
                    ),
                    css_class='specific-field',
                    id='outil-fields'
                ),
                
                # Corpus
                Div(
                    Fieldset(
                        _('Détails du Corpus'),
                        Row(
                            Column('langue_corpus', css_class='col-md-6'),
                            Column('taille_corpus', css_class='col-md-6')
                        ),
                        Row(
                            Column('domaine_corpus', css_class='col-md-6'),
                            Column('format_corpus', css_class='col-md-6')
                        ),
                    ),
                    css_class='specific-field',
                    id='corpus-fields'
                ),
                
                # Document (Parent)
                Div(
                    Fieldset(
                        _('Type de Document'),
                        Row(
                            Column('document_type', css_class='col-md-6'),
                            Column('format_document', css_class='col-md-6')
                        ),
                    ),
                    css_class='specific-field',
                    id='document-fields'
                ),
                
                # Article
                Div(
                    Fieldset(
                        _('Détails de l\'Article'),
                        'revue_article',
                        Row(
                            Column('date_publication_article', css_class='col-md-6'),
                            Column('doi_article', css_class='col-md-6')
                        ),
                    ),
                    css_class='specific-field',
                    id='article-fields'
                ),
                
                # Thèse
                Div(
                    Fieldset(
                        _('Détails de la Thèse'),
                        Row(
                            Column('directeur_these', css_class='col-md-6'),
                            Column('universite_these', css_class='col-md-6')
                        ),
                        'annee_soutenance_these',
                    ),
                    css_class='specific-field',
                    id='these-fields'
                ),
                
                # Mémoire
                Div(
                    Fieldset(
                        _('Détails du Mémoire'),
                        Row(
                            Column('niveau_memoire', css_class='col-md-6'),
                            Column('universite_memoire', css_class='col-md-6')
                        ),
                        'annee_soutenance_memoire',
                    ),
                    css_class='specific-field',
                    id='memoire-fields'
                ),
            ),
            Submit('submit', _('Enregistrer'), css_class='btn-primary w-100 py-2 mt-3')
        )

    def clean(self):
        cleaned_data = super().clean()
        resource_type = cleaned_data.get('resource_type')
        
        # Validation conditionnelle pour les champs requis
        if resource_type == 'cours':
            for field in ['domaine_cours', 'niveau_cours', 'enseignant_cours', 'universite_cours', 'annee_academique_cours']:
                if not cleaned_data.get(field):
                    self.add_error(field, _("Ce champ est obligatoire pour les cours"))
        
        # ... (validation similaire pour les autres types)

        return cleaned_data
    

    def save(self):
     resource_type = self.cleaned_data['resource_type']
     common_data = {
        'titre': self.cleaned_data['titre'],
        'description': self.cleaned_data['description'],
        'type_acces': self.cleaned_data['type_acces'],
        'auteur': self.cleaned_data['auteur'],
        'mots_cles': self.cleaned_data['mots_cles'],
        'lien_acces': self.cleaned_data['lien_acces'] or None,
    }

     if resource_type == 'cours':
        return Cours.objects.create(
            **common_data,
            domaine=self.cleaned_data['domaine_cours'],
            niveau=self.cleaned_data['niveau_cours'],
            enseignant=self.cleaned_data['enseignant_cours'],
            universite=self.cleaned_data['universite_cours'],
            annee_academique=self.cleaned_data['annee_academique_cours']
        )
     elif resource_type == 'corpus':
        return Corpus.objects.create(
            **common_data,
            langue=self.cleaned_data['langue_corpus'],
            taille=self.cleaned_data['taille_corpus'],
            domaine=self.cleaned_data['domaine_corpus'],
            format=self.cleaned_data['format_corpus']
        )
     elif resource_type == 'outil':
        return OutilTAL.objects.create(
            **common_data,
            type=self.cleaned_data['type_outil'],
            version=self.cleaned_data['version_outil'],
            documentation=self.cleaned_data['documentation_outil'],
            langues=self.cleaned_data['langues_outil']
        )
     elif resource_type == 'document':
        doc = Document.objects.create(
            **common_data,
            type=self.cleaned_data['document_type'],
            format=self.cleaned_data['format_document']
        )
        if doc.type == 'article':
            Article.objects.create(
                document=doc,
                doi=self.cleaned_data['doi_article'],
                revue=self.cleaned_data['revue_article'],
                date_publication=self.cleaned_data['date_publication_article']
            )
        elif doc.type == 'these':
            These.objects.create(
                document=doc,
                directeur=self.cleaned_data['directeur_these'],
                universite=self.cleaned_data['universite_these'],
                annee_soutenance=self.cleaned_data['annee_soutenance_these']
            )
        elif doc.type == 'memoire':
            Memoire.objects.create(
                document=doc,
                niveau=self.cleaned_data['niveau_memoire'],
                universite=self.cleaned_data['universite_memoire'],
                annee_soutenance=self.cleaned_data['annee_soutenance_memoire']
            )
        return doc
    # ... autres types
    