from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from notifications.services import NotificationService
import logging

from .models import Institution
from .forms import InstitutionFilterForm, InstitutionForm

logger = logging.getLogger(__name__)


class InstitutionListView(ListView):
    model = Institution
    template_name = 'institution_list.html'
    context_object_name = 'institutions'
    paginate_by = 9

    def get_queryset(self):
        queryset = Institution.objects.all()
        
        # Apply filters from form
        form = InstitutionFilterForm(self.request.GET)
        if form.is_valid():
            institution_type = form.cleaned_data.get('institution_type')
            country = form.cleaned_data.get('country')
            specialty = form.cleaned_data.get('specialty')
            search_term = form.cleaned_data.get('search_term')
            
            if institution_type:
                queryset = queryset.filter(type=institution_type)
            
            if country:
                queryset = queryset.filter(country=country)
            
            if specialty:
                queryset = queryset.filter(specialties=specialty)
            
            if search_term:
                queryset = queryset.filter(
                    Q(name__icontains=search_term) | 
                    Q(description__icontains=search_term) |
                    Q(acronym__icontains=search_term)
                )
        
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = InstitutionFilterForm(self.request.GET)
        return context


class InstitutionDetailView(DetailView):
    model = Institution
    template_name = 'institutions/institution_detail.html'
    context_object_name = 'institution'


class InstitutionCreateView(LoginRequiredMixin, CreateView):
    model = Institution
    form_class = InstitutionForm
    template_name = 'institutions/institution_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def post(self, request, *args, **kwargs):
        logger.info("POST request received")
        logger.info(f"POST data: {request.POST}")
        logger.info(f"FILES: {request.FILES}")
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        try:
            logger.info("Form is valid")
            form.instance.created_by = self.request.user
            self.object = form.save()
            logger.info(f"Institution created with ID: {self.object.id}")
            
            # NOTIFICATION aux modérateurs lors de la création d'une institution
            User = get_user_model()
            moderators = User.objects.filter(is_staff=True)

            for moderator in moderators:
                NotificationService.create_notification(
                    recipient=moderator,
                    notification_type='INSTITUTION_PENDING_REVIEW',
                    title=f"New institution to examine",
                    message=f"A new institution'{form.instance.name}'was created by {self.request.user.username} and requires your review.",
                    related_object=self.object,
                )

            messages.success(self.request, _("The institution has been successfully added and will be reviewed by moderators."))
            return redirect(self.get_success_url())
        except Exception as e:
            logger.error(f"Error creating institution: {str(e)}")
            messages.error(self.request, f"An error occurred while creating the institution: {str(e)}")
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        logger.error(f"Form is invalid: {form.errors}")
        messages.error(self.request, _("Please correct any errors in the form."))
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('institutions:institution_list')


class InstitutionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Institution
    form_class = InstitutionForm
    template_name = 'institutions/institution_form.html'
    
    def test_func(self):
        institution = self.get_object()
        return self.request.user == institution.created_by or self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def form_valid(self, form):
        try:
            self.object = form.save()
            logger.info(f"Institution successfully updated - ID: {self.object.id}")
            messages.success(self.request, "The institution has been successfully updated.")
            return redirect(self.get_success_url())
        except Exception as e:
            logger.error(f"Error updating institution: {str(e)}")
            messages.error(self.request, f"An error occurred while updating the institution: {str(e)}")
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        logger.error(f"Invalid edit form - Errors: {form.errors}")
        messages.error(self.request, "Please correct the errors in the form.")
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('institutions:institution_detail', kwargs={'pk': self.object.pk})


class InstitutionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Institution
    template_name = 'institutions/institution_confirm_delete.html'
    success_url = reverse_lazy('institutions:institution_list')
    
    def test_func(self):
        institution = self.get_object()
        return self.request.user == institution.created_by or self.request.user.is_staff
        
    def delete(self, request, *args, **kwargs):
        logger.info(f"Institution Deletion - ID: {self.get_object().id}")
        messages.success(self.request, "The institution has been successfully abolished.")
        return super().delete(request, *args, **kwargs)
