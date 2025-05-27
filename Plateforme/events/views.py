from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from notifications.services import NotificationService
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
import logging

from .models import Event, EventRegistration
from .forms import EventForm, EventSearchForm

logger = logging.getLogger(__name__)


class EventListView(ListView):
    """View for listing events."""
    
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 10
    
    def get_queryset(self):
        """Filter events based on user permissions."""
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_approved=True)
        form = EventSearchForm(self.request.GET)
        
        if form.is_valid():
            keyword = form.cleaned_data.get('keyword')
            event_type = form.cleaned_data.get('event_type')
            domain = form.cleaned_data.get('domain')
            start_date = form.cleaned_data.get('start_date')
            include_past = form.cleaned_data.get('include_past')
            
            if keyword:
                queryset = queryset.filter(
                    Q(title__icontains=keyword) | 
                    Q(description__icontains=keyword) |
                    Q(organizer__name__icontains=keyword)
                )
            
            if event_type:
                queryset = queryset.filter(event_type=event_type)
            
            if domain:
                queryset = queryset.filter(domains__icontains=domain)
            
            if start_date:
                queryset = queryset.filter(start_date__gte=start_date)
            
            if not include_past:
                queryset = queryset.filter(submission_deadline__gte=timezone.now().date())
        else:
            # By default, only show upcoming and ongoing events
            queryset = queryset.filter(submission_deadline__gte=timezone.now().date())
        
        return queryset.select_related('organizer', 'created_by')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = EventSearchForm(self.request.GET or None)
        return context


class EventDetailView(DetailView):
    """View for displaying event details (visible to all users)."""
    
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        """Add related objects and filter based on user permissions."""
        queryset = Event.objects.select_related('organizer', 'created_by')
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_approved=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if the user is registered for this event
        if self.request.user.is_authenticated:
            context['is_registered'] = EventRegistration.objects.filter(
                event=self.object,
                user=self.request.user
            ).exists()
        else:
            context['is_registered'] = False
            
        # Add registration count
        context['registration_count'] = self.object.registrations.count()
        return context


class EventCreateView(LoginRequiredMixin, CreateView):
    """View for creating new events."""
    
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    
    def form_valid(self, form):
        # Auto-approve events created by staff
        form.instance.is_approved = self.request.user.is_staff
        form.instance.created_by = self.request.user
        self.object = form.save()
        
        if self.object.is_approved:
            messages.success(self.request, _('Event created successfully!'))
            # Notifier tous les utilisateurs actifs
            User = get_user_model()
            active_users = User.objects.filter(is_active=True)
            NotificationService.notify_group(
                active_users,
                'EVENT_APPROVED',
                f"Nouvel événement approuvé : {self.object.title}",
                f"Un nouvel événement a été approuvé : {self.object.title}. Date : {self.object.start_date}",
                self.object
            )
            return redirect(self.object.get_absolute_url())
        else:
            messages.success(
                self.request, 
                _('Event created successfully! It will be visible after admin approval.')
            )
            # Notifier le créateur de l'événement
            NotificationService.create_notification(
                recipient=self.request.user,
                notification_type='EVENT_CREATED',
                title="Votre événement est en attente d'approbation",
                message=f"Votre événement '{self.object.title}' a été créé et est en attente d'approbation par un administrateur.",
                related_object=self.object
            )
            return redirect('events:event_list')


class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating events."""
    
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    
    def test_func(self):
        """Check if user has permission to edit this event."""
        event = self.get_object()
        return self.request.user == event.created_by or self.request.user.is_staff
    
    def form_valid(self, form):
        # If a non-staff user edits an approved event, require re-approval
        if not self.request.user.is_staff and self.get_object().is_approved:
            form.instance.is_approved = False
            messages.info(
                self.request,
                _('Your changes will be reviewed before becoming visible.')
            )
        else:
            messages.success(self.request, _('Event updated successfully!'))
            
        return super().form_valid(form)


class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting events."""
    
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('events:event_list')
    
    def test_func(self):
        """Check if user has permission to delete this event."""
        event = self.get_object()
        return self.request.user == event.created_by or self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        event_title = self.get_object().title
        messages.success(request, _('Event "{}" deleted successfully.').format(event_title))
        return super().delete(request, *args, **kwargs)


def register_for_event(request, pk):
    """View for registering to an event."""
    
    if not request.user.is_authenticated:
        messages.error(request, _('You must be logged in to register for events.'))
        return redirect('account_login')
    
    event = get_object_or_404(Event, pk=pk, is_approved=True)
    
    # Don't allow registration for past events
    if event.is_past:
        messages.error(request, _('Registration for past events is not allowed.'))
        return redirect('events:event_detail', pk=pk)
    
    # Check if user is already registered
    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        messages.info(request, _('You are already registered for this event.'))
    else:
        EventRegistration.objects.create(event=event, user=request.user)
        messages.success(request, _('You have successfully registered for "{}".').format(event.title))
    
    return redirect('events:event_detail', pk=pk)


def unregister_from_event(request, pk):
    """View for unregistering from an event."""
    
    if not request.user.is_authenticated:
        return redirect('account_login')
    
    event = get_object_or_404(Event, pk=pk)
    
    # Don't allow unregistration from past events
    if event.is_past:
        messages.error(request, _('Unregistering from past events is not allowed.'))
        return redirect('events:event_detail', pk=pk)
    
    registration = get_object_or_404(EventRegistration, event=event, user=request.user)
    registration.delete()
    
    messages.success(request, _('You have unregistered from "{}".').format(event.title))
    
    return redirect('events:event_detail', pk=pk)


# Helper function to check if a user is staff
def is_staff_check(user):
    return user.is_staff


# Vue pour valider un événement
@user_passes_test(lambda u: u.is_staff)
def event_validate(request, pk):
    """Vue pour approuver un événement"""
    event = get_object_or_404(Event, pk=pk)
    event.is_approved = True
    event.save()
    
    # Notifier le créateur de l'événement
    NotificationService.create_notification(
        recipient=event.created_by,
        notification_type='EVENT_APPROVED',
        title="Votre événement a été approuvé",
        message=f"Votre événement '{event.title}' a été approuvé et est maintenant visible par tous les utilisateurs.",
        related_object=event
    )
    
    # Notifier tous les utilisateurs actifs
    User = get_user_model()
    active_users = User.objects.filter(is_active=True)
    NotificationService.notify_group(
        active_users,
        'EVENT_APPROVED',
        f"Nouvel événement approuvé : {event.title}",
        f"Un nouvel événement a été approuvé : {event.title}. Date : {event.start_date}",
        event
    )
    
    messages.success(request, _('Event has been approved successfully!'))
    return redirect('pages:admin_calls')
