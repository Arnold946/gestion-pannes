from django.urls import path
from accounts import views

app_name = 'accounts'
urlpatterns = [
    path('utilisateur/', views.liste_et_ajout_user, name='liste_utilisateurs'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout, name='logout'),
    path('changer_mot_de_passe/', views.change_password, name='change_password'),
    path('chef_unite_informatique/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('technician/dashboard/', views.technician_dashboard, name='technician_dashboard'),
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),

]