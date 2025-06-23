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
    path('ajax/charger-materiels/', views.charger_materiels, name='charger_materiels'),
]