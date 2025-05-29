from django.urls import path

from pannes import views


app_name = 'pannes'
urlpatterns = [
    path('affecter/', views.affecter_pannes_view, name='affecter'),
    path('mes-pannes/', views.mes_pannes_view, name='mes_pannes'),
    path('exporter/', views.exporter_pannes_excel_view, name='exporter'),
    path('ajax/charger-materiels/', views.charger_materiels, name='charger_materiels'),
]