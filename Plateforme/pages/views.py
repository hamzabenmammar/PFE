from django.db import transaction
from django.urls import reverse
from django.views.generic import TemplateView
from django.utils.timezone import now
from events.models import Event
from resources.models import Corpus, NLPTool ,Document , Course
from projects.models import Project ,ProjectMember
from django.contrib.auth import get_user_model
from forum.models import Topic , ChatRoom
from django.db.models.functions import TruncDate 
from notifications.models import Notification

User = get_user_model()

class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Événements à venir
        context['events'] = Event.objects.filter(
            start_date__gte=now()
        ).order_by('start_date')[:5]
        
        # Compteurs pour les statistiques
        context['corpus_count'] = Corpus.objects.count()
        context['tools_count'] = NLPTool.objects.count()
        context['projects_count'] = Project.objects.count()
        context['members_count'] = User.objects.count()
        
      

            
        # Utilisez last_updated au lieu de views pour les ressources populaires
        context['popular_resources'] = NLPTool.objects.order_by('-last_updated')[:3]
        
        try:
            context['new_members'] = User.objects.order_by('-date_joined')[:5]
        except:
            context['new_members'] = []
            
        try:
            context['recent_discussions'] = Topic.objects.order_by('-creation_date')[:5]
        except:
            context['recent_discussions'] = []
        
        return context
    

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from .models import  Stats ,UserStatusHistory

from institutions.models import Institution

import datetime

from accounts.forms import CustomUserChangeForm  


User = get_user_model()

