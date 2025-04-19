from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.utils.translation import gettext as _
from .models import Institution, Country, Specialty

# Unregister Institution if it was already registered
try:
    admin.site.unregister(Institution)
except NotRegistered:
    pass


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'acronym', 'type', 'country', 'city', 'is_approved')
    list_filter = ('type', 'country', 'is_approved', 'specialties')
    search_fields = ('name', 'acronym', 'description')
    filter_horizontal = ('specialties',)
    actions = ['approve_institutions']

    def approve_institutions(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(
            request,
            _("Selected institutions have been successfully approved.")
        )
    approve_institutions.short_description = _("Approve selected institutions")


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
