from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Fieldset, Submit, Row, Column, HTML, Hidden    
from .models import Course, NLPTool, Corpus, Document, Article, Thesis, Memoir, ResourceBase
from accounts.models import Institution  # Nouvelle importation

class ResourceForm(forms.Form):
    RESOURCE_TYPES = [
        ('course', _('Course')),
        ('nlp_tool', _('NLP Tool')),
        ('corpus', _('Corpus')),
        ('document', _('Document')),
    ]

    DOCUMENT_TYPES = [
        ('article', _('Article')),
        ('thesis', _('Thesis')),
        ('memoir', _('Memoir')),
    ]

    # ==================== COMMON FIELDS ====================
    resource_type = forms.ChoiceField(
        choices=RESOURCE_TYPES,
        label=_("Resource Type *"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    title = forms.CharField(
        label=_("Title *"),
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        label=_("Description *"),
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    access_type = forms.ChoiceField(
        choices=ResourceBase.AccessType.choices,
        initial='public',
        label=_("Access Type *"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    # Supprimé: author (géré automatiquement)
    keywords = forms.CharField(
        label=_("Keywords"),
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text=_("Comma-separated")
    )
    access_link = forms.URLField(
        label=_("Access Link"),
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )

    # ==================== SPECIFIC FIELDS ====================
    # Course
    course_field = forms.CharField(
        label=_("Field of Study *"),
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    academic_level = forms.ChoiceField(
        choices=Course.Level.choices,
        label=_("Academic Level *"),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    # Modifié: Institution comme ModelChoiceField
    institution = forms.ModelChoiceField(
        queryset=Institution.objects.all(),
        label=_("Institution *"),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    academic_year = forms.CharField(
        label=_("Academic Year * (YYYY-YYYY)"),
        max_length=9,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text=_("Format: 2023-2024")
    )

    # NLP Tool
    tool_type = forms.ChoiceField(
        choices=NLPTool.ToolType.choices,
        label=_("Tool Type *"),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tool_version = forms.CharField(
        label=_("Version *"),
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    documentation = forms.URLField(
        label=_("Documentation"),
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )
    languages = forms.CharField(
        label=_("Supported Languages *"),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        initial='Arabic'
    )

    # Corpus
    corpus_language = forms.CharField(
        label=_("Primary Language *"),
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        initial='Arabic'
    )
    corpus_size = forms.IntegerField(
        label=_("Size * (words/documents)"),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    corpus_field = forms.CharField(
        label=_("Field of Study *"),
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    corpus_format = forms.CharField(
        label=_("Format * (TXT/CSV/JSON)"),
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # Document
    document_type = forms.ChoiceField(
        choices=DOCUMENT_TYPES,
        label=_("Document Type *"),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    document_format = forms.CharField(
        label=_("Format * (PDF/DOCX)"),
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # Article
    doi = forms.CharField(
        label=_("DOI"),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text=_("e.g., 10.1234/abcd")
    )
    journal = forms.CharField(
        label=_("Journal *"),
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    publication_date = forms.DateField(
        label=_("Publication Date *"),
        required=False,
        widget=forms.DateInput(
            attrs={'class': 'form-control', 'type': 'date'},
            format='%Y-%m-%d'
        )
    )

    # Thesis
    supervisor = forms.CharField(
        label=_("Supervisor *"),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    thesis_institution = forms.ModelChoiceField(
        queryset=Institution.objects.all(),
        label=_("Institution *"),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    defense_year = forms.IntegerField(
        label=_("Defense Year *"),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    # Memoir
    memoir_level = forms.ChoiceField(
        choices=Memoir._meta.get_field('academic_level').choices,
        label=_("Academic Level *"),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    memoir_institution = forms.ModelChoiceField(
        queryset=Institution.objects.all(),
        label=_("Institution *"),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    memoir_defense_year = forms.IntegerField(
        label=_("Defense Year *"),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Récupère l'utilisateur
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.attrs = {'novalidate': ''}
        
        # Modifié: Suppression du champ author du layout
        self.helper.layout = Layout(
            Fieldset(
                _('Basic Information'),
                Row(
                    Column('resource_type', css_class='col-md-6'),
                    Column('access_type', css_class='col-md-6')
                ),
                'title',
                'description',
                Row(
                    Column('keywords', css_class='col-md-12')  # Modifié
                ),
                'access_link',
                HTML("""<hr class="my-4">"""),
                # ... (le reste du layout reste inchangé)
            ),
            Submit('submit', _('Save'), css_class='btn-primary w-100 py-2 mt-3')
        )

    def clean(self):
        cleaned_data = super().clean()
        resource_type = cleaned_data.get('resource_type')
        
        # Validation modifiée pour les ModelChoiceFields
        if resource_type == 'course':
            required_fields = ['course_field', 'academic_level', 'institution', 'academic_year']
        elif resource_type == 'nlp_tool':
            required_fields = ['tool_type', 'tool_version']
        elif resource_type == 'corpus':
            required_fields = ['corpus_language', 'corpus_size', 'corpus_field', 'corpus_format']
        elif resource_type == 'document':
            required_fields = ['document_type', 'document_format']

        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, _("This field is required for this resource type"))

        return cleaned_data

    def save(self):
        resource_type = self.cleaned_data['resource_type']
        common_data = {
            'title': self.cleaned_data['title'],
            'description': self.cleaned_data['description'],
            'access_type': self.cleaned_data['access_type'],
            'author': self.user,  # Utilisateur connecté
            'keywords': self.cleaned_data['keywords'],
            'access_link': self.cleaned_data['access_link'] or None,
        }

        if resource_type == 'course':
            return Course.objects.create(
                **common_data,
                field=self.cleaned_data['course_field'],
                academic_level=self.cleaned_data['academic_level'],
                teacher=self.user,  # Enseignant = utilisateur
                institution=self.cleaned_data['institution'],
                academic_year=self.cleaned_data['academic_year']
            )
        elif resource_type == 'nlp_tool':
            return NLPTool.objects.create(
                **common_data,
                tool_type=self.cleaned_data['tool_type'],
                version=self.cleaned_data['tool_version'],
                documentation_link=self.cleaned_data['documentation'],
                languages=self.cleaned_data['languages']
            )
        elif resource_type == 'corpus':
            return Corpus.objects.create(
                **common_data,
                language=self.cleaned_data['corpus_language'],
                size=self.cleaned_data['corpus_size'],
                field=self.cleaned_data['corpus_field'],
                file_format=self.cleaned_data['corpus_format']
            )
        elif resource_type == 'document':
            doc = Document.objects.create(
                **common_data,
                document_type=self.cleaned_data['document_type'],
                file_format=self.cleaned_data['document_format']
            )
            
            if doc.document_type == 'article':
                Article.objects.create(
                    document=doc,
                    doi=self.cleaned_data['doi'],
                    journal=self.cleaned_data['journal'],
                    publication_date=self.cleaned_data['publication_date']
                )
            elif doc.document_type == 'thesis':
                Thesis.objects.create(
                    document=doc,
                    supervisor=self.cleaned_data['supervisor'],
                    institution=self.cleaned_data['thesis_institution'],
                    defense_year=self.cleaned_data['defense_year']
                )
            elif doc.document_type == 'memoir':
                Memoir.objects.create(
                    document=doc,
                    academic_level=self.cleaned_data['memoir_level'],
                    institution=self.cleaned_data['memoir_institution'],
                    defense_year=self.cleaned_data['memoir_defense_year']
                )
            return doc