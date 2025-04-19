from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

from accounts.managers import CustomUserManager;
from institutions.models import Institution






class CustomUser(AbstractUser):
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
  profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, default='profile_pics/default_profile_pic.png')
  objects = CustomUserManager() 

  
  USERNAME_FIELD = 'email'  
  REQUIRED_FIELDS = [] 

 

  def __str__(self):
    return self.email










