from django.contrib import admin
from .models import Document, OutilTAL, Cours , Article, These, Memoire , Corpus
# Register your models here.
from django.contrib import admin
from .models import Document, Article, These, Memoire

class ArticleInline(admin.StackedInline):
    model = Article
    extra = 1  # Nombre de formulaires vides affichés

class TheseInline(admin.StackedInline):
    model = These
    extra = 1

class MemoireInline(admin.StackedInline):
    model = Memoire
    extra = 1

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("titre", "type", "auteur")
    inlines = []  # Par défaut, aucun inline

    def get_inlines(self, request, obj=None):
        """Affiche uniquement l'inline correspondant au type de document."""
        if obj and obj.type == Document.TypeDocument.ARTICLE:
            return [ArticleInline]
        elif obj and obj.type == Document.TypeDocument.THESE:
            return [TheseInline]
        elif obj and obj.type == Document.TypeDocument.MEMOIRE:
            return [MemoireInline]
        return []
    
admin.site.register(OutilTAL)
admin.site.register(Cours)
admin.site.register(Article)
admin.site.register(These)
admin.site.register(Memoire)
admin.site.register(Corpus)
