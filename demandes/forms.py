from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import DemandeMatiere, LigneDemande


class BootstrapFormMixin:
    def appliquer_bootstrap(self):
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"


class DemandeMatiereForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = DemandeMatiere
        fields = ["objet", "district", "description", "statut"]
        widgets = {
            "objet": forms.TextInput(attrs={"placeholder": "Ex. Matériel de maintenance"}),
            "district": forms.TextInput(attrs={"placeholder": "Ex. District de Rabat"}),
            "description": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Informations complémentaires (facultatif)"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.appliquer_bootstrap()


class LigneDemandeForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = LigneDemande
        fields = ["designation", "quantite", "unite"]
        widgets = {
            "designation": forms.TextInput(attrs={"placeholder": "Désignation de l’article"}),
            "quantite": forms.NumberInput(attrs={"min": "0.01", "step": "0.01"}),
            "unite": forms.TextInput(attrs={"placeholder": "Ex. pièce, kg, m"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.appliquer_bootstrap()


class BaseLigneDemandeFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        lignes_valides = 0
        for form in self.forms:
            if not hasattr(form, "cleaned_data") or form.cleaned_data.get("DELETE"):
                continue
            if form.cleaned_data.get("designation") and form.cleaned_data.get("quantite"):
                lignes_valides += 1

        if lignes_valides < 1:
            raise forms.ValidationError("Ajoutez au moins une ligne d’article valide.")


LigneDemandeFormSet = inlineformset_factory(
    DemandeMatiere,
    LigneDemande,
    form=LigneDemandeForm,
    formset=BaseLigneDemandeFormSet,
    fields=["designation", "quantite", "unite"],
    extra=0,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
