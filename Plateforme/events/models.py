from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse
import uuid
from accounts.models import Institution


class Event(models.Model):
    """Model for scientific events related to Arabic NLP research."""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    TYPE_CHOICES = (
        ('conference', _('Conference')),
        ('workshop', _('Workshop')),
        ('seminar', _('Seminar')),
        ('call_for_papers', _('Call for Papers')),
        ('hackathon', _('Hackathon')),
        ('other', _('Other')),
    )
    
    DOMAIN_CHOICES = (
        ('nlp', _('Natural Language Processing')),
        ('speech', _('Speech Processing')),
        ('ai', _('Artificial Intelligence')),
        ('arabic_lang', _('Arabic Language')),
        ('linguistics', _('Linguistics')),
        ('other', _('Other')),
    )
    
    title = models.CharField(_('Title'), max_length=255)
    description = models.TextField(_('Description'))
    event_type = models.CharField(_('Event Type'), max_length=20, choices=TYPE_CHOICES)
    domains = models.CharField(_('Domains'), max_length=255, help_text=_('Comma-separated domains'))
    location = models.CharField(_('Location'), max_length=255, blank=True)
    is_virtual = models.BooleanField(_('Virtual Event'), default=False)
    start_date = models.DateField(_('Start Date'))
    end_date = models.DateField(_('End Date'))
    submission_deadline = models.DateField(_('Submission Deadline'), null=True, blank=True)
    website = models.URLField(_('Website'), blank=True)
    organizer = models.ForeignKey(Institution, on_delete=models.CASCADE, verbose_name=_('Organizer'))
    contact_email = models.EmailField(_('Contact Email'))
    
    # File attachments for call for papers, etc.
    attachment = models.FileField(_('Attachment'), upload_to='events/attachments/', blank=True, null=True)
    
    # Metadata
    created_by = models.ForeignKey(get_user_model(), related_name='created_events', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = _('Event')
        verbose_name_plural = _('Events')
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('events:event_detail', kwargs={'pk': self.pk})
    
    @property
    def is_upcoming(self):
        return self.start_date >= timezone.now().date()
    
    @property
    def is_ongoing(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date
    
    @property
    def days_until_deadline(self):
        if not self.submission_deadline:
            return None
        
        delta = self.submission_deadline - timezone.now().date()
        return delta.days if delta.days >= 0 else None
    
    @property
    def domain_list(self):
        return [domain.strip() for domain in self.domains.split(',')]


class EventRegistration(models.Model):
    """Model to track users who registered for events."""
    
    event = models.ForeignKey(Event, related_name='registrations', on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), related_name='event_registrations', on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('event', 'user')
        verbose_name = _('Event Registration')
        verbose_name_plural = _('Event Registrations')
    
    def __str__(self):
        return f"{self.user.username} - {self.event.title}"
