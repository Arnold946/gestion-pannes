
from django import forms

from materiels.models import Materiel, CategorieMateriel
from pannes.models import AffectationPanne, Panne


class PanneForm(forms.ModelForm):
    class Meta:
        model = Panne
        fields = ['titre','description', 'priority','categorie_materiel', 'materiel']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'priority': forms.Select(),
            'materiel': forms.Select(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categorie_materiel'].queryset = CategorieMateriel.objects.all()
        self.fields['materiel'].queryset = Materiel.objects.none()
        if 'categorie_materiel' in self.data:
            try:
                categorie_id = int(self.data.get('categorie_materiel'))
                self.fields['materiel'].queryset = Materiel.objects.filter(categorie_id=categorie_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.materiel:
            self.fields['materiel'].queryset = Materiel.objects.filter(
                categorie=self.instance.materiel.categorie).order_by('name')

class AffectationPanneForm(forms.ModelForm):
    class Meta:
        model = AffectationPanne
        fields = ['panne','technicien']
        widgets = {
            'panne': forms.Select(),
            'technicien': forms.Select(),
        }