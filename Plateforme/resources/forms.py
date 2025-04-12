# forms.py
from django import forms
from django.forms import ModelForm, Select, Textarea
from .models import Document, Course, NLPTool, Article, Thesis, Memoir, Corpus

class ResourceForm(forms.Form):
    """
    A form for creating different types of resources.
    """
    RESOURCE_TYPES = [
        ('document', 'Document'),
        ('tool', 'NLP Tool'),
        ('course', 'Course'),
        ('article', 'Article'),
        ('thesis', 'Thesis'),
        ('memoir', 'Memoir'),
        ('corpus', 'Corpus')
    ]
    
    resource_type = forms.ChoiceField(
        choices=RESOURCE_TYPES,
        label="Resource Type",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Common fields for all resources
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
    )
    access_type = forms.ChoiceField(
        choices=[
            ('public', 'Public'),
            ('private', 'Private'),
            ('restricted', 'Restricted Access')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    keywords = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # NLP Tool specific fields
    tool_type = forms.ChoiceField(
        choices=NLPTool.ToolType.choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    version = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    documentation_link = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )
    languages = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Course specific fields
    field = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    academic_level = forms.ChoiceField(
        choices=Course.Level.choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    academic_year = forms.CharField(
        max_length=9,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2023-2024'})
    )
    
    # Document specific fields
    document_type = forms.ChoiceField(
        choices=Document.DocumentType.choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    file_format = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PDF, DOCX, etc.'})
    )
    
    # Corpus specific fields
    language = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Arabic'})
    )
    size = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    # Article specific fields
    doi = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    journal = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    publication_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    # Thesis/Memoir specific fields
    supervisor = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    defense_year = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        resource_type = cleaned_data.get('resource_type')
        
        # Validate required fields based on resource type
        if resource_type == 'tool':
            required_fields = ['tool_type', 'version']
        elif resource_type == 'course':
            required_fields = ['field', 'academic_level', 'academic_year']
        elif resource_type == 'document':
            required_fields = ['document_type', 'file_format']
        elif resource_type == 'corpus':
            required_fields = ['language', 'size', 'field', 'file_format']
        else:
            required_fields = []
            
        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, f'This field is required for {resource_type}.')
                
        return cleaned_data
        
    def save(self):
        """
        Create the appropriate resource based on the form data.
        """
        data = self.cleaned_data
        resource_type = data['resource_type']
        
        # Common attributes for all resources
        common_attrs = {
            'title': data['title'],
            'description': data['description'],
            'access_type': data['access_type'],
            'keywords': data['keywords'],
            'author': self.user,
        }
        
        if resource_type == 'tool':
            tool = NLPTool.objects.create(
                **common_attrs,
                tool_type=data['tool_type'],
                version=data['version'],
                documentation_link=data['documentation_link'],
                languages=data['languages'] or 'Arabic',
            )
            return tool
            
        elif resource_type == 'course':
            from accounts.models import Institution
            # Get the first institution (this should be improved in a real app)
            institution = Institution.objects.first()
            course = Course.objects.create(
                **common_attrs,
                field=data['field'],
                academic_level=data['academic_level'],
                academic_year=data['academic_year'],
                teacher=self.user,  # Assuming the author is the teacher
                institution=institution,
            )
            return course
            
        elif resource_type == 'corpus':
            corpus = Corpus.objects.create(
                **common_attrs,
                language=data['language'] or 'Arabic',
                size=data['size'],
                field=data['field'],
                file_format=data['file_format'],
            )
            return corpus
            
        elif resource_type == 'document':
            document = Document.objects.create(
                **common_attrs,
                document_type=data['document_type'],
                file_format=data['file_format'],
            )
            
            # Create corresponding specialized document
            if data['document_type'] == Document.DocumentType.ARTICLE and data.get('journal'):
                from accounts.models import Institution
                Article.objects.create(
                    document=document,
                    doi=data.get('doi', ''),
                    journal=data['journal'],
                    publication_date=data['publication_date'],
                )
            elif data['document_type'] == Document.DocumentType.THESIS and data.get('supervisor'):
                from accounts.models import Institution
                institution = Institution.objects.first()
                Thesis.objects.create(
                    document=document,
                    supervisor=data['supervisor'],
                    institution=institution,
                    defense_year=data['defense_year'],
                )
            elif data['document_type'] == Document.DocumentType.MEMOIR:
                from accounts.models import Institution
                institution = Institution.objects.first()
                Memoir.objects.create(
                    document=document,
                    academic_level=data.get('academic_level', 'master'),
                    institution=institution,
                    defense_year=data.get('defense_year', 2023),
                )
                
            return document