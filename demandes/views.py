from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DemandeMatiereForm, LigneDemandeFormSet
from .models import DemandeMatiere


@login_required
def dashboard(request):
    toutes_les_demandes = DemandeMatiere.objects.select_related("createur")
    demandes = toutes_les_demandes
    recherche = request.GET.get("q", "").strip()
    statut = request.GET.get("statut", "").strip()
    statuts_valides = {valeur for valeur, _ in DemandeMatiere.Statut.choices}

    if recherche:
        demandes = demandes.filter(
            Q(reference__icontains=recherche)
            | Q(objet__icontains=recherche)
            | Q(district__icontains=recherche)
        )
    if statut in statuts_valides:
        demandes = demandes.filter(statut=statut)
    else:
        statut = ""

    contexte = {
        "demandes": demandes,
        "recherche": recherche,
        "statut_actif": statut,
        "statuts": DemandeMatiere.Statut.choices,
        "total": toutes_les_demandes.count(),
        "total_brouillon": toutes_les_demandes.filter(
            statut=DemandeMatiere.Statut.BROUILLON
        ).count(),
        "total_en_cours": toutes_les_demandes.filter(
            statut=DemandeMatiere.Statut.EN_COURS
        ).count(),
        "total_cloturee": toutes_les_demandes.filter(
            statut=DemandeMatiere.Statut.CLOTUREE
        ).count(),
    }
    return render(request, "demandes/dashboard.html", contexte)


def _formulaire_demande(request, demande=None):
    est_creation = demande is None
    demande = demande or DemandeMatiere()

    if request.method == "POST":
        formulaire = DemandeMatiereForm(request.POST, instance=demande)
        lignes = LigneDemandeFormSet(
            request.POST,
            instance=demande,
            prefix="lignes",
        )
        if formulaire.is_valid() and lignes.is_valid():
            with transaction.atomic():
                demande = formulaire.save(commit=False)
                if est_creation:
                    demande.createur = request.user
                demande.save()
                lignes.instance = demande
                lignes.save()
            action = "créée" if est_creation else "modifiée"
            messages.success(request, f"La demande {demande.reference} a été {action}.")
            return redirect("demande_detail", pk=demande.pk)
    else:
        formulaire = DemandeMatiereForm(instance=demande)
        lignes = LigneDemandeFormSet(instance=demande, prefix="lignes")

    return render(
        request,
        "demandes/demande_form.html",
        {
            "formulaire": formulaire,
            "lignes": lignes,
            "demande": demande,
            "est_creation": est_creation,
        },
    )


@login_required
def demande_creer(request):
    return _formulaire_demande(request)


@login_required
def demande_modifier(request, pk):
    demande = get_object_or_404(DemandeMatiere, pk=pk)
    return _formulaire_demande(request, demande)


@login_required
def demande_detail(request, pk):
    demande = get_object_or_404(
        DemandeMatiere.objects.select_related("createur").prefetch_related("lignes"),
        pk=pk,
    )
    return render(request, "demandes/demande_detail.html", {"demande": demande})


@login_required
def demande_supprimer(request, pk):
    demande = get_object_or_404(DemandeMatiere, pk=pk)
    if request.method == "POST":
        reference = demande.reference
        demande.delete()
        messages.success(request, f"La demande {reference} a été supprimée.")
        return redirect("dashboard")
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET", "POST"])
    return render(
        request,
        "demandes/demande_confirm_delete.html",
        {"demande": demande},
    )
