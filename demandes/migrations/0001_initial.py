import decimal

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DemandeMatiere",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reference", models.CharField(blank=True, editable=False, max_length=20, null=True, unique=True, verbose_name="référence")),
                ("objet", models.CharField(max_length=200, verbose_name="objet")),
                ("district", models.CharField(max_length=120, verbose_name="district")),
                ("description", models.TextField(blank=True, verbose_name="description")),
                ("statut", models.CharField(choices=[("BROUILLON", "Brouillon"), ("EN_COURS", "En cours"), ("CLOTUREE", "Clôturée")], default="BROUILLON", max_length=20, verbose_name="statut")),
                ("cree_le", models.DateTimeField(auto_now_add=True, verbose_name="créée le")),
                ("modifiee_le", models.DateTimeField(auto_now=True, verbose_name="modifiée le")),
                ("createur", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="demandes_matiere", to=settings.AUTH_USER_MODEL, verbose_name="créateur")),
            ],
            options={
                "verbose_name": "demande de matières",
                "verbose_name_plural": "demandes de matières",
                "ordering": ["-cree_le"],
            },
        ),
        migrations.CreateModel(
            name="LigneDemande",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("designation", models.CharField(max_length=200, verbose_name="désignation")),
                ("quantite", models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(decimal.Decimal("0.01"))], verbose_name="quantité")),
                ("unite", models.CharField(blank=True, max_length=30, verbose_name="unité")),
                ("demande", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lignes", to="demandes.demandematiere", verbose_name="demande")),
            ],
            options={
                "verbose_name": "ligne de demande",
                "verbose_name_plural": "lignes de demande",
                "ordering": ["id"],
                "constraints": [models.CheckConstraint(condition=models.Q(("quantite__gt", 0)), name="quantite_strictement_positive")],
            },
        ),
    ]
