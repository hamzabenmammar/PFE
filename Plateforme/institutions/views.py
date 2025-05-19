from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from notifications.services import NotificationService

from .models import Institution
from .forms import InstitutionFilterForm, InstitutionForm


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
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        context = self.get_context_data()
        researcher_formset = context['researcher_formset']
        project_formset = context['project_formset']
        
        if researcher_formset.is_valid() and project_formset.is_valid():
            self.object = form.save()
            researcher_formset.instance = self.object
            researcher_formset.save()
            project_formset.instance = self.object
            project_formset.save()

            # NOTIFICATION aux modérateurs lors de la création d'une institution
            User = get_user_model()
            moderators = User.objects.filter(is_staff=True)

            for moderator in moderators:
                NotificationService.create_notification(
                    recipient=moderator,
                    notification_type='INSTITUTION_PENDING_REVIEW', # Type spécifique
                    title=f"Nouvelle institution à examiner",
                    message=f"Une nouvelle institution '{form.instance.name}' a été créée par {self.request.user.username} et nécessite votre examen.",
                    related_object=self.object, # Lier à l'institution créée
                    # action_url=... # Ajouter un lien vers la page d'admin ou de modération si elle existe
                )

            messages.success(self.request, _("The institution has been successfully added and will be reviewed by moderators."))
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))
    
    def get_success_url(self):
        return reverse_lazy('institutions:institution_list')


class InstitutionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Institution
    form_class = InstitutionForm
    template_name = 'institution_form.html'
    
    def test_func(self):
        institution = self.get_object()
        return self.request.user == institution.created_by or self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        researcher_formset = context['researcher_formset']
        project_formset = context['project_formset']
        
        if researcher_formset.is_valid() and project_formset.is_valid():
            self.object = form.save()
            researcher_formset.instance = self.object
            researcher_formset.save()
            project_formset.instance = self.object
            project_formset.save()
            
            messages.success(self.request, _("The institution has been successfully updated."))
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))
    
    def get_success_url(self):
        return reverse_lazy('institutions:institution_detail', kwargs={'pk': self.object.pk})


class InstitutionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Institution
    template_name = 'institution_confirm_delete.html'
    success_url = reverse_lazy('institutions:institution_list')
    
    def test_func(self):
        institution = self.get_object()
        return self.request.user == institution.created_by or self.request.user.is_staff
