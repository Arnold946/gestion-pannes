from django.urls import path

from pannes import views


app_name = 'pannes'
urlpatterns = [
    path('affecter/', views.affecter_pannes_view, name='affecter'),
    path('mes-pannes/', views.mes_pannes_view, name='mes_pannes'),
    path('mes-pannes-attr/', views.mes_pannes_attribuees, name='mes_pannes_attr'),
    path('liste_pannes', views.liste_pannes_et_techniciens_view, name='liste_pannes'),
    path('changer_statut/<int:affectation_id>/',views.changer_statut_affectation, name='statut'),
    path('exporter/', views.exporter_pannes_excel_view, name='exporter'),
    path('fiche-reparation/print/<int:affectation_id>/', views.fiche_reparation_printable, name='fiche_reparation_print'),
    path('fiche-reparation/<int:affectation_id>/', views.creer_fiche_de_reparation, name='fiche_reparation_form'),
    path('fiches-reparation/', views.liste_fiches_reparation, name='liste_fiches_reparation'),
    path('notifications/', views.toutes_notifications_view, name='toutes_notifications'),
    path('ajax/charger-materiels/', views.charger_materiels, name='charger_materiels'),
]