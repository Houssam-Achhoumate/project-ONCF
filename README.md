# Prototype — Suivi des Demandes de Matières ONCF

Petite application Django en français permettant à des utilisateurs connectés de consulter et de gérer un registre partagé de Demandes de Matières (DM).

## Fonctionnalités

- Connexion et déconnexion avec l’authentification Django.
- Tableau de bord avec compteurs, recherche et filtre par statut.
- Création, consultation, modification et suppression des DM.
- Ajout et suppression de lignes d’articles dans une DM.
- Administration Django des utilisateurs et des données.

## Installation sous Windows

Prérequis : Python 3.10 ou une version plus récente.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Ouvrir ensuite <http://127.0.0.1:8000/>, puis se connecter avec le compte créé.

## Tests

```powershell
python manage.py test
python manage.py check
python manage.py makemigrations --check --dry-run
```

## Routes principales

| Route | Fonction |
|---|---|
| `/connexion/` | Connexion |
| `/` | Tableau de bord |
| `/dm/nouvelle/` | Création d’une DM |
| `/dm/<id>/` | Détail d’une DM |
| `/dm/<id>/modifier/` | Modification |
| `/dm/<id>/supprimer/` | Confirmation de suppression |
| `/admin/` | Administration Django |

## Choix techniques

- Python, Django 5.2 LTS et SQLite.
- Templates Django rendus côté serveur.
- Bootstrap 5 chargé par CDN et styles locaux.
- JavaScript natif uniquement pour les lignes d’articles.

Ce prototype est prévu pour une exécution locale. Il n’inclut ni inscription publique, ni API REST, ni workflow métier multi-rôles.
