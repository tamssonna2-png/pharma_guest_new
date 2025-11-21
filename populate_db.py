"""import os
import django
from datetime import date, timedelta
import random

# Configuration Django - DOIT ÊTRE EN PREMIER
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ges_pha.settings')
django.setup()

# Les imports des modèles DOIVENT être APRÈS django.setup()
from django.contrib.auth.models import User
from tamsPh.models import Pharmacie, Medicament

def create_test_data():
    print("🧹 Nettoyage...")
    Medicament.objects.all().delete()
    Pharmacie.objects.all().delete()
    User.objects.filter(username='pharmacien_central').delete()  # Supprimer l'utilisateur aussi

    print("👤 Création utilisateur...")
    user, created = User.objects.get_or_create(
        username='pharmacien_central',
        defaults={
            'email': 'central@pharma.com',
            'first_name': 'Pierre',
            'last_name': 'Martin'
        }
    )
    if created:
        user.set_password('pharma123')
        user.save()

    print("🏥 Création pharmacies...")
    
    # Utiliser get_or_create pour la pharmacie aussi
    pharma, created = Pharmacie.objects.get_or_create(
        nom='Pharmacie Centrale',
        defaults={
            'address': '+221 33 123 45 67',
            'zone': '123 Rue Principale',
            'utilisateur': user
        }
    )
    
    if created:
        print("✅ Pharmacie Centrale créée")
    else:
        print("✅ Pharmacie Centrale déjà existante - mise à jour")
        # Mettre à jour les champs si nécessaire
        pharma.adresse = '123 Rue Principale'
        pharma.telephone = '+221 33 123 45 67'
        pharma.save()

# À la fin du fichier, vous devriez avoir :
if __name__ == "__main__":
    create_test_data()"""



import os
import django
from datetime import date, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ges_pha.settings')
django.setup()

from django.contrib.auth.models import User
from tamsPh.models import Pharmacie, Medicament

def create_test_data():
    print("🧹 Nettoyage...")
    Medicament.objects.all().delete()
    Pharmacie.objects.all().delete()
    
    print("👤 Création utilisateur...")
    user, created = User.objects.get_or_create(
        username='pharmacien_central',
        defaults={
            'email': 'central@pharma.com',
            'first_name': 'Pierre',
            'last_name': 'Martin'
        }
    )
    if created:
        user.set_password('pharma123')
        user.save()
    
    print("🏥 Création pharmacies...")
    pharmacies_data = [
        {
            'nom': 'Pharmacie Centrale',
            'address': '123 Avenue des Champs-Élysées, Paris',
            'zone': 'Centre-ville',
            'deGarde': True,
            'latitude': 48.8698,
            'longitude': 2.3078,
            'utilisateur': user
        }
    ]
    
    pharmacies = []
    for data in pharmacies_data:
        pharma = Pharmacie.objects.create(**data)
        pharmacies.append(pharma)
        print(f"✅ {pharma.nom} créée")
    
    print("💊 Création médicaments...")
    medicaments_data = [
        # Pharmacie Centrale
        {'nom': 'Paracétamol 500mg', 'categorie': 'Antidouleur', 'quantite': 45, 'prix': 2.50, 'description': 'Anti-douleur et anti-fièvre', 'pharmacie': pharmacies[0]},
        {'nom': 'Ibuprofène 400mg', 'categorie': 'Anti-inflammatoire', 'quantite': 32, 'prix': 3.20, 'description': 'Anti-inflammatoire non stéroïdien', 'pharmacie': pharmacies[0]},
        {'nom': 'Amoxicilline 1g', 'categorie': 'Antibiotique', 'quantite': 18, 'prix': 8.50, 'description': 'Antibiotique à large spectre', 'pharmacie': pharmacies[0]},
        {'nom': 'Ventoline', 'categorie': 'Respiratoire', 'quantite': 12, 'prix': 12.30, 'description': 'Traitement de lasthme', 'pharmacie': pharmacies[0]},
        {'nom': 'Doliprane 1000mg', 'categorie': 'Antidouleur', 'quantite': 8, 'prix': 4.20, 'description': 'Antalgique puissant', 'pharmacie': pharmacies[0]},
    ]
    
    for data in medicaments_data:
        medicament = Medicament.objects.create(**data)
        print(f"✅ {medicament.nom} - {medicament.quantite} unités")
    
    print("\n🎉 DONNÉES CRÉÉES AVEC SUCCÈS !")
    print(f"🏥 {Pharmacie.objects.count()} pharmacies")
    print(f"💊 {Medicament.objects.count()} médicaments")
    print(f"👤 Utilisateur: {user.username} (mdp: pharma123)")
    
    # Statistiques
    total_stock = sum(m.quantite for m in Medicament.objects.all())
    valeur_stock = sum(m.quantite * m.prix for m in Medicament.objects.all())
    print(f"📊 Stock total: {total_stock} unités")
    print(f"💰 Valeur estimée: {valeur_stock:.2f}€")

if __name__ == '__main__':
    create_test_data()