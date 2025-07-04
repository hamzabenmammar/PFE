# Generated by Django 5.1.7 on 2025-05-28 13:23

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('SYSTEM', 'Système'), ('PROJECT_INVITATION', 'Invitation à un projet'), ('MEMBERSHIP_REQUEST', "Demande d'adhésion"), ('PROJECT_UPDATE', 'Mise à jour de projet'), ('TASK_ASSIGNED', 'Tâche assignée'), ('COMMENT', 'Commentaire'), ('EVENT_CREATED', 'Événement créé'), ('EVENT_APPROVED', 'Événement approuvé')], default='SYSTEM', max_length=50)),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('read', models.BooleanField(default=False)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('object_id', models.UUIDField(blank=True, null=True)),
                ('project_id', models.UUIDField(blank=True, null=True)),
                ('sender_id', models.UUIDField(blank=True, null=True)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
