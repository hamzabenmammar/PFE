from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

from .models import Event, EventRegistration
from .forms import EventForm, EventSearchForm

class EventListView(ListView):
    """View for listing events."""
    
    model = Event
    template_name = 'event_list.html'
    context_object_name = 'events'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Event.objects.all()
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
                    Q(organizer__icontains=keyword)
                )
            
            if event_type:
                queryset = queryset.filter(event_type=event_type)
            
            if domain:
                queryset = queryset.filter(domains__icontains=domain)
            
            if start_date:
                queryset = queryset.filter(start_date__gte=start_date)
            
            if not include_past:
                queryset = queryset.filter(end_date__gte=timezone.now().date())
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = EventSearchForm(self.request.GET or None)
        return context


class EventDetailView(DetailView):
    """View for displaying event details."""
    
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'
    
    def get_queryset(self):
        # Only show approved events to regular users
        if self.request.user.is_staff:
            return Event.objects.all()
      
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_registered'] = EventRegistration.objects.filter(
                event=self.object, 
                user=self.request.user
            ).exists()
        return context


class EventCreateView(LoginRequiredMixin, CreateView):
    """View for creating new events."""
    
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
      
        
        messages.success(
            self.request, 
            'Event created successfully! It will be visible after admin approval.' 
            if not self.request.user.is_staff else 'Event created successfully!'
        )
        return super().form_valid(form)


class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating events."""
    
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    
    def test_func(self):
        event = self.get_object()
        return self.request.user == event.created_by or self.request.user.is_staff
    
    def form_valid(self, form):
        
        messages.success(self.request, 'Event updated successfully!')
        return super().form_valid(form)


class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting events."""
    
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('events:event_list')
    
    def test_func(self):
        event = self.get_object()
        return self.request.user == event.created_by or self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Event deleted successfully.')
        return super().delete(request, *args, **kwargs)


def register_for_event(request, pk):
    """View for registering to an event."""
    
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to register for events.')
        return redirect('login')
    
    event = get_object_or_404(Event, pk=pk)
    
    # Check if user is already registered
    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        messages.info(request, 'You are already registered for this event.')
    else:
        EventRegistration.objects.create(event=event, user=request.user)
        messages.success(request, f'You have successfully registered for "{event.title}".')
    
    return redirect('events:event_detail', pk=pk)


def unregister_from_event(request, pk):
    """View for unregistering from an event."""
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    event = get_object_or_404(Event, pk=pk)
    registration = get_object_or_404(EventRegistration, event=event, user=request.user)
    registration.delete()
    
    messages.success(request, f'You have unregistered from "{event.title}".')
    return redirect('events:event_detail', pk=pk)
