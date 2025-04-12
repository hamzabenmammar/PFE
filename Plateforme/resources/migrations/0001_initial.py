# Generated by Django 5.1.7 on 2025-04-12 10:20

import django.db.models.deletion
import resources.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Corpus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(help_text='Titre descriptif de la ressource', max_length=200, verbose_name='Titre')),
                ('description', models.TextField(help_text='Description détaillée de la ressource', verbose_name='Description')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('type_acces', models.CharField(choices=[('public', 'Public'), ('privé', 'Privé'), ('restreint', 'Accès restreint')], default='public', max_length=20, verbose_name="Type d'accès")),
                ('lien_acces', models.URLField(blank=True, null=True, verbose_name="Lien d'accès")),
                ('auteur', models.CharField(max_length=100, verbose_name='Auteur')),
                ('mots_cles', models.CharField(max_length=255, null=True, verbose_name='Mots-clés')),
                ('statut', models.CharField(choices=[('brouillon', 'Brouillon'), ('soumis', 'Soumis'), ('publié', 'Publié'), ('rejeté', 'Rejeté')], default='brouillon', max_length=20)),
                ('langue', models.CharField(default='arabe', help_text='Langue principale du corpus', max_length=50, verbose_name='Langue du corpus')),
                ('taille', models.IntegerField(help_text='Taille en nombre de mots ou de documents', verbose_name='Taille du corpus')),
                ('domaine', models.CharField(help_text='Domaine principal du corpus', max_length=50, verbose_name="Domaine d'étude")),
                ('format', models.CharField(help_text='Format du corpus (ex: TXT, CSV, JSON)', max_length=10, verbose_name='Format')),
            ],
            options={
                'ordering': ['-date_creation'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(help_text='Titre descriptif de la ressource', max_length=200, verbose_name='Titre')),
                ('description', models.TextField(help_text='Description détaillée de la ressource', verbose_name='Description')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('type_acces', models.CharField(choices=[('public', 'Public'), ('privé', 'Privé'), ('restreint', 'Accès restreint')], default='public', max_length=20, verbose_name="Type d'accès")),
                ('lien_acces', models.URLField(blank=True, null=True, verbose_name="Lien d'accès")),
                ('auteur', models.CharField(max_length=100, verbose_name='Auteur')),
                ('mots_cles', models.CharField(max_length=255, null=True, verbose_name='Mots-clés')),
                ('statut', models.CharField(choices=[('brouillon', 'Brouillon'), ('soumis', 'Soumis'), ('publié', 'Publié'), ('rejeté', 'Rejeté')], default='brouillon', max_length=20)),
                ('type', models.CharField(choices=[('article', 'Article'), ('thèse', 'Thèse'), ('mémoire', 'Mémoire')], max_length=20, verbose_name='Type de document')),
                ('format', models.CharField(help_text='PDF, DOCX, TXT, etc.', max_length=10, verbose_name='Format')),
            ],
            options={
                'verbose_name': 'Document',
                'verbose_name_plural': 'Documents',
            },
        ),
        migrations.CreateModel(
            name='OutilTAL',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(help_text='Titre descriptif de la ressource', max_length=200, verbose_name='Titre')),
                ('description', models.TextField(help_text='Description détaillée de la ressource', verbose_name='Description')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('type_acces', models.CharField(choices=[('public', 'Public'), ('privé', 'Privé'), ('restreint', 'Accès restreint')], default='public', max_length=20, verbose_name="Type d'accès")),
                ('lien_acces', models.URLField(blank=True, null=True, verbose_name="Lien d'accès")),
                ('auteur', models.CharField(max_length=100, verbose_name='Auteur')),
                ('mots_cles', models.CharField(max_length=255, null=True, verbose_name='Mots-clés')),
                ('statut', models.CharField(choices=[('brouillon', 'Brouillon'), ('soumis', 'Soumis'), ('publié', 'Publié'), ('rejeté', 'Rejeté')], default='brouillon', max_length=20)),
                ('type', models.CharField(choices=[('tokenization', 'Tokenisation'), ('stemming', 'Racinisation'), ('ner', "Reconnaissance d'entités"), ('pos_tagging', 'Étiquetage morphosyntaxique'), ('sentiment_analysis', 'Analyse de sentiments'), ('machine_translation', 'Traduction automatique')], help_text="Type de l'outil de TAL", max_length=50, verbose_name="Type d'outil")),
                ('version', models.CharField(help_text="Version de l'outil (ex: 1.0.0)", max_length=20, verbose_name='Version')),
                ('documentation', models.URLField(blank=True, help_text='URL de la documentation officielle', null=True, verbose_name='Lien vers la documentation')),
                ('dateMiseAJour', models.DateField(auto_now=True, verbose_name='Dernière mise à jour')),
                ('langues', models.CharField(default='arabe', help_text="Langues supportées par l'outil, séparées par des virgules", max_length=255, verbose_name='Langues supportées')),
            ],
            options={
                'verbose_name': 'Outil de TAL',
                'verbose_name_plural': 'Outils de TAL',
                'ordering': ['-date_creation'],
            },
        ),
        migrations.CreateModel(
            name='Cours',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(help_text='Titre descriptif de la ressource', max_length=200, verbose_name='Titre')),
                ('description', models.TextField(help_text='Description détaillée de la ressource', verbose_name='Description')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('type_acces', models.CharField(choices=[('public', 'Public'), ('privé', 'Privé'), ('restreint', 'Accès restreint')], default='public', max_length=20, verbose_name="Type d'accès")),
                ('lien_acces', models.URLField(blank=True, null=True, verbose_name="Lien d'accès")),
                ('auteur', models.CharField(max_length=100, verbose_name='Auteur')),
                ('mots_cles', models.CharField(max_length=255, null=True, verbose_name='Mots-clés')),
                ('statut', models.CharField(choices=[('brouillon', 'Brouillon'), ('soumis', 'Soumis'), ('publié', 'Publié'), ('rejeté', 'Rejeté')], default='brouillon', max_length=20)),
                ('domaine', models.CharField(help_text='Domaine principal du cours', max_length=50, verbose_name="Domaine d'étude")),
                ('niveau', models.CharField(choices=[('licence', 'Licence'), ('master', 'Master'), ('doctorat', 'Doctorat')], help_text="Niveau d'étude requis", max_length=20, verbose_name='Niveau académique')),
                ('enseignant', models.CharField(help_text="Nom complet de l'enseignant", max_length=100, verbose_name='Enseignant responsable')),
                ('universite', models.CharField(help_text='Université ou école dispensant le cours', max_length=200, verbose_name='Établissement')),
                ('annee_academique', models.CharField(help_text='Format : 2023-2024', max_length=9, validators=[resources.models.validate_annee_academique], verbose_name='Année académique')),
            ],
            options={
                'verbose_name': 'Cours',
                'verbose_name_plural': 'Cours',
                'ordering': ['-annee_academique', 'domaine'],
                'indexes': [models.Index(fields=['domaine', 'niveau'], name='resources_c_domaine_d76718_idx')],
            },
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doi', models.CharField(blank=True, help_text="Identifiant numérique d'article (ex: 10.1234/abcd)", max_length=100, verbose_name='DOI')),
                ('revue', models.CharField(max_length=200, verbose_name='Revue/Journal')),
                ('date_publication', models.DateField(verbose_name='Date de publication')),
                ('document', models.OneToOneField(limit_choices_to={'type': 'article'}, on_delete=django.db.models.deletion.CASCADE, related_name='article', to='resources.document')),
            ],
            options={
                'verbose_name': 'Article scientifique',
                'verbose_name_plural': 'Articles scientifiques',
            },
        ),
        migrations.CreateModel(
            name='Memoire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('niveau', models.CharField(choices=[('licence', 'Licence'), ('master', 'Master'), ('doctorat', 'Doctorat')], max_length=50, verbose_name='Niveau académique')),
                ('universite', models.CharField(max_length=200, verbose_name='Université')),
                ('annee_soutenance', models.IntegerField(verbose_name='Année de soutenance')),
                ('document', models.OneToOneField(limit_choices_to={'type': 'mémoire'}, on_delete=django.db.models.deletion.CASCADE, related_name='memoire', to='resources.document')),
            ],
            options={
                'verbose_name': 'Mémoire',
                'verbose_name_plural': 'Mémoires',
            },
        ),
        migrations.CreateModel(
            name='These',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('directeur', models.CharField(max_length=100, verbose_name='Directeur de thèse')),
                ('universite', models.CharField(max_length=200, verbose_name='Université')),
                ('annee_soutenance', models.IntegerField(verbose_name='Année de soutenance')),
                ('document', models.OneToOneField(limit_choices_to={'type': 'thèse'}, on_delete=django.db.models.deletion.CASCADE, related_name='these', to='resources.document')),
            ],
            options={
                'verbose_name': 'Thèse',
                'verbose_name_plural': 'Thèses',
            },
        ),
    ]
