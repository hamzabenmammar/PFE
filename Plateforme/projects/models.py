from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from accounts.models import Institution
import uuid
class Project(models.Model):
  id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
  title = models.CharField(max_length=255)
  institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
  coordinator = models.ForeignKey(
    get_user_model(), 
    on_delete=models.CASCADE,
    related_name='coordinated_projects'
  )
  description = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  date_start = models.DateField(blank=True, null=True)
  date_end = models.DateField(blank=True, null=True)
  def __str__(self):
    return self.title
  def get_absolute_url(self):
    return reverse('projects:project_detail', kwargs={'pk': self.pk})


class ProjectMember(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE , related_name='memberships')
    member = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='projects'
    )
    role = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('project', 'member')
    def __str__(self):
        return f"{self.member.username} - {self.project.title}"
    def get_absolute_url(self):
        return reverse('projects:project_detail', kwargs={'pk': self.project.pk})









