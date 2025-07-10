import calendar
from collections import OrderedDict

from django.contrib.auth.decorators import user_passes_test, login_required
from django.db import IntegrityError
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from pyexpat.errors import messages
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.core.mail import send_mail
from AppGestIncidents import settings
from accounts.backends import EmailAuthBackend
from accounts.forms import EmailLoginForm, PasswordChangeFormCustom, UserCreationFormCustom, ModifierUtilisateurForm
from accounts.models import PermissionInterface, User
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt

from pannes.models import Panne, AffectationPanne, Notification


# Create your views here.
#--------------------- VUE D'AJOUT D'UTILISATEURS ------------------------------
@login_required
def liste_et_ajout_user(request):
    permission = PermissionInterface.objects.filter(
        role=request.user.role,
        interface__name="ajout_utilisateur"
    ).first()
    print("Permission récupérée :", permission)
    peut_ajouter = permission and permission.peut_ajouter
    form = None

    if peut_ajouter:
        if request.method == 'POST':
            form = UserCreationFormCustom(request.POST, request.FILES)
            if form.is_valid():
                user = form.save(commit=False)
                mot_de_passe_temporaire = form.cleaned_data['password']
                user.set_password(mot_de_passe_temporaire)
                user.doit_changer_mot_de_passe = True
                try:
                    user.save()

                    # Envoi de l'e-mail
                    try:
                        send_mail(
                            subject="Votre compte a été créé",
                            message=f"Bonjour {user.username},\n\nVotre mot de passe temporaire est : {mot_de_passe_temporaire}\nMerci de le changer à votre première connexion.",
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[user.email],
                            fail_silently=False,
                        )
                    except Exception as e:
                        print(f"Erreur lors de l'envoi de l'e-mail : {e}")

                    return redirect('accounts:liste_utilisateurs')

                except IntegrityError as e:
                    messages.error(request, "Erreur : ce nom d’utilisateur ou cette adresse e-mail existe déjà.")
            else:
                messages.error(request, "Le formulaire est invalide.")
        else:
            form = UserCreationFormCustom()

    utilisateurs_actifs = User.objects.filter(is_active=True)
    utilisateurs_inactifs = User.objects.filter(is_active=False)
    return render(request, 'accounts/liste_user.html', {
        'form': form,
        'utilisateurs_actifs': utilisateurs_actifs,
        'utilisateurs_inactifs': utilisateurs_inactifs,
        'peut_ajouter': peut_ajouter,
    })
#---------------------------- VUE DE CONNEXION D'UTILISATEURS ------------------------

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect


def login_view(request):
    if request.method == 'POST':
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if user.role.name == 'chef unite informatique':
                        return redirect('accounts:admin_dashboard')
                    elif user.role.name == 'technicien':
                        return redirect('accounts:technician_dashboard')
                    else:
                        return redirect('accounts:user_dashboard')
                else:
                    messages.error(request, 'Votre compte est désactivé.')
            else:
                messages.error(request, 'Identifiants incorrects.')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = EmailLoginForm()

    return render(request, 'accounts/login.html', {'form': form})

from django.contrib.auth import logout as auth_logout
def logout(request):
    auth_logout(request)
    return redirect('accounts:login')

                

