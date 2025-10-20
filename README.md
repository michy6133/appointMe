# AppointMe - Système de gestion de rendez-vous

Application Django pour la gestion de rendez-vous médicaux ou professionnels.

## Fonctionnalités

- **Authentification** : Connexion et inscription des utilisateurs
- **Tableau de bord** : Vue d'ensemble avec statistiques
- **Gestion des rendez-vous** : Création, modification, suppression
- **Gestion des clients** : Base de données des clients
- **Calendrier** : Vue calendaire des rendez-vous
- **Services** : Gestion des services proposés
- **Interface moderne** : Design responsive avec Tailwind CSS

## Installation

1. **Cloner le projet**
```bash
cd /home/mchy/projet/appointMe
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configurer la base de données**
```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

5. **Charger les données d'exemple (optionnel)**
```bash
python manage.py create_sample_data
```

6. **Lancer le serveur**
```bash
python manage.py runserver
```

## Accès à l'application

- **URL principale** : http://127.0.0.1:8000/
- **Interface d'administration** : http://127.0.0.1:8000/admin/
- **Compte par défaut** (si données d'exemple chargées) : admin/admin123

## Structure du projet

```
appointMe/
├── appointme_project/          # Configuration Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── appointments/               # Application principale
│   ├── models.py              # Modèles de données
│   ├── views.py               # Vues de l'application
│   ├── urls.py                # URLs de l'application
│   ├── admin.py               # Interface d'administration
│   ├── templates/             # Templates HTML
│   └── management/            # Commandes personnalisées
├── static/                    # Fichiers statiques
├── media/                     # Fichiers uploadés
└── requirements.txt           # Dépendances Python
```

## Modèles de données

- **Customer** : Clients
- **Service** : Services proposés
- **Appointment** : Rendez-vous
- **Staff** : Personnel
- **BusinessHours** : Heures d'ouverture
- **AppointmentReminder** : Rappels de rendez-vous

## Pages principales

1. **Login/Register** : Authentification
2. **Dashboard** : Tableau de bord avec statistiques
3. **Calendar** : Calendrier des rendez-vous
4. **Appointments** : Liste et gestion des rendez-vous
5. **Customers** : Gestion des clients

## Technologies utilisées

- **Backend** : Django 2.2.16
- **Frontend** : HTML5, Tailwind CSS, JavaScript
- **Base de données** : SQLite (par défaut)
- **Icônes** : Lucide Icons

## Développement

Pour contribuer au projet :

1. Créer une branche feature
2. Faire les modifications
3. Tester les changements
4. Créer une pull request

## Licence

Ce projet est sous licence MIT.
