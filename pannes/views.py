import openpyxl
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from openpyxl.styles import Font, PatternFill, Alignment

from accounts.models import PermissionInterface, User
from materiels.models import Materiel, CategorieMateriel
from pannes.forms import AffectationPanneForm, PanneForm
from pannes.models import Panne, AffectationPanne, Notification


# Create your views here.
def liste_pannes_et_techniciens_view(request):
    pannes = Panne.objects.all()
    techniciens = User.objects.filter(role__name='technicien')
    pannes_non_attribuees = Panne.objects.filter(affectation_panne__isnull=True)

    context={
        'pannes':pannes,
        'techniciens':techniciens,
        'pannes_non_attribuees':pannes_non_attribuees
    }

    return render(request, 'pannes/liste_pannes.html', context)

def affecter_pannes_view(request):
    if request.method == 'POST':
        panne_id = request.POST.get('panne')
        technicien_id = request.POST.get('technicien')

        try:
            panne = Panne.objects.get(id=panne_id)
            technicien = User.objects.get(id=technicien_id, role__name='technicien')
            chef = request.user

            # Vérifie que l'affectation n'existe pas déjà
            if AffectationPanne.objects.filter(panne=panne, technicien=technicien).exists():
                messages.warning(request, "Cette panne est déjà attribuée à ce technicien.")
            else:
                AffectationPanne.objects.create(
                    panne=panne,
                    technicien=technicien,
                    attribue_par=chef,
                    status_reparation= 'Non traitée'
                )

                Notification.objects.create(
                    utilisateur=technicien,
                    panne=panne,
                    message=f"Panne assignée à {panne.user}",
                )
                messages.succes(request, "La panne a bien été atribuée")
        except Panne.DoesNotExist:
            messages.error(request, "Panne introuvable.")
        except User.DoesNotExist:
            messages.error(request, "Technicien introuvable.")

        return redirect('pannes:liste_pannes')
    return redirect('pannes:liste_pannes')

def mes_pannes_view(request):
    # Vérifie les permissions
    permission = PermissionInterface.objects.filter(
        role=request.user.role,
        interface__name="mes_pannes"
    ).first()

    #if not permission or not permission.peut_ajouter:
        #return HttpResponseForbidden("Vous n'avez pas la permission d'accéder à cette page.")
    
    if request.method == 'POST':
        form = PanneForm(request.POST)
        if form.is_valid():
            panne = form.save(commit=False)
            panne.user = request.user
            panne.save()
            return redirect('pannes:mes_pannes')  # rechargement de la page avec la nouvelle panne
    else:
        form = PanneForm()

    categories = CategorieMateriel.objects.all()
    pannes = Panne.objects.filter(user=request.user)  # liste des pannes à afficher
    return render(request, 'pannes/mes_pannes.html', {'form': form, 'pannes': pannes, 'categories':categories})

def mes_pannes_attribuees(request):
    return render(request, 'pannes/mes_pannes_attribuees.html')

def liste_pannes_view(request):
    return render(request, 'pannes/liste_pannes.html')

def exporter_pannes_excel_view(request):
    #creation du classeur et de la feuille
    global cell
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Liste des pannes"

    #ajout des en-tetes
    headers = ["#", "Titre", "Description", "Priorité", "Statut", "Date"]
    header_font = Font(bold=True, color="FFFFFF")
    fill = PatternFill(start_color="FF007BFF", end_color="FF007BFF", fill_type="solid")

    #positionnement des en-tetes
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.font = header_font
        cell.fill = fill
        cell.alignment = Alignment(horizontal="center")

    pannes = Panne.objects.all().order_by('-date_signalement')

    #ajout des declarations de pannes
    for row_num, panne in enumerate(pannes,2):
        ws.cell(row=row_num, column=1, value=row_num-1)
        ws.cell(row=row_num, column=2, value=panne.titre)
        ws.cell(row=row_num, column=3, value=panne.description)
        ws.cell(row=row_num, column=4, value=panne.priority)
        ws.cell(row=row_num, column=5, value=panne.status)
        ws.cell(row=row_num, column=6, value=panne.date_signalement.strftime('%Y-%m-%d %H:%M'))

    #redimensionnement des colonnes
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        if cell.value:
            if len(str(cell.value)) > max_length:
                max_length = len(str(cell.value))
        adjusted_width = (max_length + 8)
        ws.column_dimensions[column].width = adjusted_width

    # Réponse HTTP pour téléchargement
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="pannes.xlsx"'
    wb.save(response)
    return response


def charger_materiels(request):
    categorie_id = request.GET.get('categorie_materiel')
    materiels = Materiel.objects.filter(categorie_id=categorie_id).order_by('name')
    html = render_to_string('pannes/includes/option_materiels.html', {'materiels': materiels})
    return HttpResponse(html)