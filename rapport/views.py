from django.shortcuts import render

# Create your views here.
def rapports_synthese(request):
    return render(request, 'rapport/rapport_synthese.html')

def rapports_detaille(request):
    return render(request, 'rapport/rapport_detaille.html')

def rapports_statistique(request):
    return render(request, 'rapport/rapport_statistique.html')

def rapports_performance(request):
    return render(request, 'rapport/rapport_performance.html')

def rapports_maintenance(request):
    return render(request, 'rapport/rapport_maintenance.html')