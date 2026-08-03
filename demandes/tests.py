from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import DemandeMatiere, LigneDemande


class PrototypeDMTests(TestCase):
    def setUp(self):
        utilisateur = get_user_model()
        self.user = utilisateur.objects.create_user(
            username="district1",
            password="mot-de-passe-test",
            first_name="Agent",
            last_name="District",
        )
        self.autre_user = utilisateur.objects.create_user(
            username="district2",
            password="autre-mot-de-passe",
        )
        self.demande = DemandeMatiere.objects.create(
            objet="Outillage de maintenance",
            district="Rabat",
            description="Besoin pour une intervention planifiée.",
            statut=DemandeMatiere.Statut.BROUILLON,
            createur=self.user,
        )
        self.ligne = LigneDemande.objects.create(
            demande=self.demande,
            designation="Clé dynamométrique",
            quantite=Decimal("2"),
            unite="pièce",
        )

    def connecter(self, utilisateur=None):
        self.client.force_login(utilisateur or self.user)

    @staticmethod
    def donnees_demande(**surcharges):
        donnees = {
            "objet": "Équipements de signalisation",
            "district": "Casablanca",
            "description": "Demande urgente.",
            "statut": DemandeMatiere.Statut.EN_COURS,
            "lignes-TOTAL_FORMS": "1",
            "lignes-INITIAL_FORMS": "0",
            "lignes-MIN_NUM_FORMS": "1",
            "lignes-MAX_NUM_FORMS": "1000",
            "lignes-0-designation": "Lampe de signalisation",
            "lignes-0-quantite": "5",
            "lignes-0-unite": "pièce",
        }
        donnees.update(surcharges)
        return donnees

    def test_les_pages_metier_exigent_une_connexion(self):
        urls = [
            reverse("dashboard"),
            reverse("demande_creer"),
            reverse("demande_detail", args=[self.demande.pk]),
            reverse("demande_modifier", args=[self.demande.pk]),
            reverse("demande_supprimer", args=[self.demande.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                reponse = self.client.get(url)
                self.assertRedirects(reponse, f"{reverse('connexion')}?next={url}")

    def test_connexion_valide_et_invalide(self):
        invalide = self.client.post(
            reverse("connexion"),
            {"username": self.user.username, "password": "incorrect"},
        )
        self.assertEqual(invalide.status_code, 200)
        self.assertContains(invalide, "Identifiant ou mot de passe incorrect")

        valide = self.client.post(
            reverse("connexion"),
            {"username": self.user.username, "password": "mot-de-passe-test"},
        )
        self.assertRedirects(valide, reverse("dashboard"))

    def test_deconnexion_accepte_uniquement_post(self):
        self.connecter()
        self.assertEqual(self.client.get(reverse("deconnexion")).status_code, 405)
        self.assertRedirects(
            self.client.post(reverse("deconnexion")),
            reverse("connexion"),
        )

    def test_dashboard_affiche_compteurs_recherche_et_filtre(self):
        DemandeMatiere.objects.create(
            objet="Rails",
            district="Fès",
            statut=DemandeMatiere.Statut.CLOTUREE,
            createur=self.autre_user,
        )
        self.connecter()

        reponse = self.client.get(reverse("dashboard"))
        self.assertEqual(reponse.context["total"], 2)
        self.assertEqual(reponse.context["total_brouillon"], 1)
        self.assertEqual(reponse.context["total_cloturee"], 1)

        recherche = self.client.get(reverse("dashboard"), {"q": "Outillage"})
        self.assertEqual(list(recherche.context["demandes"]), [self.demande])

        filtre = self.client.get(
            reverse("dashboard"),
            {"statut": DemandeMatiere.Statut.CLOTUREE},
        )
        self.assertEqual(filtre.context["demandes"].count(), 1)
        self.assertEqual(
            filtre.context["demandes"].first().statut,
            DemandeMatiere.Statut.CLOTUREE,
        )

    def test_creation_valide_genere_reference_et_ligne(self):
        self.connecter()
        reponse = self.client.post(
            reverse("demande_creer"),
            self.donnees_demande(),
        )

        nouvelle = DemandeMatiere.objects.exclude(pk=self.demande.pk).get()
        self.assertRedirects(reponse, reverse("demande_detail", args=[nouvelle.pk]))
        self.assertRegex(nouvelle.reference, rf"^DM-\d{{4}}-{nouvelle.pk:04d}$")
        self.assertEqual(nouvelle.createur, self.user)
        self.assertEqual(nouvelle.lignes.count(), 1)
        self.assertEqual(nouvelle.lignes.get().designation, "Lampe de signalisation")

    def test_creation_refuse_une_demande_sans_ligne(self):
        self.connecter()
        donnees = self.donnees_demande(
            **{
                "lignes-0-designation": "",
                "lignes-0-quantite": "",
                "lignes-0-unite": "",
            }
        )
        avant = DemandeMatiere.objects.count()
        reponse = self.client.post(reverse("demande_creer"), donnees)

        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(DemandeMatiere.objects.count(), avant)
        self.assertTrue(reponse.context["lignes"].non_form_errors())

    def test_creation_refuse_une_quantite_nulle(self):
        self.connecter()
        donnees = self.donnees_demande(**{"lignes-0-quantite": "0"})
        avant = DemandeMatiere.objects.count()
        reponse = self.client.post(reverse("demande_creer"), donnees)

        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(DemandeMatiere.objects.count(), avant)
        self.assertTrue(reponse.context["lignes"].forms[0].errors["quantite"])

    def test_detail_affiche_demande_et_articles(self):
        self.connecter()
        reponse = self.client.get(reverse("demande_detail", args=[self.demande.pk]))
        self.assertContains(reponse, self.demande.reference)
        self.assertContains(reponse, self.demande.objet)
        self.assertContains(reponse, self.ligne.designation)

    def test_modification_met_a_jour_demande_et_lignes(self):
        self.connecter()
        donnees = self.donnees_demande(
            objet="Outillage modifié",
            statut=DemandeMatiere.Statut.CLOTUREE,
            **{
                "lignes-TOTAL_FORMS": "2",
                "lignes-INITIAL_FORMS": "1",
                "lignes-0-id": str(self.ligne.pk),
                "lignes-0-designation": "Clé dynamométrique renforcée",
                "lignes-0-quantite": "3",
                "lignes-0-unite": "pièce",
                "lignes-1-designation": "Gants",
                "lignes-1-quantite": "10",
                "lignes-1-unite": "paire",
            },
        )
        ancienne_date = self.demande.modifiee_le
        reponse = self.client.post(
            reverse("demande_modifier", args=[self.demande.pk]),
            donnees,
        )

        self.demande.refresh_from_db()
        self.assertRedirects(reponse, reverse("demande_detail", args=[self.demande.pk]))
        self.assertEqual(self.demande.objet, "Outillage modifié")
        self.assertEqual(self.demande.statut, DemandeMatiere.Statut.CLOTUREE)
        self.assertGreater(self.demande.modifiee_le, ancienne_date)
        self.assertEqual(self.demande.lignes.count(), 2)

    def test_suppression_est_confirmee_puis_effective(self):
        self.connecter()
        url = reverse("demande_supprimer", args=[self.demande.pk])
        confirmation = self.client.get(url)
        self.assertEqual(confirmation.status_code, 200)
        self.assertTrue(DemandeMatiere.objects.filter(pk=self.demande.pk).exists())

        reponse = self.client.post(url)
        self.assertRedirects(reponse, reverse("dashboard"))
        self.assertFalse(DemandeMatiere.objects.filter(pk=self.demande.pk).exists())
        self.assertFalse(LigneDemande.objects.filter(pk=self.ligne.pk).exists())

    def test_deux_utilisateurs_voient_la_meme_demande(self):
        self.connecter(self.autre_user)
        dashboard = self.client.get(reverse("dashboard"))
        detail = self.client.get(reverse("demande_detail", args=[self.demande.pk]))
        self.assertContains(dashboard, self.demande.reference)
        self.assertEqual(detail.status_code, 200)

    def test_suppression_sans_jeton_csrf_est_refusee(self):
        client_csrf = Client(enforce_csrf_checks=True)
        client_csrf.force_login(self.user)
        reponse = client_csrf.post(reverse("demande_supprimer", args=[self.demande.pk]))
        self.assertEqual(reponse.status_code, 403)
        self.assertTrue(DemandeMatiere.objects.filter(pk=self.demande.pk).exists())