def is_admin(user):
    """Check if user is an admin"""
    return user.is_staff or user == 'admin'


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Main admin dashboard view"""
    # Get statistics for the dashboard
    today = timezone.now().date()
    
    # Recent users
    recent_users = User.objects.filter(
        date_joined__gte=today-datetime.timedelta(days=30)
    ).order_by('-date_joined')[:10]
    
    # Recent content
    recent_publications =  Document.objects.order_by('-creation_date').prefetch_related('authors')[:5]
    recent_corpora = Corpus.objects.all().order_by('-creation_date')[:5]
    recent_tools = NLPTool.objects.all().order_by('-creation_date')[:5]
    recent_projects = Project.objects.all().order_by('-created_at')[:5]
    
    # Count statistics
    users_count = User.objects.count()
    resources_count = (
        Document.objects.count() + 
        Corpus.objects.count() + 
        NLPTool.objects.count() + 
        Course.objects.count()
    )
    projects_count = Project.objects.filter(status='ongoing').count()
    forum_posts_count = Topic.objects.count() + ChatRoom.objects.count()
    
    # Users by type
    users_by_type = User.objects.order_by('-date_joined')[:10]
    
    # Get monthly growth rates
    last_month = today - datetime.timedelta(days=30)
    two_months_ago = today - datetime.timedelta(days=60)
    
    users_this_month = User.objects.filter(date_joined__gte=last_month).count()
    users_last_month = User.objects.filter(
        date_joined__gte=two_months_ago, 
        date_joined__lt=last_month
    ).count()
    
    if users_last_month > 0:
        user_growth = ((users_this_month - users_last_month) / users_last_month) * 100
    else:
        user_growth = 100 if users_this_month > 0 else 0
        
    # Publications this month
    pubs_this_month = Document.objects.filter(creation_date__gte=last_month).count()
    pubs_last_month = Document.objects.filter(
        creation_date__gte=two_months_ago, 
        creation_date__lt=last_month
    ).count()
    
    if pubs_last_month > 0:
        pubs_growth = ((pubs_this_month - pubs_last_month) / pubs_last_month) * 100
    else:
        pubs_growth = 100 if pubs_this_month > 0 else 0

    # Projects growth
    projects_this_month = Project.objects.filter(created_at__gte=last_month).count()
    projects_last_month = Project.objects.filter(
        created_at__gte=two_months_ago, 
        created_at__lt=last_month
    ).count()
    
    if projects_last_month > 0:
        projects_growth = ((projects_this_month - projects_last_month) / projects_last_month) * 100
    else:
        projects_growth = 100 if projects_this_month > 0 else 0
    
    # Forum posts growth
    posts_this_month = (
        Topic.objects.filter(created_at__gte=last_month).count() + 
        ChatRoom.objects.filter(created_at__gte=last_month).count()
    )
    
    posts_last_month = (
        Topic.objects.filter(created_at__gte=two_months_ago, created_at__lt=last_month).count() + 
        ChatRoom.objects.filter(created_at__gte=two_months_ago, created_at__lt=last_month).count()  
    )
    
    if posts_last_month > 0:
        posts_growth = ((posts_this_month - posts_last_month) / posts_last_month) * 100
    else:
        posts_growth = 100 if posts_this_month > 0 else 0
    
    # Combine all statistics
    context = {
        'recent_users': recent_users,
        'recent_publications': recent_publications,
        'recent_corpora': recent_corpora,
        'recent_tools': recent_tools,
        'recent_projects': recent_projects,
        'users_count': users_count,
        'resources_count': resources_count,
        'projects_count': projects_count,
        'forum_posts_count': forum_posts_count,
        'users_by_type': users_by_type,
        'user_growth': user_growth,
        'pubs_growth': pubs_growth,
        'projects_growth': projects_growth,
        'posts_growth': posts_growth,
    }
    
    return render(request, 'admin/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_users(request):
    """Admin user management view"""
    # Récupération des filtres passés en querystring
    filter_status = request.GET.get('status', '')
    search = request.GET.get('search', '').strip()
    
    # Base queryset : tous les utilisateurs
    qs = User.objects.all().order_by('-date_joined')
    
    # Filtrage "statut"
    if filter_status == 'active':
        qs = qs.filter(is_active=True)
    elif filter_status == 'pending':
        # en attente : non actifs et non vérifiés
        qs = qs.filter(is_active=False, is_email_verified=False)
    elif filter_status == 'blocked':
        # bloqués : non actifs mais vérifiés (ou autre règle métier)
        qs = qs.filter(is_active=False, is_email_verified=True)
    
    # Recherche full-text sur username, email, prénom, nom
    if search:
        qs = qs.filter(
            Q(full_name__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Nombre d'utilisateurs "en attente" pour l'en-tête
    pending_users_count = User.objects.filter(
        is_active=False,
        is_email_verified=False
    ).count()
    
    context = {
        'users': qs,
        'pending_users_count': pending_users_count,
        'filter_status': filter_status,
        'search': search,
    }
    return render(request, 'admin/users.html', context)

@login_required
@user_passes_test(is_admin)
def admin_user_new(request):
    """Vue pour créer un nouvel utilisateur."""
    if request.method == 'POST':
        # Extraire les données du formulaire
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        status = request.POST.get('status', 'active')
        
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(full_name=full_name).exists():
            messages.error(request, f"Un utilisateur avec le nom {full_name} existe déjà.")
            return render(request, 'admin/users/new.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, f"Un utilisateur avec l'email {email} existe déjà.")
            return render(request, 'admin/users/new.html')
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            full_name=full_name,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            status=status
        )
        
        # Créer une entrée dans l'historique
        UserStatusHistory.objects.create(
            user=user,
            old_status='new',
            new_status=status,
            changed_by=request.user,
            change_date=timezone.now()
        )
        
        messages.success(request, f"L'utilisateur {full_name} a été créé avec succès.")
        return redirect('pages:admin_users')
    
    return render(request, 'admin/users_new.html')

@login_required
@user_passes_test(is_admin)
@transaction.atomic
def admin_user_activate(request, user_id):
    """Vue pour activer un utilisateur."""
    user = get_object_or_404(User, id=user_id)
    
    if user.status == 'active':
        messages.info(request, f"L'utilisateur {user.full_name} est déjà actif.")
        return redirect('pages:admin_users')
    
    old_status = user.status
    user.is_active = True
    user.status = 'active'
    user.save()
    
    # Créer une entrée dans l'historique
    UserStatusHistory.objects.create(
        user=user,
        old_status=old_status,
        new_status='active',
        changed_by=request.user,
        change_date=timezone.now()
    )
    
    # Notification d'activation
    Notification.objects.create(
        recipient=user,
        title="Compte activé",
        message="Votre compte a été activé par un administrateur. Vous pouvez maintenant accéder à toutes les fonctionnalités."
    )
    
    messages.success(request, f"L'utilisateur {user.full_name} a été activé avec succès.")
    
    # Rediriger vers la page précédente si disponible
    next_url = request.GET.get('next', reverse('pages:admin_users'))
    return redirect(next_url)

@login_required
@user_passes_test(is_admin)
def admin_user_block(request, user_id):
    """Vue pour bloquer un utilisateur."""
    user = get_object_or_404(User, id=user_id)
    
    # Empêcher le blocage de soi-même
    if user == request.user:
        messages.error(request, "Vous ne pouvez pas bloquer votre propre compte.")
        return redirect('pages:admin_users')
    
    if user.status == 'blocked':
        messages.info(request, f"L'utilisateur {user.full_name} est déjà bloqué.")
        return redirect('pages:admin_users')
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        old_status = user.status
        user.is_active = False
        user.status = 'blocked'
        user.save()
        
        # Créer une entrée dans l'historique
        UserStatusHistory.objects.create(
            user=user,
            old_status=old_status,
            new_status='blocked',
            changed_by=request.user,
            change_date=timezone.now(),
            reason=reason
        )
        
        # Notification de blocage
        Notification.objects.create(
            recipient=user,
            title="Compte bloqué",
            message="Votre compte a été bloqué par un administrateur. Veuillez contacter le support si besoin."
        )
        
        messages.success(request, f"L'utilisateur {user.full_name} a été bloqué avec succès.")
        return redirect('pages:admin_users')
    
    return render(request, 'admin/block_confirm.html', {'user_obj': user})


@login_required
@user_passes_test(is_admin)
def admin_user_history(request, user_id):
    """Vue pour afficher l'historique des statuts d'un utilisateur."""
    user = get_object_or_404(User, id=user_id)
    history = UserStatusHistory.objects.filter(user=user).order_by('-change_date')
    
    context = {
        'user_obj': user,
        'history': history,
    }
    
    return render(request, 'admin/history.html', context)

@login_required
@user_passes_test(is_admin)
def admin_user_edit(request, user_id):
    """Admin view to edit user details"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"L'utilisateur {user.username} a été mis à jour avec succès.")
            return redirect('pages:admin_users')
    else:
        form = CustomUserChangeForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
    }
    
    return render(request, 'admin/user_edit.html', context)


