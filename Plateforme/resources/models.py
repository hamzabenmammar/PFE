from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.core.exceptions import PermissionDenied  



# Create your models here.


class RessourceBase(models.Model):
    """
    Base model for all resources.
    """
    
    class TypeAcces(models.TextChoices):
        PUBLIC = 'public', _('Public')
        PRIVE = 'privé', _('Privé')
        RESTREINT = 'restreint', _('Accès restreint')

    titre = models.CharField(
        max_length=200,
        verbose_name=_("Titre"),
        help_text=_("Titre descriptif de la ressource")
    )
    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("Description détaillée de la ressource")
    )
    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date de création")
    )
    type_acces = models.CharField(
        max_length=20,
        choices=TypeAcces.choices,
        default=TypeAcces.PUBLIC,
        verbose_name=_("Type d'accès")
    )

    lien_acces = models.URLField(
        verbose_name=_("Lien d'accès"),
        blank=True,
        null=True
    )
    auteur = models.CharField(
        max_length=100,
        verbose_name=_("Auteur"),
    )
    mots_cles = models.CharField(
        max_length=255,
        null=True,
        verbose_name=_("Mots-clés"),
    )
    STATUT_CHOICES = [
        ('brouillon', _('Brouillon')),
        ('soumis', _('Soumis')),
        ('publié', _('Publié')),
        ('rejeté', _('Rejeté'))
    ]
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='brouillon'
    )
   
   
    class Meta:
        abstract = True
        ordering = ['-date_creation'] 

    def __str__(self):
        return self.titre
    
     # Méthodes de l'UML à implémenter
    def modifier(self, **kwargs):
        """Permet de modifier les champs de la ressource."""
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save()

    def supprimer(self):
        """Supprime la ressource."""
        self.delete()

    @classmethod
    def get_resource_class(cls, resource_type):
        """Mappe les types de ressources aux classes concrètes"""
        TYPE_MAP = {
            'document': Document,
            'outil': OutilTAL,
            'cours': Cours,
            'article': Article,
            'these': These,
            'memoire': Memoire,
            'corpus': Corpus
        }
        return TYPE_MAP.get(resource_type.lower())    

def validate_annee_academique(value):
    """
    Valide le format AAAA-AAAA pour l'année académique
    """
    import re
    if not re.match(r'^\d{4}-\d{4}$', value):
        raise ValidationError(
            _("Format d'année académique invalide. Utilisez le format : 2023-2024")
        )
    annee_debut, annee_fin = map(int, value.split('-'))
    if annee_fin != annee_debut + 1:
        raise ValidationError(
            _("L'année de fin doit être l'année de début + 1")
        )   

class Cours(RessourceBase):
    """
    Modèle héritant de RessourceBase pour représenter un cours académique.
    Correspond exactement aux spécifications UML fournies.
    """
    
    class Niveau(models.TextChoices):
        LICENCE = 'licence', _('Licence')
        MASTER = 'master', _('Master')
        DOCTORAT = 'doctorat', _('Doctorat')

    domaine = models.CharField(
        max_length=50,
        verbose_name=_("Domaine d'étude"),
        help_text=_("Domaine principal du cours")
    )

    niveau = models.CharField(
        max_length=20,
        choices=Niveau.choices,
        verbose_name=_("Niveau académique"),
        help_text=_("Niveau d'étude requis")
    )

    enseignant = models.CharField(
        max_length=100,
        verbose_name=_("Enseignant responsable"),
        help_text=_("Nom complet de l'enseignant")
    )

    universite = models.CharField(
        max_length=200,
        verbose_name=_("Établissement"),
        help_text=_("Université ou école dispensant le cours")
    )

    annee_academique = models.CharField(
        max_length=9,
        verbose_name=_("Année académique"),
        help_text=_("Format : 2023-2024"),
        validators=[validate_annee_academique]
    )

    
   
  
    class Meta:
        verbose_name = _("Cours")
        verbose_name_plural = _("Cours")
        ordering = ['-annee_academique', 'domaine']
        indexes = [
            models.Index(fields=['domaine', 'niveau']),
        ]

    def __str__(self):
        return f"{self.titre} ({self.get_niveau_display()}) - {self.enseignant}"

    def publier(self):
        """Méthode pour publier le cours"""
        self.est_public = True
        self.save()
        return self

    def acceder(self):
        """Méthode pour vérifier l'accès"""
        if not self.est_public:
            raise PermissionDenied(_("Ce cours nécessite une authentification"))
        return self
    

class Document(RessourceBase):

    class TypeDocument(models.TextChoices):
        ARTICLE = 'article', _('Article')
        THESE = 'thèse', _('Thèse')
        MEMOIRE = 'mémoire', _('Mémoire')

    type = models.CharField(
        max_length=20,
        choices=TypeDocument.choices,
        verbose_name=_("Type de document")
    )    
    format = models.CharField(
        max_length=10,
        verbose_name=_("Format"),
        help_text=_("PDF, DOCX, TXT, etc.")
    )
   
 
    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"

    def get_citation(self):
        """Génère une citation standardisée selon le type."""
        if hasattr(self, 'article'):
            return self.article.get_citation()
        elif hasattr(self, 'these'):
            return self.these.get_citation()
        elif hasattr(self, 'memoire'):
            return self.memoire.get_citation()
        return f"{self.titre} ({self.auteur}, {self.date_creation.year})"
    