#-------------------------- VUE DE CHENGEMENT MDP D'UTILISATEURS ------------------------
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeFormCustom(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.doit_changer_mot_de_passe = False
            user.save()
            return redirect('accounts:login')  # Redirige vers la page de connexion après le changement de mot de passe
    else:
        form = PasswordChangeFormCustom(user=request.user)

    return render(request, 'accounts/change_password.html', {'form': form})

@login_required
def admin_dashboard(request):
    utilisateur = request.user
    notifications = Notification.objects.filter(utilisateur=utilisateur).order_by('-date_envoi')[:3]
    total_pannes = Panne.objects.count()
    pannes_en_cours = AffectationPanne.objects.filter(statut_reparation = 'en_cours').count()
    pannes_resolues = AffectationPanne.objects.filter(statut_reparation = 'terminee').count()

    pannes_recentes = Panne.objects.order_by('-date_signalement')[:3]

    # Graphique bar : Pannes par mois (6 derniers mois)
    today = timezone.now()
    six_months_ago = today.replace(month=max(today.month - 5, 1), day=1)
    pannes_par_mois_qs = (
        Panne.objects
        .filter(date_signalement__gte=six_months_ago)
        .annotate(month=TruncMonth('date_signalement'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )

    mois_labels = []
    mois_data = []

    mois_dict = OrderedDict()

    for i in range(6):
        mois = (today.replace(day=1) - timezone.timedelta(days=i * 30)).strftime('%B')
        mois_dict[mois] = 0
    mois_dict = OrderedDict(reversed(mois_dict.items()))

    for item in pannes_par_mois_qs:
        nom_mois = calendar.month_name[item['month'].month]
        mois_dict[nom_mois] = item['total']

    mois_labels = list(mois_dict.keys())
    mois_data = list(mois_dict.values())

    # Graphique ligne : par priorité
    priorites = ['faible', 'moyenne', 'haute']
    priorite_data = [Panne.objects.filter(priority=p).count() for p in priorites]
    return render(request, 'accounts/admin_dashboard.html', {
        'total_pannes': total_pannes,
        'pannes_en_cours': pannes_en_cours,
        'pannes_resolues': pannes_resolues,
        'pannes_recentes': pannes_recentes,
        'mois_labels': mois_labels,
        'mois_data': mois_data,
        'priorites': priorites,
        'priorite_data': priorite_data,
        'notifications' : notifications
    })
@login_required
def technician_dashboard(request):
    return render(request, 'accounts/technician_dashboard.html')
@login_required
def user_dashboard(request):
    return render(request, 'accounts/user_dashboard.html')

def test_email(request):
    try:
        send_mail(
            subject="Test Email depuis Django",
            message="Ceci est un test d'envoi d'e-mail depuis Django avec Gmail.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['arnoldlouis237@gmail.com'],  # mets ici ton adresse email
            fail_silently=False,
        )
        return HttpResponse("E-mail envoyé avec succès ✅")
    except Exception as e:
        return HttpResponse(f"Erreur lors de l'envoi : {e}")
@login_required
def liste_permissions_view(request):
    permissions = PermissionInterface.objects.select_related('role', 'interface')
    return render(request, 'accounts/permission.html', {
        'permissions': permissions
    })

@user_passes_test(lambda u: u.role.name == "chef unite informatique")
def desactiver_utilisateur(request, user_id):
    utilisateur = get_object_or_404(User, id=user_id)

    if utilisateur.is_active:
        utilisateur.is_active = False
        utilisateur.save()
        messages.success(request, f"L'utilisateur {utilisateur.username} a été désactivé.")
    else:
        messages.warning(request, f"L'utilisateur {utilisateur.username} est déjà désactivé.")
    return redirect('accounts:liste_utilisateurs')

@user_passes_test(lambda u: u.role.name == "chef unite informatique")
def reactiver_utilisateur(request, user_id):
    utilisateur = get_object_or_404(User, id=user_id)
    if not utilisateur.is_active:
        utilisateur.is_active = True
        utilisateur.save()
        messages.success(request, f"L'utilisateur {utilisateur.username} a été réactivé.")
    else:
        messages.warning(request, f"L'utilisateur {utilisateur.username} est déjà activé.")
    return redirect('accounts:liste_utilisateurs')

@login_required
def modifier_utilisateur(request, user_id):
    utilisateur = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = ModifierUtilisateurForm(request.POST, request.FILES, instance=utilisateur)
        if form.is_valid():
            form.save()
            return redirect('liste_utilisateurs')  # ou une autre vue
    else:
        form = ModifierUtilisateurForm(instance=utilisateur)

    return render(request, 'utilisateurs/modifier.html', {
        'form': form,
        'utilisateur': utilisateur
    })
