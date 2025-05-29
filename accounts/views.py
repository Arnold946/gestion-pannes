from pyexpat.errors import messages
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.core.mail import send_mail
from AppGestIncidents import settings
from accounts.backends import EmailAuthBackend
from accounts.forms import EmailLoginForm, PasswordChangeFormCustom, UserCreationFormCustom
from accounts.models import PermissionInterface, User
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
#--------------------- VUE D'AJOUT D'UTILISATEURS ------------------------------
def liste_et_ajout_user(request):
    # Vérifie les permissions pour l'ajout
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

                return redirect('accounts:liste_user')  # Redirection vers la même page
        else:
            form = UserCreationFormCustom()

    # Récupération des utilisateurs à afficher
    utilisateurs = User.objects.all()

    return render(request, 'accounts/liste_user.html', {
        'form': form,
        'utilisateurs': utilisateurs,
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
                login(request, user)
                if user.role.name == 'chef unite informatique':
                    return redirect('accounts:admin_dashboard')
                elif user.role.name == 'technicien':
                    return redirect('technicien_dashboard')
                else:
                    return redirect('accounts:user_dashboard')
            else:
                # Authentification échouée, message d'erreur
                messages.error(request, 'Identifiants incorrects.')
        else:
            # formulaire invalide (ex: email mal formé)
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = EmailLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout(request):
    pass
                

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


def admin_dashboard(request):
    return render(request, 'accounts/admin_dashboard.html')

def technician_dashboard(request):
    return render(request, 'accounts/technician_dashboard.html')

def user_dashboard(request):
    return render(request, 'accounts/user_dashboard.html')