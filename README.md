Site E-Commerce Django

Un site e-commerce complet développé avec Django. Il permet aux utilisateurs de s'inscrire en tant que client ou d'accéder à l'administration pour gérer les produits.

Principales fonctionnalités

- Authentification : inscription, connexion, déconnexion.
- Rôles :
  - Client: peut consulter les produits.
  - Admin: peut ajouter, modifier et supprimer des produits.
- Interface d’administration sécurisée.
- Affichage dynamique des produits.
- Interface frontend intégrée (100% Django, sans React ni frameworks externes).

 Technologies utilisées

- Django (backend + frontend)
- Python 3.x
- HTML/CSS (via Django templates)
- SQLite (ou PostgreSQL/MySQL selon la config)

## 🚀 Installation (en local)

1. Cloner le projet
   bash
   git clone https://github.com/BlueEagleTech/e_commerce.git
   cd nom-du-repo
2. python -m venv env
source env/bin/activate  # Linux/macOS
env\Scripts\activate     # Windows
3. pip install -r requirements.txt
4. python manage.py migrate
5. python manage.py runserver

