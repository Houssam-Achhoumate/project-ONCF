from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class DemandeMatiere(models.Model):
    class Statut(models.TextChoices):
        BROUILLON = "BROUILLON", "Brouillon"
        EN_COURS = "EN_COURS", "En cours"
        CLOTUREE = "CLOTUREE", "Clôturée"

    reference = models.CharField(
        "référence",
        max_length=20,
        unique=True,
        editable=False,
        null=True,
        blank=True,
    )
    objet = models.CharField("objet", max_length=200)
    district = models.CharField("district", max_length=120)
    description = models.TextField("description", blank=True)
    statut = models.CharField(
        "statut",
        max_length=20,
        choices=Statut.choices,
        default=Statut.BROUILLON,
    )
    createur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="créateur",
        related_name="demandes_matiere",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    cree_le = models.DateTimeField("créée le", auto_now_add=True)
    modifiee_le = models.DateTimeField("modifiée le", auto_now=True)

    class Meta:
        ordering = ["-cree_le"]
        verbose_name = "demande de matières"
        verbose_name_plural = "demandes de matières"

    def save(self, *args, **kwargs):
        doit_generer_reference = not self.reference
        super().save(*args, **kwargs)
        if doit_generer_reference:
            reference = f"DM-{timezone.localdate().year}-{self.pk:04d}"
            type(self).objects.filter(pk=self.pk).update(reference=reference)
            self.reference = reference

    def __str__(self):
        return f"{self.reference or 'Nouvelle DM'} — {self.objet}"


class LigneDemande(models.Model):
    demande = models.ForeignKey(
        DemandeMatiere,
        verbose_name="demande",
        related_name="lignes",
        on_delete=models.CASCADE,
    )
    designation = models.CharField("désignation", max_length=200)
    quantite = models.DecimalField(
        "quantité",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    unite = models.CharField("unité", max_length=30, blank=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "ligne de demande"
        verbose_name_plural = "lignes de demande"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantite__gt=0),
                name="quantite_strictement_positive",
            )
        ]

    def __str__(self):
        return f"{self.designation} ({self.quantite:g} {self.unite})".strip()