class These(models.Model):

    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        related_name='these',
        limit_choices_to={'type': Document.TypeDocument.THESE}
    )
    directeur = models.CharField(
        max_length=100,
        verbose_name=_("Directeur de thèse"),
    )
    universite = models.CharField(
        max_length=200,
        verbose_name=_("Université"),
    )
    annee_soutenance = models.IntegerField(
        verbose_name=_("Année de soutenance"),
    )

    def get_citation(self):
        return f"{self.document.auteur} ({self.annee_soutenance}). {self.document.titre}. Thèse de doctorat, {self.universite}."

    class Meta:
        verbose_name = _("Thèse")
        verbose_name_plural = _("Thèses")
    

class Memoire(models.Model):
    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        related_name='memoire',
        limit_choices_to={'type': Document.TypeDocument.MEMOIRE}
    )

    niveau = models.CharField(
        max_length=50,
        choices=[
            ('licence', _('Licence')),
            ('master', _('Master')),
            ('doctorat', _('Doctorat'))
        ],
        verbose_name=_("Niveau académique"),
    )
    universite = models.CharField(
        max_length=200,
        verbose_name=_("Université"),
    )
    annee_soutenance = models.IntegerField(
        verbose_name=_("Année de soutenance"),
    )

    def get_citation(self):
        niveau_display = dict(self._meta.get_field('niveau').choices).get(self.niveau)
        return f"{self.document.auteur} ({self.annee_soutenance}). {self.document.titre}. Mémoire de {niveau_display}, {self.universite}."

    class Meta:
        verbose_name = _("Mémoire")
        verbose_name_plural = _("Mémoires")


class Article(models.Model):
    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        related_name='article',
        limit_choices_to={'type': Document.TypeDocument.ARTICLE}
    )
    doi = models.CharField(
        max_length=100,
        verbose_name=_("DOI"),
        blank=True,
        help_text=_("Identifiant numérique d'article (ex: 10.1234/abcd)")
    )
    revue = models.CharField(
        max_length=200,
        verbose_name=_("Revue/Journal"),
    )
    date_publication = models.DateField(
        verbose_name=_("Date de publication")
    )

    def get_citation(self):
        return f"{self.document.auteur} ({self.date_publication.year}). {self.document.titre}. {self.revue}. DOI: {self.doi}"

    class Meta:
        verbose_name = _("Article scientifique")
        verbose_name_plural = _("Articles scientifiques")


class OutilTAL(RessourceBase):



    class TypeOutil(models.TextChoices):
        TOKENIZATION = 'tokenization', _('Tokenisation')
        STEMMING = 'stemming', _('Racinisation')
        NER = 'ner', _('Reconnaissance d\'entités')
        POS_TAGGING = 'pos_tagging', _('Étiquetage morphosyntaxique')
        SENTIMENT_ANALYSIS = 'sentiment_analysis', _('Analyse de sentiments')
        MACHINE_TRANSLATION = 'machine_translation', _('Traduction automatique')

    type = models.CharField(
        max_length=50,
        choices=TypeOutil.choices,
        verbose_name=_("Type d'outil"),
        help_text=_("Type de l'outil de TAL")
    )
    version = models.CharField(
        max_length=20,
        verbose_name=_("Version"),
        help_text=_("Version de l'outil (ex: 1.0.0)")
    )
    documentation = models.URLField(
        verbose_name=_("Lien vers la documentation"),
        blank=True,
        null=True,
        help_text=_("URL de la documentation officielle")
    )
    dateMiseAJour = models.DateField(
        auto_now=True,
        verbose_name=_("Dernière mise à jour")
    )
    langues = models.CharField(
        max_length=255,
        verbose_name=_("Langues supportées"),
        help_text=_("Langues supportées par l'outil, séparées par des virgules"),
        default='arabe',
    )

    class Meta:
        verbose_name = _("Outil de TAL")
        verbose_name_plural = _("Outils de TAL")
        ordering = ['-date_creation']

    def clean(self):
        """Validation spécifique aux outils TAL"""
        if self.type == self.TypeOutil.MACHINE_TRANSLATION and not self.langues:
            raise ValidationError(
                _("Un outil de traduction doit spécifier les langues supportées.")
            )

    def __str__(self):
        return f"{self.titre} ({self.get_type_display()})"
    

class Corpus(RessourceBase):
    """
    Modèle pour représenter un corpus de données textuelles.
    """
    langue = models.CharField(
        max_length=50,
        verbose_name=_("Langue du corpus"),
        help_text=_("Langue principale du corpus"),
        default='arabe'
    )
    taille = models.IntegerField(
        verbose_name=_("Taille du corpus"),
        help_text=_("Taille en nombre de mots ou de documents")
    )
    domaine = models.CharField(
        max_length=50,
        verbose_name=_("Domaine d'étude"),
        help_text=_("Domaine principal du corpus")
    )
    format = models.CharField(
        max_length=10,
        verbose_name=_("Format"),
        help_text=_("Format du corpus (ex: TXT, CSV, JSON)")
    )