@login_required
@user_passes_test(is_admin)
def admin_user_status(request, user_id, status):
    """Change user status (approve, block, etc.)"""
    user = get_object_or_404(User, id=user_id)
    user.status = status
    user.save()
    
    status_messages = {
        'active': "activé",
        'pending': "mis en attente",
        'inactive': "désactivé",
        'blocked': "bloqué"
    }
    
    messages.success(request, f"L'utilisateur {user.username} a été {status_messages.get(status, 'mis à jour')}.")
    return redirect('admin_users')


@login_required
@user_passes_test(is_admin)
def admin_publications(request):
    """Admin publications management"""
    # Filter parameters
    publication_type = request.GET.get('publication_type', '')
    status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    # Base queryset
    publications = Document.objects.all().order_by('-creation_date')
    
    # Apply filters
    if publication_type:
        publications = publications.filter(publication_type=publication_type)
    if status:
        publications = publications.filter(status=status)
    if search:
        publications = publications.filter(
            Q(title__icontains=search) | 
            Q(abstract__icontains=search) |
            Q(keywords__icontains=search) |
            Q(authors__username__icontains=search)
        ).distinct()
    
    pending_publications_count = Document.objects.filter(status='pending').count()
    
    context = {
        'publications': publications,
        'pending_publications_count': pending_publications_count,
        'filter_publication_type': publication_type,
        'filter_status': status,
        'search': search,
    }
    
    return render(request, 'admin/publications.html', context)


