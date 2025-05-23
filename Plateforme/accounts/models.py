from datetime import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from accounts.managers import CustomUserManager
from institutions.models import Institution


from django.utils.crypto import get_random_string




class CustomUser(AbstractUser):
  STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('active', 'Actif'),
        ('blocked', 'Bloqué'),
    ]
  id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
  username = None
  email = models.EmailField(unique=True)
  full_name = models.CharField(max_length=255 , null=True , blank=True)
  institution = models.ForeignKey(Institution, on_delete=models.CASCADE , null=True , blank=True)
  bio = models.TextField(blank=True)
  status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Statut du compte"
    )
  avatar = models.ImageField(
        upload_to='avatars/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name="Photo de profil"
    )
  objects = CustomUserManager() 
  is_email_verified = models.BooleanField(default=False)
  email_verification_code = models.CharField(max_length=6, blank=True, null=True)

  def generate_verification_code(self):
        self.email_verification_code = get_random_string(length=6, allowed_chars='0123456789')
        self.save()

  
  USERNAME_FIELD = 'email'  
  REQUIRED_FIELDS = [] 

 

  def __str__(self):
    return self.email







