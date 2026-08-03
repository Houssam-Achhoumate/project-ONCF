from django.contrib import admin

from .models import DemandeMatiere, LigneDemande


class LigneDemandeInline(admin.TabularInline):
    model = LigneDemande
    extra = 0


@admin.register(DemandeMatiere)
class DemandeMatiereAdmin(admin.ModelAdmin):
    list_display = ("reference", "objet", "district", "statut", "createur", "cree_le")
    list_filter = ("statut", "district", "cree_le")
    search_fields = ("reference", "objet", "district", "description")
    readonly_fields = ("reference", "cree_le", "modifiee_le")
    inlines = [LigneDemandeInline]


@admin.register(LigneDemande)
class LigneDemandeAdmin(admin.ModelAdmin):
    list_display = ("designation", "quantite", "unite", "demande")
    search_fields = ("designation", "demande__reference")