@login_required
@user_passes_test(is_admin)
def admin_corpora(request):
    """Admin corpora management"""
    # Filter parameters
    corpus_type = request.GET.get('corpus_type', '')
    status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    # Base queryset
    corpora = Corpus.objects.all().order_by('-creation_date')
    
    # Apply filters
    if corpus_type:
        corpora = corpora.filter(corpus_type=corpus_type)
    if status:
        corpora = corpora.filter(status=status)
    if search:
        corpora = corpora.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search) |
            Q(owner__username__icontains=search)
        )
    
    pending_corpora_count = Corpus.objects.filter(status='pending').count()
    
    context = {
        'corpora': corpora,
        'pending_corpora_count': pending_corpora_count,
        'filter_corpus_type': corpus_type,
        'filter_status': status,
        'search': search,
    }
    
    return render(request, 'admin/corpora.html', context)

@login_required
@user_passes_test(is_admin)
def admin_tools(request):
    """Admin tools management"""
    # Filter parameters
    tool_type = request.GET.get('tool_type', '')
    status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    # Base queryset
    tools = NLPTool.objects.all().order_by('-creation_date')
    
    # Apply filters
    if tool_type:
        tools = tools.filter(tool_type=tool_type)
    if status:
        tools = tools.filter(status=status)
    if search:
        tools = tools.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search) |
            Q(owner__username__icontains=search)
        )
    
    pending_tools_count = NLPTool.objects.filter(status='pending').count()
    
    context = {
        'tools': tools,
        'pending_tools_count': pending_tools_count,
        'filter_tool_type': tool_type,
        'filter_status': status,
        'search': search,
    }
    
    return render(request, 'admin/tools.html', context)


@login_required
@user_passes_test(is_admin)
def admin_projects(request):
    """Admin projects management"""
    # Filter parameters
    status = request.GET.get('status', '')
    visibility = request.GET.get('visibility', '')
    search = request.GET.get('search', '')
    
    # Base queryset
    projects = Project.objects.all().order_by('-created_at')
    
    # Apply filters
    if status:
        projects = projects.filter(status=status)
    if visibility:
        projects = projects.filter(visibility=visibility)
    if search:
        projects = projects.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) |
            Q(objectives__icontains=search) |
            Q(participants__username__icontains=search)
        ).distinct()
    
    context = {
        'projects': projects,
        'filter_status': status,
        'filter_visibility': visibility,
        'search': search,
    }
    
    return render(request, 'admin/projects.html', context)


@login_required
@user_passes_test(is_admin)
def admin_courses(request):
    """Admin courses management"""
    # Filter parameters
    level = request.GET.get('level', '')
    is_public = request.GET.get('is_public', '')
    search = request.GET.get('search', '')
    
    # Base queryset
    courses = Course.objects.all().order_by('-creation_date')
    
    # Apply filters
    if level:
        courses = courses.filter(level=level)
    if is_public:
        courses = courses.filter(is_public=(is_public == 'true'))
    if search:
        courses = courses.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) |
            Q(author__username__icontains=search)
        )
    
    context = {
        'courses': courses,
        'filter_level': level,
        'filter_is_public': is_public,
        'search': search,
    }
    
    return render(request, 'admin/courses.html', context)


@login_required
@user_passes_test(is_admin)
def admin_forum(request):
    """Admin forum management"""
    # Filter parameters
    category = request.GET.get('category', '')
    is_closed = request.GET.get('is_closed', '')
    search = request.GET.get('search', '')
    
    # Base queryset
    topics = Topic.objects.all().order_by('-created_at')
    
    # Apply filters
    if category:
        topics = topics.filter(category_id=category)
    if is_closed:
        topics = topics.filter(is_closed=(is_closed == 'true'))
    if search:
        topics = topics.filter(
            Q(title__icontains=search) | 
            Q(content__icontains=search) |
            Q(author__username__icontains=search)
        )
    
    # Get categories for filter
    
    
    context = {
        'topics': topics,
        'filter_category': category,
        'filter_is_closed': is_closed,
        'search': search,
    }
    
    return render(request, 'admin/forum.html', context)


