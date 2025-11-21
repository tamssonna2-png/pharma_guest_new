from django.db import models
from django.conf import settings
from typing import List, Dict, Any
from django.contrib.auth.models import User
# Create your models here.
class Medicament(models.Model):
    #id_medicament = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=280)
    categorie = models.CharField(max_length=280)
    description = models.CharField(max_length=280)
    quantite = models.IntegerField()
    prix = models.IntegerField()
    image = models.ImageField(upload_to='medicament/', null=True, blank=True)
    pharmacie = models.ForeignKey('Pharmacie', on_delete=models.CASCADE)
def __str__(self):
    return self.nom

class Specialiste(models.Model):
    #id_specialiste = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=280)
    specialite = models.CharField(max_length=280)
    Disponible =models.BooleanField(default=False)

def __str__(self):
    return self.nom

class MonIA(models.Model):
    TYPE_CONVERSATION_CHOICES = [
        ('stock', 'Gestion de Stock'),
        ('conseil', 'Conseil Client'), 
        ('analyse', 'Analyse et Statistiques'),
        ('general', 'Question Générale'),
        ('urgence', 'Situation d\'Urgence'),
        ('autre', 'pour d\'autre questions ou preoccupation'),  # ✅ Très bien !
    ]
    Pharmacie=models.ForeignKey('Pharmacie',on_delete=models.CASCADE,related_name='mon_ia')
    message =models.TextField()
    reponse =models.TextField()
    timestamp=models.DateTimeField(auto_now_add=True)#à quoi ca sert?
    type_conversation =models.CharField(max_length=50,choices=TYPE_CONVERSATION_CHOICES,default='general',verbose_name="Type de Conversation")

class Pharmacie(models.Model):
    #id_pharmacie = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=280)
    address = models.CharField(max_length=280)
    zone = models.CharField(max_length=280)
    deGarde = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

def __str__(self):
    return self.nom 

import math
import requests
from typing import List, Dict, Any
# Rayon de la Terre en kilomètres (utilisé dans la formule de Haversine)
R = 6371 

def calculer_distance(lat1, lon1, lat2, lon2):
    """
    Calcule la distance entre deux points GPS en utilisant la formule de Haversine (en km).
    """
    # ... (le corps de la fonction de calcul de distance) ...
    lon1_rad, lat1_rad, lon2_rad, lat2_rad = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def trouver_pharmacies_les_plus_proches(user_lat: float, user_lon: float, max_distance_km: float,choice:int=1) -> dict:
    """
    Recherche les pharmacies les plus proches (de garde et toutes) dans la base de données locale
    en utilisant les coordonnées de l'utilisateur et la formule de Haversine.
    """
    toutes_les_pharmacies = Pharmacie.objects.all()#.exclude(latitude__isnull=True)
    resultats_avec_distance = []
    if choice==1:
        for pharmacie in toutes_les_pharmacies:
            if pharmacie.latitude is not None and pharmacie.longitude is not None:
                distance = calculer_distance(
                    user_lat, user_lon, 
                    pharmacie.latitude, pharmacie.longitude
                 )
                if distance <= max_distance_km:
                    resultats_avec_distance.append({
                        'pharmacie': pharmacie,
                        'distance_km': round(distance, 2)
                 })
        
        resultats_avec_distance.sort(key=lambda x: x['distance_km'])
        
        toutes_proches = resultats_avec_distance
        de_garde_proches = [r for r in resultats_avec_distance if r['pharmacie'].deGarde]
        return {
            'toutes_proches': toutes_proches,
            'de_garde_proches': de_garde_proches,
         }
    else:
        OVERPASS_URL = "http://overpass-api.de/api/interpreter"
        query = f"""
        [out:json][timeout:25];
        (
        node["amenity"="pharmacy"](around:{max_distance_km * 1000}, {user_lat}, {user_lon});
        way["amenity"="pharmacy"](around:{max_distance_km* 1000}, {user_lat}, {user_lon});
        );
        out center;
        """
    
        try:
            response = requests.post(OVERPASS_URL, data={'data': query})
            response.raise_for_status() 
            data = response.json()
        
            pharmacies = []
            for element in data.get('elements', []):
            
                # Utiliser la latitude/longitude du centre si c'est un 'way'
                lat = element.get('lat') if element.get('lat') else element['center']['lat']
                lon = element.get('lon') if element.get('lon') else element['center']['lon']
            
                pharmacies.append({
                'nom': element['tags'].get('name', 'Pharmacie (Nom non spécifié)'),
                'lat': lat,
                'lon': lon,
                'adresse_complete': element['tags'].get('addr:full', element['tags'].get('addr:street', 'Adresse non disponible')),
                'deGarde': 'Inconnu (API gratuite)',
                 'distance':calculer_distance(user_lat,user_lon,lat,lon) # Toujours impossible à déterminer via OSM
                })
            """for pharmacie in pharmacies:
                print(pharmacie['distance'])"""
            pharmacies=sorted(pharmacies,key=lambda x:x['distance'])
            return pharmacies
        
        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion à l'API Overpass : {e}")
            return []
       