@login_required
@user_passes_test(is_admin)
def admin_institutions(request):
    """Admin institutions management"""
    # Filter parameters
    country = request.GET.get('country', '')
    is_active = request.GET.get('is_active', '')
    search = request.GET.get('search', '')
    
    # Base queryset
    institutions = Institution.objects.all().order_by('name')
    
    # Apply filters
    if country:
        institutions = institutions.filter(country=country)
    if is_active:
        institutions = institutions.filter(is_active=(is_active == 'true'))
    if search:
        institutions = institutions.filter(
            Q(name__icontains=search) | 
            Q(acronym__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Get unique countries for filter
    countries = Institution.objects.values_list('country', flat=True).distinct()
    
    context = {
        'institutions': institutions,
        'countries': countries,
        'filter_country': country,
        'filter_is_active': is_active,
        'search': search,
    }
    
    return render(request, 'admin/institutions.html', context)


@login_required
@user_passes_test(is_admin)
def admin_calls(request):
    """Admin calls for papers management"""
    # Filter parameters
    call_type = request.GET.get('call_type', '')
    is_active = request.GET.get('is_active', '')
    search = request.GET.get('search', '')
    
    # Base queryset
    calls = Event.objects.all().order_by('submission_deadline')
    
    # Apply filters
    if call_type:
        calls = calls.filter(call_type=call_type)
    if is_active:
        calls = calls.filter(is_active=(is_active == 'true'))
    if search:
        calls = calls.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) |
            Q(organizer__icontains=search) |
            Q(topics__icontains=search)
        )
    
    context = {
        'calls': calls,
        'filter_call_type': call_type,
        'filter_is_active': is_active,
        'search': search,
    }
    
    return render(request, 'admin/calls.html', context)

@login_required
@user_passes_test(is_admin)
def admin_statistics(request):
    """Admin statistics view"""
    # 1. Récupérer la plage de dates
    start = request.GET.get('start_date', '')
    end = request.GET.get('end_date', '')

    if start:
        start_date = datetime.datetime.strptime(start, '%Y-%m-%d').date()
    else:
        start_date = (timezone.now() - datetime.timedelta(days=30)).date()

    if end:
        end_date = datetime.datetime.strptime(end, '%Y-%m-%d').date()
    else:
        end_date = timezone.now().date()

    # 2. Charger les Stats existantes
    stats = Stats.objects.filter(date__gte=start_date, date__lte=end_date).order_by('date')

    # 3. Si aucune ligne, calculer les valeurs "à la volée"
    if not stats.exists():
        last = None
        current_stats = {
            'users_count': User.objects.count(),
            'publications_count': Document.objects.count(),
            'corpora_count': Corpus.objects.count(),
            'tools_count': NLPTool.objects.count(),
            'projects_count': Project.objects.count(),
            'forum_posts_count': Topic.objects.count() + ChatRoom.objects.count(),
            'visits_count': 0,        # ou calculer si vous avez un modèle Visite
            'downloads_count': 0,     # pareil pour les téléchargements
        }
    else:
        last = stats.last()
        current_stats = {
            'users_count': last.users_count,
            'publications_count': last.publications_count,
            'corpora_count': last.corpora_count,
            'tools_count': last.tools_count,
            'projects_count': last.projects_count,
            'forum_posts_count': last.forum_posts_count,
            'visits_count': last.visits_count,
            'downloads_count': last.downloads_count,
        }

    # 4. Préparer les données brutes pour les graphiques
    # Les dates sont déjà des objets date — on les convertit en string automatiquement au rendu du JSON côté front.
    chart_dates     = [stat.date for stat in stats]
    users_data      = [stat.users_count for stat in stats]
    resources_data  = [stat.publications_count + stat.corpora_count + stat.tools_count for stat in stats]
    visits_data     = [stat.visits_count for stat in stats]
    downloads_data  = [stat.downloads_count for stat in stats]

    # 5. Comptage des inscriptions utilisateurs par jour
    user_regs = (
        User.objects
        .filter(date_joined__date__gte=start_date, date_joined__date__lte=end_date)
        .annotate(day=TruncDate('date_joined'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    user_reg_dates  = [row['day'] for row in user_regs]
    user_reg_counts = [row['count'] for row in user_regs]

    context = {
        'stats': stats,
        'current_stats': current_stats,
        'start_date': start_date,
        'end_date': end_date,

        # Séries pour les graphiques (retournées au template, qui peut les JSONifier)
        'chart_dates': chart_dates,
        'users_data': users_data,
        'resources_data': resources_data,
        'visits_data': visits_data,
        'downloads_data': downloads_data,

        # Séries pour le graphique des inscriptions
        'user_reg_dates':  user_reg_dates,
        'user_reg_counts': user_reg_counts,
    }

    return render(request, 'admin/statistics.html', context)

@login_required
@user_passes_test(is_admin)
def admin_settings(request):
    """Admin settings view"""
    # You can implement site settings model if needed
    return render(request, 'admin/settings.html')


@login_required
@user_passes_test(is_admin)
def admin_security(request):
    """Admin security view"""
    # Recent login attempts
    # Implement login attempts model if needed
    return render(request, 'admin/security.html')


# API endpoints for dashboard
@login_required
@user_passes_test(is_admin)
def admin_api_stats(request):
    """API endpoint for dashboard statistics"""
    today = timezone.now().date()
    last_month = today - datetime.timedelta(days=30)
    two_months_ago = today - datetime.timedelta(days=60)
    
    # Users stats
    users_count = User.objects.count()
    users_this_month = User.objects.filter(date_joined__gte=last_month).count()
    users_last_month = User.objects.filter(
        date_joined__gte=two_months_ago, 
        date_joined__lt=last_month
    ).count()
    
    if users_last_month > 0:
        user_growth = ((users_this_month - users_last_month) / users_last_month) * 100
    else:
        user_growth = 100 if users_this_month > 0 else 0
    
    # Combine all resources
    resources_count = (
        Document.objects.count() + 
        Corpus.objects.count() + 
        NLPTool.objects.count() + 
        Course.objects.count()
    )
    
    resources_this_month = (
        Document.objects.filter(created_at__gte=last_month).count() +
        Corpus.objects.filter(created_at__gte=last_month).count() +
        NLPTool.objects.filter(created_at__gte=last_month).count() +
        Course.objects.filter(created_at__gte=last_month).count()
    )
    
    resources_last_month = (
        Document.objects.filter(created_at__gte=two_months_ago, created_at__lt=last_month).count() +
        Corpus.objects.filter(created_at__gte=two_months_ago, created_at__lt=last_month).count() +
        NLPTool.objects.filter(created_at__gte=two_months_ago, created_at__lt=last_month).count() +
        Course.objects.filter(created_at__gte=two_months_ago, created_at__lt=last_month).count()
    )
    
    if resources_last_month > 0:
        resources_growth = ((resources_this_month - resources_last_month) / resources_last_month) * 100
    else:
        resources_growth = 100 if resources_this_month > 0 else 0
    
    # Projects
    projects_count = Project.objects.filter(status='ongoing').count()
    projects_this_month = Project.objects.filter(created_at__gte=last_month).count()
    projects_last_month = Project.objects.filter(
        created_at__gte=two_months_ago, 
        created_at__lt=last_month
    ).count()
    
    if projects_last_month > 0:
        projects_growth = ((projects_this_month - projects_last_month) / projects_last_month) * 100
    else:
        projects_growth = 100 if projects_this_month > 0 else 0
    
    # Forum posts
    forum_posts_count = Topic.objects.count() + ChatRoom.objects.count()
    posts_this_month = (
        Topic.objects.filter(created_at__gte=last_month).count() + 
        ChatRoom.objects.filter(created_at__gte=last_month).count()
    )
    
    posts_last_month = (
        Topic.objects.filter(created_at__gte=two_months_ago, created_at__lt=last_month).count() + 
        ChatRoom.objects.filter(created_at__gte=two_months_ago, created_at__lt=last_month).count()  
    )
    
    if posts_last_month > 0:
        posts_growth = ((posts_this_month - posts_last_month) / posts_last_month) * 100
    else:
        posts_growth = 100 if posts_this_month > 0 else 0
    
    return JsonResponse({
        'users': {
            'count': users_count,
            'growth': user_growth,
        },
        'resources': {
            'count': resources_count,
            'growth': resources_growth,
        },
        'projects': {
            'count': projects_count,
            'growth': projects_growth,
        },
        'forum_posts': {
            'count': forum_posts_count,
            'growth': posts_growth,
        },
    })


@login_required
@user_passes_test(is_admin)
def admin_api_recent_users(request):
    """API endpoint for recent users"""
    recent_users = User.objects.all().order_by('-date_joined')[:10]
    data = []
    
    for user in recent_users:
        data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'status': user.get_status_display(),
            'date_joined': user.date_joined.strftime('%Y-%m-%d'),
        })
    
    return JsonResponse({'users': data})


@login_required
@user_passes_test(is_admin)
def admin_api_recent_content(request):
    """API endpoint for recent content"""
    content_type = request.GET.get('type', 'all')
    
    if content_type == 'publications':
        items = Document.objects.all().order_by('-created_at')[:10]
        data = [
            {
                'id': item.id,
                'title': item.title,
                'type': item.get_publication_type_display(),
                'author': ", ".join([author.get_full_name() for author in item.authors.all()]),
                'date': item.created_at.strftime('%Y-%m-%d'),
                'status': item.get_status_display(),
            } 
            for item in items
        ]
    elif content_type == 'corpus':
        items = Corpus.objects.all().order_by('-created_at')[:10]
        data = [
            {
                'id': item.id,
                'title': item.name,
                'type': item.get_corpus_type_display(),
                'author': item.owner.get_full_name(),
                'date': item.created_at.strftime('%Y-%m-%d'),
                'status': item.get_status_display(),
            } 
            for item in items
        ]
    elif content_type == 'tools':
        items = NLPTool.objects.all().order_by('-created_at')[:10]
        data = [
            {
                'id': item.id,
                'title': item.name,
                'type': item.get_tool_type_display(),
                'author': item.owner.get_full_name(),
                'date': item.created_at.strftime('%Y-%m-%d'),
                'status': item.get_status_display(),
            } 
            for item in items
        ]
    elif content_type == 'projects':
        items = ProjectMember.objects.all().order_by('-created_at')[:10]
        data = [
            {
                'id': item.id,
                'title': item.title,
                'type': 'Projet',
                'author': ", ".join([participant.get_full_name() for participant in item.participants.all()[:2]]),
                'date': item.created_at.strftime('%Y-%m-%d'),
                'status': item.get_status_display(),
            } 
            for item in items
        ]
    else:
        # All content mixed
        publications = Document.objects.all().order_by('-created_at')[:5]
        corpora = Corpus.objects.all().order_by('-created_at')[:5]
        tools = NLPTool.objects.all().order_by('-created_at')[:5]
        
        data = []
        
        for item in publications:
            data.append({
                'id': item.id,
                'title': item.title,
                'type': 'Publication',
                'author': ", ".join([author.get_full_name() for author in item.authors.all()]),
                'date': item.created_at.strftime('%Y-%m-%d'),
                'status': item.get_status_display(),
            })
        
        for item in corpora:
            data.append({
                'id': item.id,
                'title': item.name,
                'type': 'Corpus',
                'author': item.owner.get_full_name(),
                'date': item.created_at.strftime('%Y-%m-%d'),
                'status': item.get_status_display(),
            })
        
        for item in tools:
            data.append({
                'id': item.id,
                'title': item.name,
                'type': 'Outil',
                'author': item.owner.get_full_name(),
                'date': item.created_at.strftime('%Y-%m-%d'),
                'status': item.get_status_display(),
            })
        
        # Sort by date
        data.sort(key=lambda x: x['date'], reverse=True)
        data = data[:10]
    
    return JsonResponse({'content': data})

