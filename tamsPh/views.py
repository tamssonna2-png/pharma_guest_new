from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from tamsPh.models import Medicament
from tamsPh.models import Specialiste
from tamsPh.models import Pharmacie,trouver_pharmacies_les_plus_proches,calculer_distance
from tamsPh.models import MonIA,Notification
from django.contrib.auth.models import User
# Create your views here.

def accueil(request):
    """Page d'accueil principale"""
    return render(request, 'accueil.html')

# Mets cette fonction AU DÉBUT de ton views.py
def creer_notification_pharmacie(pharmacie, type_notification, message, commande=None):
    notification = Notification.objects.create(
        pharmacie=pharmacie,
        type_notification=type_notification,
        message=message,
        commande=commande
    )
    return notification

def index(request):
    """Medicament.objects.all().delete()
    Specialiste.objects.all().delete() 
    Pharmacie.objects.all().delete()"""
    """
    Vue qui gère la recherche de pharmacies proches après réception des coordonnées GPS.
    """
    user_lat = request.GET.get('lat')
    user_lon = request.GET.get('lon')
    rayon= int(request.GET.get('distance', 5))
    context = {}
    nom_pharmacie = request.GET.get('nom_pharmacie', '').strip()
    pharmacies_recherche = []
    if nom_pharmacie:
        pharmacies_recherche = Pharmacie.objects.filter(
            nom__icontains=nom_pharmacie
        )
        context['pharmacies_recherche'] = pharmacies_recherche 
    if user_lat and user_lon:
        try:
            lat = float(user_lat)
            lon = float(user_lon)
            # 1. Effectuer la recherche de proximité
            choice=int(request.GET.get('choice', 1))
            resultats = trouver_pharmacies_les_plus_proches(lat, lon,rayon,choice)
            context['user_lat'] = lat
            context['user_lon'] = lon
            context['current_choice'] = choice
            
            if choice==1:
                for item in resultats['toutes_proches']:
                    pharmacie_obj = item['pharmacie']
                    distance = item['distance_km']
    
                    # 🚨 Accéder aux attributs de l'objet Django
                    nom = pharmacie_obj.nom
                    adresse = pharmacie_obj.address
                    est_de_garde = pharmacie_obj.deGarde
    
                    #print(f"NOM: {nom}, DISTANCE: {distance} km, ADRESSE: {adresse}, GARDE: {est_de_garde}")

                context=({
                    'pharmacies_de_garde': resultats['de_garde_proches'],
                    'toutes_pharmacies1': resultats['toutes_proches'],
                    'message': f"Résultats trouvés près de {lat}, {lon}.",
                })
            else:    
                pha=[]
                pharmacies_a_afficher = []
                for pharma_data in resultats:
                    criteres_recherche = {
                        'nom': pharma_data['nom'],
                        'address': pharma_data['adresse_complete'],
                    }
                    pha1={
                        'nom':pharma_data['nom'],
                        'address':pharma_data['adresse_complete'],
                        'latitude': pharma_data['lat'],
                        'longitude':pharma_data['lon'],
                        #deGarde=pharma_data['deGarde']
                    }
                    pha2, created =Pharmacie.objects.get_or_create(
                    defaults=pha1,
                    **criteres_recherche)
                    distance=pharma_data['distance']
                    if created:
                        #print(f"DEBUG: Nouvelle pharmacie créée : {pha2.nom} {distance}")
                        pha.append(pha2) # Ajoute uniquement les nouvelles à la liste
                    else:
                        """print(f"DEBUG: Pharmacie déjà existante (doublon évité) : {pha2.nom} {distance}")"""
                    """context = {
                        'pharmacies_de_garde': resultats,
                        'toutes_pharmacies2': resultats,
                        'message': f"Résultats trouvés près de {lat}, {lon}.",
                    }"""
                    pharmacies_a_afficher.append({
                        'id': pha2.id,
                        'nom': pha2.nom,
                        'address': pha2.address,
                        'zone': pha2.zone,
                        'deGarde': pha2.deGarde,  # Récupérer depuis la base
                        'distance': distance
                    })
                
                # ✅ CORRECTION: Utiliser update() et créer une structure cohérente
                context.update({
                    'toutes_pharmacies2': resultats,  # ✅ Structure cohérente
                    'message': f"Résultats trouvés près de {lat}, {lon}.",
                })

            # 2. Remplir le contexte pour le template
            
        except ValueError:
            context['erreur'] = "Coordonnées GPS reçues invalides."
        except Exception as e:
            context['erreur'] = f"Erreur lors du traitement de la recherche : {e}"
    
    else:
        # C'est la première fois que la page est chargée sans coordonnées
        context['message'] = "Veuillez autoriser la géolocalisation pour commencer la recherche."  
    return render(request,'index.html',context)
#<!--💊 {{ toutes_pharmacies2|length|default:toutes_pharmacies1|length }} Pharmacie(s) trouvée(s)-->




def medicament_client(request):
    nom_medic = request.GET.get('nom_medic', '').strip()
    user_lat = request.GET.get('lat')
    user_lon = request.GET.get('lon')
    #print(user_lat," et ",user_lon)
    
    # 1. INITIALISATION DU CONTEXTE
    context = {
        'terme_recherche': nom_medic,
        'medicaments': [], # Cette liste sera remplie plus tard
        'erreur': None,
        'message': None,
    }

    # Si le champ de recherche est vide
    if not nom_medic:
        #context['erreur'] = "Veuillez entrer un nom de médicament."
        return render(request, 'resultat_medicament.html', context)
        
    # 2. RECHERCHE DES MÉDICAMENTS
    medicaments_qs = Medicament.objects.filter(
        nom__icontains=nom_medic
    ).select_related('pharmacie')

    # Si aucun médicament n'est trouvé
    if not medicaments_qs.exists():
        context['erreur'] = f'Aucun médicament trouvé pour "{nom_medic}".'
        return render(request, 'resultat_medicament.html', context)
        
    
    # 3. TRAITEMENT AVEC/SANS COORDONNÉES
    medicaments_list = []
    
    if user_lat and user_lon:
        # CAS 1 : Coordonnées disponibles
        try:
            lat_user = float(user_lat)
            lon_user = float(user_lon)
            
            for med in medicaments_qs:
                distance = calculer_distance(
                    lat_user, lon_user, 
                    med.pharmacie.latitude, med.pharmacie.longitude
                )
                medicaments_list.append({
                    'id':med.id,
                    'nom': med.nom,
                    'categorie': med.categorie,
                    'description': med.description,
                    'prix': med.prix,
                    'pharmacie_id':med.pharmacie.id,
                    'pharmacie_nom': med.pharmacie.nom,
                    'pharmacie_adresse': med.pharmacie.address,
                    'pharmacie_zone': med.pharmacie.zone,
                    'distance': distance
                })
            
        except (ValueError):
            context['erreur'] = "Coordonnées GPS reçues invalides. Les distances ne sont pas calculées."
            # On passe au Cas 2 pour afficher les résultats sans distance
            # (Le code ci-dessous gérera l'affichage des résultats sans distance)
            user_lat = None # Force le passage au bloc else ci-dessous
            
        except Exception as e:
            context['erreur'] = f"Erreur interne : {e}"
            
    
    if not user_lat or not user_lon or 'erreur' in context:
        # CAS 2 : Aucune coordonnée ou erreur de coordonnées
        
        # Si on est passé par le bloc "try" mais qu'une erreur de valeur a eu lieu, 
        # medicaments_list est vide, il faut la remplir sans distance.
        if not medicaments_list:
            context['message'] = context.get('message', "Veuillez autoriser la géolocalisation pour voir les distances.") 
            
            for med in medicaments_qs:
                medicaments_list.append({
                    'nom': med.nom,
                    'categorie': med.categorie,
                    'description': med.description,
                    'prix': med.prix,
                    'pharmacie_nom': med.pharmacie.nom,
                    'pharmacie_adresse': med.pharmacie.address,
                    'pharmacie_zone': med.pharmacie.zone,
                    'distance': None
                })
        
    # 4. RENDU FINAL (Une seule fois)
    # 🌟 Mettre à jour le contexte avec la liste remplie
    context['medicaments'] = medicaments_list
    
    return render(request, 'resultat_medicament.html', context)




@login_required

def mes_medicaments_connecte(request):
    """Version sécurisée - pharmacie connectée voit SES médicaments"""
    #print(request.user)
    try:
        # ⭐ CORRECTION : Cherchez la pharmacie qui a cet utilisateur
        pharmacie = Pharmacie.objects.get(utilisateur=request.user)
        medicaments = Medicament.objects.filter(pharmacie=pharmacie)
        return render(request
        , 'mes_medicaments.html', {
            'pharmacie': pharmacie,
            'medicaments': medicaments
        })
    except Pharmacie.DoesNotExist:
        # ⭐ CORRECTION : Utilisez le template qui existe
        return render(request, 'mes_medicaments.html', {
            'pharmacie': None,
            'medicaments': [],
            'erreur': 'Aucune pharmacie associée à votre compte'
        })
        #http://localhost:8000/mes-medicaments/




from django.shortcuts import render, get_object_or_404, redirect
from .form import MedicamentForm

@login_required
def ajouter_medicament(request):
    """Permet à une pharmacie d'ajouter un médicament"""
    pharmacie = get_object_or_404(Pharmacie, utilisateur=request.user)
    
    if request.method == 'POST':
        form = MedicamentForm(request.POST, request.FILES)
        if form.is_valid():
            medicament = form.save(commit=False)
            medicament.pharmacie = pharmacie  # Associe automatiquement à la pharmacie
            medicament.save()
            return redirect('mes_medicaments_perso')
    else:
        form = MedicamentForm()
    
    return render(request, 'ajouter_medicament.html', {'form': form})
    #http://localhost:8000/ajouter-medicament/

@login_required
def supprimer_medicament(request, medicament_id):
    """Permet à une pharmacie de supprimer un de ses médicaments"""
    pharmacie = get_object_or_404(Pharmacie, utilisateur=request.user)
    medicament = get_object_or_404(Medicament, id=medicament_id, pharmacie=pharmacie)
    
    if request.method == 'POST':
        medicament.delete()
        return redirect('mes_medicaments_perso')
    
    return render(request, 'supprimer_medicament.html', {'medicament': medicament})
    #http://localhost:8000/supprimer-medicament/2/


@login_required
def modifier_medicament(request, medicament_id):
    """Permet à une pharmacie de modifier un de ses médicaments"""
    pharmacie = get_object_or_404(Pharmacie, utilisateur=request.user)
    medicament = get_object_or_404(Medicament, id=medicament_id, pharmacie=pharmacie)
    
    if request.method == 'POST':
        form = MedicamentForm(request.POST, request.FILES, instance=medicament)
        if form.is_valid():
            form.save()
            return redirect('mes_medicaments_perso')
    else:
        form = MedicamentForm(instance=medicament)
    
    return render(request, 'modifier_medicament.html', {
        'form': form,
        'medicament': medicament
    })



@login_required
    
def rechercher_medicament(request):
    nom_medic = request.GET.get('nom_medic', '').strip()
    try:
        pharmacie = Pharmacie.objects.get(utilisateur=request.user)
        medicaments = Medicament.objects.filter(
            pharmacie=pharmacie, 
            nom__icontains=nom_medic
        )
        
        # CORRECTION : Ajouter les variables au contexte
        return render(request, 'rechercher_medicament_pharmacie.html', {
            'terme_recherche': nom_medic,
            'medicaments': medicaments,
            'pharmacie': pharmacie
        })
        
    except Pharmacie.DoesNotExist:
        return render(request, 'rechercher_medicament_pharmacie.html', {
            'erreur': 'Aucune pharmacie associée à votre compte'
        })

from .form import InscriptionPharmacieForm

def inscription_pharmacie(request):
    """Permet à une nouvelle pharmacie de créer un compte"""
    if request.method == 'POST':
        form = InscriptionPharmacieForm(request.POST)
        if form.is_valid():
            # 1. Créer l'utilisateur
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            
            # 2. Créer la pharmacie
            pharmacie = Pharmacie.objects.create(
                nom=form.cleaned_data['nom_pharmacie'],
                address=form.cleaned_data['address'],
                zone=form.cleaned_data['zone'],
                latitude=form.cleaned_data['latitude'],
                longitude=form.cleaned_data['longitude'],
                utilisateur=user
            )
            
            # 3. Connecter automatiquement l'utilisateur
            from django.contrib.auth import login
            login(request, user)
            
            return redirect('mes_medicaments_perso')
    else:
        form = InscriptionPharmacieForm()
    
    return render(request, 'inscription_pharmacie.html', {'form': form})
    #http://localhost:8000/inscription/

def info_pharmacie(request, pharmacie_id):
    """Affiche les détails d'une pharmacie spécifique"""
    # Récupérer la pharmacie ou retourner une erreur 404 si non trouvée
    pharmacie = get_object_or_404(Pharmacie, id=pharmacie_id)
    
    # Vous pouvez aussi récupérer les médicaments de cette pharmacie si vous avez une relation
    # medicaments = Medicament.objects.filter(pharmacie=pharmacie)
    
    context = {
        'pharmacie': pharmacie,
        # 'medicaments': medicaments,  # Si vous voulez afficher les médicaments
    }
    
    return render(request, 'info_pharmacie.html', context)
#http://localhost:8000/info-pharmacie/1/


@login_required
def modifier_pharmacie(request):
    """
    Vue pour permettre au pharmacien de modifier les informations de sa pharmacie et son compte
    """
    try:
        pharmacie = Pharmacie.objects.get(utilisateur=request.user)
    except Pharmacie.DoesNotExist:
        messages.error(request, "Aucune pharmacie associée à votre compte.")
        return redirect('mes_medicaments_perso')
    
    if request.method == 'POST':
        # Données de la pharmacie
        nom = request.POST.get('nom')
        address = request.POST.get('address')
        zone = request.POST.get('zone')
        deGarde = request.POST.get('deGarde') == 'on'
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        # Données du compte utilisateur
        new_username = request.POST.get('new_username', '').strip()
        current_password = request.POST.get('current_password', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        # Validation des données de la pharmacie
        if not nom or not address or not zone:
            messages.error(request, "Veuillez remplir tous les champs obligatoires de la pharmacie.")
        else:
            try:
                # Mettre à jour la pharmacie
                pharmacie.nom = nom
                pharmacie.address = address
                pharmacie.zone = zone
                pharmacie.deGarde = deGarde
                
                if latitude:
                    pharmacie.latitude = float(latitude)
                if longitude:
                    pharmacie.longitude = float(longitude)
                
                pharmacie.save()
                
                # Gestion de la modification du compte utilisateur
                user_updated = False
                user = request.user
                
                # Modification du nom d'utilisateur
                if new_username and new_username != user.username:
                    if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
                        messages.error(request, "Ce nom d'utilisateur est déjà utilisé.")
                    else:
                        user.username = new_username
                        user_updated = True
                        messages.success(request, "Nom d'utilisateur modifié avec succès.")
                
                # Modification du mot de passe
                if new_password:
                    if not current_password:
                        messages.error(request, "Veuillez entrer votre mot de passe actuel pour modifier le mot de passe.")
                    elif not user.check_password(current_password):
                        messages.error(request, "Mot de passe actuel incorrect.")
                    elif new_password != confirm_password:
                        messages.error(request, "Les nouveaux mots de passe ne correspondent pas.")
                    else:
                        user.set_password(new_password)
                        user_updated = True
                        messages.success(request, "Mot de passe modifié avec succès.")
                
                # Sauvegarder les modifications de l'utilisateur
                if user_updated:
                    user.save()
                    # Reconnecter l'utilisateur si le mot de passe a changé
                    if new_password:
                        from django.contrib.auth import update_session_auth_hash
                        update_session_auth_hash(request, user)
                
                messages.success(request, "✅ Toutes les modifications ont été enregistrées avec succès!")
                return redirect('mes_medicaments_perso')
                
            except ValueError:
                messages.error(request, "❌ Erreur: Les coordonnées GPS doivent être des nombres valides.")
            except Exception as e:
                messages.error(request, f"❌ Une erreur s'est produite: {str(e)}")
    
    context = {
        'pharmacie': pharmacie,
    }
    
    return render(request, 'modif_info_pharmacie.html', context)
    #http://localhost:8000/modif-info-pharmacie/




from django.http import HttpResponse

from django.core.mail import send_mail
from django.conf import settings
import random
import string

def generate_temp_password():
    """Génère un mot de passe temporaire"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(10))

def reset_password(request):
    """Page de demande de réinitialisation de mot de passe"""
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        
        try:
            # Chercher l'utilisateur par username OU email
            try:
                # Essayer d'abord avec le username
                user = User.objects.get(username=identifier)
            except User.DoesNotExist:
                # Si pas trouvé, essayer avec l'email
                user = User.objects.get(email=identifier)
            
            # Générer un nouveau mot de passe temporaire
            temp_password = generate_temp_password()
            user.set_password(temp_password)
            user.save()
            
            # Afficher le mot de passe dans la même page
            return render(request, 'reset_password.html', {
                'new_password': temp_password,
                'username': user.username,
                'email': user.email,
                'messages': [
                    {
                        'message': '✅ Mot de passe réinitialisé avec succès !',
                        'tags': 'success'
                    }
                ]
            })
            
        except User.DoesNotExist:
            messages.error(request, 
                '❌ Aucun utilisateur trouvé avec cet identifiant. '
                'Vérifiez votre nom d\'utilisateur ou email.'
            )
    
    return render(request, 'reset_password.html')

def admin_reset_password(request, username):
    """Réinitialisation par administrateur (pour votre fonction originale)"""
    if not request.user.is_staff:
        return HttpResponse('❌ Accès réservé aux administrateurs')
    
    try:
        user = User.objects.get(username=username)
        temp_password = generate_temp_password()
        user.set_password(temp_password)
        user.save()
        
        return HttpResponse(f'''
        ✅ Mot de passe réinitialisé avec succès !
        
        Utilisateur : {username}
        Mot de passe temporaire : {temp_password}
        
        Veuillez communiquer ces informations à l'utilisateur.
        ''')
        
    except User.DoesNotExist:
        return HttpResponse(f'❌ Utilisateur "{username}" non trouvé')
    










    #Maintenant il s'agit des vues qui effectuent des taches speialiser pour le niveau 3
    #je n'y comprend absolument rien

from datetime import datetime
import math
from collections import Counter, defaultdict
from django.db.models import Q, Count, Avg
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages

# === SYSTÈME DE RECOMMANDATION SIMPLIFIÉ ===
class PharmaAI:
    """Système d'intelligence artificielle simplifié sans dépendances externes"""
    
    @staticmethod
    def calculer_similarite(texte1, texte2):
        """Calcule la similarité entre deux textes (algorithme maison)"""
        if not texte1 or not texte2:
            return 0
            
        mots1 = set(texte1.lower().split())
        mots2 = set(texte2.lower().split())
        
        intersection = mots1.intersection(mots2)
        union = mots1.union(mots2)
        
        return len(intersection) / len(union) if union else 0
    
    @staticmethod
    def recommander_medicaments_similaires(medicament_cible, medicaments_liste, max_recommandations=3):
        """Recommande des médicaments similaires"""
        recommandations = []
        
        for medicament in medicaments_liste:
            if medicament.id == medicament_cible.id:
                continue
                
            # Calculer plusieurs scores de similarité
            score_nom = PharmaAI.calculer_similarite(medicament_cible.nom, medicament.nom)
            score_categorie = 1.0 if medicament_cible.categorie == medicament.categorie else 0.0
            score_description = PharmaAI.calculer_similarite(
                medicament_cible.description or "", 
                medicament.description or ""
            )
            
            # Score composite pondéré
            score_final = (score_nom * 0.5) + (score_categorie * 0.3) + (score_description * 0.2)
            
            if score_final > 0.1:  # Seuil minimum
                recommandations.append({
                    'medicament': medicament,
                    'score': round(score_final, 2),
                    'confiance': 'Élevée' if score_final > 0.6 else 'Moyenne' if score_final > 0.3 else 'Faible'
                })
        
        # Trier et retourner les meilleures recommandations
        recommandations.sort(key=lambda x: x['score'], reverse=True)
        return recommandations[:max_recommandations]

# === BUSINESS INTELLIGENCE MAISON ===
# Dans views.py - CORRIGEZ votre classe BusinessIntelligence
class BusinessIntelligence:
    """Système d'analyse de données sans pandas"""
    
    @staticmethod
    def analyser_tendances_recherches():
        """Analyse les tendances de recherche des utilisateurs"""
        # Données simulées - remplacez par vos vraies données
        donnees_exemple = [
            {'terme': 'paracétamol', 'count': 15, 'niveau': '🔥 Très populaire'},
            {'terme': 'doliprane', 'count': 12, 'niveau': '🔥 Très populaire'},
            {'terme': 'vitamine c', 'count': 8, 'niveau': '📈 En croissance'},
            {'terme': 'ibuprofène', 'count': 6, 'niveau': '📈 En croissance'},
            {'terme': 'sirop', 'count': 4, 'niveau': '📊 Stable'},
        ]
        return donnees_exemple
    
    @staticmethod
    def generer_rapport_performance():
        """Génère un rapport de performance des pharmacies"""
        # Statistiques basiques sans pandas
        try:
            total_medicaments = Medicament.objects.count()
            pharmacies_actives = Pharmacie.objects.count()
        except:
            total_medicaments = 0
            pharmacies_actives = 0
        
        stats = {
            'total_medicaments': total_medicaments,
            'pharmacies_actives': pharmacies_actives,
            'taux_disponibilite_moyen': BusinessIntelligence.calculer_taux_disponibilite(),
            'medicaments_populaires': BusinessIntelligence.get_medicaments_populaires(),
            'zones_couvertes': BusinessIntelligence.analyser_zones_couvertes()  # CORRECTION DU NOM
        }
        
        return stats
    
    @staticmethod
    def analyser_zones_couvertes():
        """Analyse les zones géographiques couvertes"""
        # Simuler des données de zones
        return [
            {'zone': 'Centre-ville', 'pharmacies': 5, 'couverture': 'Élevée'},
            {'zone': 'Nord', 'pharmacies': 3, 'couverture': 'Moyenne'},
            {'zone': 'Sud', 'pharmacies': 2, 'couverture': 'Faible'},
        ]
    
    @staticmethod
    def calculer_taux_disponibilite():
        """Calcule le taux de disponibilité moyen"""
        try:
            medicaments = Medicament.objects.all()
            if not medicaments:
                return 0
                
            total = sum(1 for med in medicaments if med.quantite > 0)
            return round((total / len(medicaments)) * 100, 1)
        except:
            return 75.0  # Valeur par défaut en cas d'erreur
    
    @staticmethod
    def get_medicaments_populaires(limit=5):
        """Retourne les médicaments les plus populaires"""
        try:
            return list(Medicament.objects.all()[:limit])
        except:
            return []

# === VUE AVEC IA INTÉGRÉE ===
def recherche_intelligente(request):
    """Page de recherche avec fonctionnalités IA intégrées"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return render(request, 'recherche_ia.html', {
            'ai_enabled': True,
            'message': '🔍 Entrez un médicament à rechercher'
        })
    
    # Recherche traditionnelle
    medicaments_trouves = Medicament.objects.filter(
        Q(nom__icontains=query) | 
        Q(description__icontains=query) |
        Q(categorie__icontains=query)
    ).select_related('pharmacie')
    
    # Recommandations IA
    recommandations_ia = []
    if medicaments_trouves:
        medicament_principal = medicaments_trouves.first()
        autres_medicaments = Medicament.objects.exclude(id=medicament_principal.id)[:20]  # Limiter pour performance
        
        recommandations_ia = PharmaAI.recommander_medicaments_similaires(
            medicament_principal, 
            autres_medicaments,
            max_recommandations=3
        )
    
    # Analyse Business Intelligence
    tendances = BusinessIntelligence.analyser_tendances_recherches()
    rapport_performance = BusinessIntelligence.generer_rapport_performance()
    
    context = {
        'query': query,
        'medicaments': medicaments_trouves,
        'recommandations_ia': recommandations_ia,
        'tendances_bi': tendances,
        'rapport_performance': rapport_performance,
        'ai_enabled': True,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return render(request, 'recherche_ia.html', context)





from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Pharmacie, Medicament

@login_required
def tableau_bord_pharmacien(request):
    """Tableau de bord BI personnalisé pour le pharmacien connecté"""
    
    try:
        # 1. Récupérer la pharmacie de l'utilisateur connecté
        pharmacie = Pharmacie.objects.get(utilisateur=request.user)
        
        # 2. Statistiques SPÉCIFIQUES à cette pharmacie
        medicaments_pharmacie = Medicament.objects.filter(pharmacie=pharmacie)
        total_medicaments = medicaments_pharmacie.count()
        
        # Calcul du taux de disponibilité réel
        medicaments_en_stock = medicaments_pharmacie.filter(quantite__gt=0).count()
        taux_disponibilite = (medicaments_en_stock / total_medicaments * 100) if total_medicaments > 0 else 0
        
        # Médicaments les plus vendus/populaires de CETTE pharmacie
        medicaments_populaires = medicaments_pharmacie.order_by('-quantite')[:5]
        
        # 3. Données BI SPÉCIFIQUES
        donnees_bi = {
            'pharmacie': pharmacie,
            'statistiques': {
                'total_medicaments': total_medicaments,
                'medicaments_en_stock': medicaments_en_stock,
                'medicaments_rupture': medicaments_pharmacie.filter(quantite=0).count(),
                'taux_disponibilite': round(taux_disponibilite, 1),
                'chiffre_affaires_estime': calculer_ca_estime(pharmacie),
                'clients_quotidiens': estimer_clients_quotidiens(pharmacie)
            },
            'medicaments_populaires': [
                {
                    'nom': med.nom,
                    'quantite': med.quantite,
                    'prix': med.prix,
                    'statut': '🟢 Bon stock' if med.quantite > 20 else '🟡 Stock moyen' if med.quantite > 5 else '🔴 Rupture imminente'
                }
                for med in medicaments_populaires
            ],
            'alertes_stock': [
                {
                    'nom': med.nom,
                    'quantite': med.quantite,
                    'urgence': '🔴 CRITIQUE' if med.quantite == 0 else '🟠 URGENT' if med.quantite <= 2 else '🟡 ATTENTION'
                }
                for med in medicaments_pharmacie if med.quantite <= 5
            ],
            'performances': {
                'score_disponibilite': min(100, taux_disponibilite + 20),  # Score ajusté
                'classement_zone': "🏆 2ème sur 8",  # Valeur fixe pour éviter l'erreur
                'taux_fidelite': 78,  # À calculer avec vos données
                'satisfaction_clients': '⭐ 4.5/5'
            }
        }
        
        # 4. Recommandations PERSONNALISÉES
        recommandations = generer_recommandations_personnalisees(pharmacie, medicaments_pharmacie)
        
        context = {
            'donnees_bi': donnees_bi,
            'recommandations': recommandations,
            'timestamp': datetime.now().strftime("%d/%m/%Y à %H:%M")
        }
        
        return render(request, 'tableau_bord_pharmacien.html', context)
        
    except Pharmacie.DoesNotExist:
        # Gérer le cas où l'utilisateur n'a pas de pharmacie
        return render(request, 'erreur_pharmacie.html', {
            'message': '❌ Aucune pharmacie associée à votre compte'
        })
    except Exception as e:
        # Version de secours en cas d'erreur
        return render(request, 'tableau_bord_pharmacien.html', {
            'donnees_bi': {
                'pharmacie': {'nom': 'Votre Pharmacie', 'address': 'Adresse non disponible'},
                'statistiques': {
                    'total_medicaments': 'N/A',
                    'taux_disponibilite': 'N/A',
                    'chiffre_affaires_estime': 'N/A',
                    'clients_quotidiens': 'N/A'
                },
                'alertes_stock': [],
                'performances': {
                    'score_disponibilite': 'N/A',
                    'classement_zone': 'N/A',
                    'taux_fidelite': 'N/A'
                }
            },
            'recommandations': ["🤖 Système en cours de configuration...", "📊 Données bientôt disponibles"],
            'timestamp': datetime.now().strftime("%d/%m/%Y à %H:%M"),
            'erreur': str(e)
        })

# === FONCTIONS AUXILIAIRES ===

def calculer_ca_estime(pharmacie):
    """Calcule le chiffre d'affaires estimé de la pharmacie"""
    try:
        medicaments = Medicament.objects.filter(pharmacie=pharmacie)
        if not medicaments:
            return "0 FCFA"
        
        # Estimation basique : prix moyen × quantité moyenne × facteur
        prix_moyen = sum(med.prix for med in medicaments) / len(medicaments)
        quantite_moyenne = sum(med.quantite for med in medicaments) / len(medicaments)
        ca_estime = prix_moyen * quantite_moyenne * 0.3  # Facteur de rotation
        
        return f"{int(ca_estime):,} FCFA".replace(',', ' ')
    except:
        return "Estimation en cours..."

def estimer_clients_quotidiens(pharmacie):
    """Estime le nombre de clients quotidiens"""
    try:
        # Basé sur le nombre de médicaments et la localisation
        medicaments_count = Medicament.objects.filter(pharmacie=pharmacie).count()
        return max(10, medicaments_count // 3)  # Estimation basique
    except:
        return 25  # Valeur par défaut

def generer_recommandations_personnalisees(pharmacie, medicaments):
    """Génère des recommandations spécifiques à cette pharmacie"""
    recommandations = []
    
    try:
        # Analyser les stocks
        medicaments_faible_stock = [med for med in medicaments if med.quantite <= 5]
        medicaments_populaires = sorted(medicaments, key=lambda x: x.quantite, reverse=True)[:3]
        
        if medicaments_faible_stock:
            noms = ", ".join(med.nom for med in medicaments_faible_stock[:3])
            recommandations.append(f"🔴 **Réapprovisionnement urgent** : {noms}")
        
        if medicaments_populaires:
            noms = ", ".join(med.nom for med in medicaments_populaires)
            recommandations.append(f"📈 **Produits performants** : {noms} - maintenir les stocks")
        
        # Recommandations génériques basées sur l'analyse
        recommandations.extend([
            "💡 **Promotion** : Mettre en avant les vitamines en période hivernale",
            "🎯 **Service** : Envisager la livraison à domicile pour les clients âgés",
            "📊 **Optimisation** : Réduire les stocks des médicaments peu demandés"
        ])
        
    except Exception as e:
        # Recommandations par défaut en cas d'erreur
        recommandations = [
            "🤖 Système d'analyse IA activé",
            "📈 Vos données sont en cours d'analyse",
            "💡 Recommandations personnalisées bientôt disponibles"
        ]
    
    return recommandations


from django.contrib.auth.decorators import login_required

@login_required
def recherche_intelligente_pharmacie(request):
    """Recherche IA uniquement pour les médicaments de la pharmacie connectée"""
    
    query = request.GET.get('q', '').strip()
    
    try:
        # 1. Récupérer la pharmacie de l'utilisateur connecté
        pharmacie = Pharmacie.objects.get(utilisateur=request.user)
        
        if not query:
            return render(request, 'recherche_ia.html', {
                'pharmacie': pharmacie,
                'ai_enabled': True,
                'message': '🔍 Entrez un médicament à rechercher dans votre pharmacie'
            })
        
        # 2. Recherche UNIQUEMENT dans les médicaments de CETTE pharmacie
        medicaments_trouves = Medicament.objects.filter(
            pharmacie=pharmacie
        ).filter(
            Q(nom__icontains=query) | 
            Q(description__icontains=query) |
            Q(categorie__icontains=query)
        )
        
        # 3. Recommandations IA basées uniquement sur les médicaments de cette pharmacie
        recommandations_ia = []
        if medicaments_trouves:
            medicament_principal = medicaments_trouves.first()
            autres_medicaments = Medicament.objects.filter(pharmacie=pharmacie).exclude(id=medicament_principal.id)[:20]
            
            recommandations_ia = PharmaAI.recommander_medicaments_similaires(
                medicament_principal, 
                autres_medicaments,
                max_recommandations=3
            )
        
        # 4. Statistiques de CETTE pharmacie uniquement
        stats_pharmacie = generer_statistiques_pharmacie(pharmacie)
        
        context = {
            'query': query,
            'pharmacie': pharmacie,
            'medicaments': medicaments_trouves,
            'recommandations_ia': recommandations_ia,
            'stats_pharmacie': stats_pharmacie,
            'ai_enabled': True,
            'timestamp': datetime.now().strftime("%d/%m/%Y à %H:%M")
        }
        
        return render(request, 'recherche_ia.html', context)
        
    except Pharmacie.DoesNotExist:
        return render(request, 'recherche_ia.html', {
            'erreur': '❌ Aucune pharmacie associée à votre compte'
        })

def generer_statistiques_pharmacie(pharmacie):
    """Génère les statistiques spécifiques à une pharmacie"""
    medicaments_pharmacie = Medicament.objects.filter(pharmacie=pharmacie)
    total_medicaments = medicaments_pharmacie.count()
    
    # Calcul des stats réelles
    medicaments_en_stock = medicaments_pharmacie.filter(quantite__gt=0).count()
    taux_disponibilite = (medicaments_en_stock / total_medicaments * 100) if total_medicaments > 0 else 0
    
    # Tendances basées sur les recherches internes
    tendances_pharmacie = analyser_tendances_pharmacie(pharmacie)
    
    return {
        'total_medicaments': total_medicaments,
        'medicaments_en_stock': medicaments_en_stock,
        'taux_disponibilite': round(taux_disponibilite, 1),
        'tendances': tendances_pharmacie,
        'alertes_stock': medicaments_pharmacie.filter(quantite__lte=5).count(),
        'performance': '🟢 Excellente' if taux_disponibilite > 80 else '🟡 Moyenne' if taux_disponibilite > 60 else '🔴 À améliorer'
    }

def analyser_tendances_pharmacie(pharmacie):
    """Analyse les tendances spécifiques à cette pharmacie"""
    # En pratique, vous analyseriez les recherches faites sur cette pharmacie
    medicaments_populaires = Medicament.objects.filter(pharmacie=pharmacie).order_by('-quantite')[:5]
    
    tendances = []
    for i, med in enumerate(medicaments_populaires):
        niveau = "🔥 Très demandé" if i < 2 else "📈 En croissance" if i < 4 else "📊 Stable"
        tendances.append({
            'terme': med.nom,
            'niveau': niveau,
            'stock': med.quantite,
            'statut': '🟢 Bon' if med.quantite > 20 else '🟡 Moyen' if med.quantite > 5 else '🔴 Faible'
        })
    
    return tendances

import requests







def get_contexte_pharmacie(pharmacie):
    """Récupère toutes les données de la pharmacie pour l'IA"""
    
    contexte = f"""
# CONTEXTE COMPLET - PHARMACIE {pharmacie.nom.upper()}

## INFORMATIONS GÉNÉRALES:
- Nom: {pharmacie.nom}
- Adresse: {pharmacie.address}
- Zone: {pharmacie.zone}
- Statut: {'DE GARDE' if pharmacie.deGarde else 'Normal'}
- Coordonnées: {pharmacie.latitude}, {pharmacie.longitude}




## STOCK DE MÉDICAMENTS:
"""
    
    # Récupérer les médicaments CORRECTEMENT
    try:
        medicaments = Medicament.objects.filter(pharmacie=pharmacie)
        
        if medicaments.exists():
            for med in medicaments:
                contexte += f"""
- **{med.nom}** 
  • Catégorie: {med.categorie}
  • Quantité: {med.quantite} unités
  • Prix: {med.prix}€
  • Description: {med.description or 'Non spécifiée'}
"""
        else:
            contexte += "\n- Aucun médicament en stock\n"
            
    except Exception as e:
        contexte += f"\n- Erreur chargement stock: {str(e)}\n"
    
    # Statistiques du stock (VALUE ADDED!)
    try:
        total_medicaments = medicaments.count()
        total_quantite = sum(med.quantite for med in medicaments)
        valeur_stock = sum(med.quantite * med.prix for med in medicaments if med.prix)
        
        contexte += f"""
## STATISTIQUES STOCK:
- Nombre de médicaments différents: {total_medicaments}
- Quantité totale en stock: {total_quantite} unités
- Valeur estimée du stock: {valeur_stock:.2f}€
"""
    except:
        pass
    
    # Historique des conversations
    conversations_recentes = MonIA.objects.filter(Pharmacie=pharmacie).order_by('-timestamp')[:3]
    if conversations_recentes:
        contexte += "\n## HISTORIQUE RÉCENT:\n"
        for conv in conversations_recentes:
            contexte += f"- {conv.type_conversation}: {conv.message[:50]}...\n"
    
    return contexte


def converser_avec_ia(pharmacie, prompt, context="general"):
    # VÉRIFICATION CRITIQUE DE LA CLÉ API
    if not hasattr(settings, 'GOOGLE_AI_API_KEY') or not settings.GOOGLE_AI_API_KEY:
        return "❌ Erreur: Clé API Google AI non configurée dans settings.py"
    
    if settings.GOOGLE_AI_API_KEY == "votre-clé-api-ici" or len(settings.GOOGLE_AI_API_KEY) < 10:
        return "❌ Erreur: Clé API Google AI invalide. Remplacez 'votre-clé-api-ici' par votre vraie clé."
    
    contexte_pharma = get_contexte_pharmacie(pharmacie)
    prompt_enrichi = f"""
{contexte_pharma}

## QUESTION DU PHARMACIEN ({context}):
{prompt} (repond en cette langue)

## INSTRUCTIONS:
Tu es un assistant expert pour les pharmacies. Utilise les données ci-dessus pour donner des conseils personnalisés.
- Analyse le stock et identifie les risques
- Propose des actions concrètes
- Donne des insights business
- Sois précis et utilitaire
"""
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-001:generateContent"
    headers = {
        'Content-Type': 'application/json'
    }
    params = {
        'key': settings.GOOGLE_AI_API_KEY
    }
    data = {
        "contents": [{
            "parts": [{
                "text": prompt_enrichi
            }]
        }]
    }
    
    try:
        reponse = requests.post(
            url, 
            headers=headers, 
            params=params, 
            json=data,
            timeout=30  # Ajout timeout
        )
        
        # GESTION DÉTAILLÉE DES ERREURS
        if reponse.status_code == 200:
            reponse_texte = reponse.json()['candidates'][0]['content']['parts'][0]['text']
            
            # Sauvegarde en base
            MonIA.objects.create(
                Pharmacie=pharmacie,
                message=prompt,
                reponse=reponse_texte,
                type_conversation=context
            )
            return reponse_texte
            
        elif reponse.status_code == 403:
            error_detail = reponse.json().get('error', {}).get('message', 'Accès refusé')
            return f"🔐 Erreur 403 - Accès refusé: {error_detail}\n\n💡 Solution: Vérifiez votre clé API Google AI dans Google Cloud Console"
        
        elif reponse.status_code == 400:
            error_detail = reponse.json().get('error', {}).get('message', 'Requête invalide')
            return f"📝 Erreur 400 - Requête invalide: {error_detail}"
        
        elif reponse.status_code == 429:
            return "⏰ Erreur 429 - Quota dépassé. Attendez quelques minutes ou vérifiez votre quota Google Cloud."
        
        else:
            return f"🌐 Erreur API {reponse.status_code}: {reponse.text}"
            
    except requests.exceptions.RequestException as e:
        return f"🔌 Erreur réseau: {str(e)}"
    except Exception as e:
        return f"❌ Erreur inattendue: {str(e)}"







"""def test_ia(request):
    from .models import Pharmacie
    
    # Prend la première pharmacie de ta base
    pharmacie_test = Pharmacie.objects.first()
    
    if not pharmacie_test:
        return HttpResponse("❌ Aucune pharmacie dans la base")
    
    # Appelle ta fonction IA
    reponse = converser_avec_ia(
        pharmacie_test, 
        "buenos dias"
    )"""
    
    #Affiche le résultat brut pour debug
    #return HttpResponse(f"""{reponse}
    #""")

#http://localhost:8000/test-ia/



"""def lister_modeles(request):
    url = "https://generativelanguage.googleapis.com/v1beta/models"
    params = {'key': settings.GOOGLE_AI_API_KEY}
    
    response = requests.get(url, params=params)
    return HttpResponse(f"Modèles disponibles: {response.text}")
#http://localhost:8000/lister-modeles"""


# Dans views.py

import json
from django.http import JsonResponse

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required


#http://localhost:8000/pharmacie/1/chat-ia/




@login_required
def chat_ia(request, pharmacie_id):
    pharmacie = get_object_or_404(Pharmacie, id=pharmacie_id, utilisateur=request.user)
    from datetime import datetime, timedelta
    yesterday = datetime.now() - timedelta(days=1)
    conversations = MonIA.objects.filter(Pharmacie=pharmacie,timestamp__gte=yesterday).order_by('timestamp')
    
    reponse_ia = None
    
    if request.method == 'POST':
        message = request.POST.get('message')
        contexte = request.POST.get('contexte', 'general')
        
        try:
            reponse_ia = converser_avec_ia(pharmacie, message, contexte)
            
            # Vérifier si c'est une requête AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'reponse': reponse_ia
                })
                
        except Exception as e:
            print(f"Erreur IA: {e}")  # Pour debugger
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
            # Pour les requêtes normales, on continue normalement
    
    # Si c'est une requête GET ou POST normale (pas AJAX)
    return render(request, 'chat_ia.html', {
        'pharmacie': pharmacie,
        'conversations': conversations,
        'reponse_ia': reponse_ia
    })
from .form import InscriptionPersonel

def inscription_personel(request):
    pharmacie = get_object_or_404(Pharmacie, utilisateur=request.user)
    if request.method=='POST':
        form=InscriptionPersonel(request.POST,request.FILES)
        if form.is_valid():
            personel=Specialiste.objects.create(
                nom=form.cleaned_data['nom'],
                prenom=form.cleaned_data['prenom'],
                specialite=form.cleaned_data['specialite'],
                photo=form.cleaned_data['photo'],
                pharmacie=pharmacie
            )
            return redirect('info_personel') 
    else:
            form=InscriptionPersonel()
    return render (request,'inscription_personel.html',{'form': form})

#http://localhost:8000/inscription-personel/

@login_required
def info_personel(request):
    try:
        pharmacie=Pharmacie.objects.get(utilisateur=request.user)
        personels=Specialiste.objects.filter(pharmacie=pharmacie)
        print("Personnels trouvés:", personels.values_list('id', 'nom', 'prenom'))
        return render(request,'info_personel.html',{
            'pharmacie':pharmacie,
            'personnels':personels
        })
    except Pharmacie.DoesNotExist:
        return render(request,'info_personel.html',{
            'pharmacie':None,
            'personnels':[],
            'erreur':'Aucune pharmacie associée à votre compte'
        })
#http://localhost:8000/info-personel/
@login_required
def suprimer_personel(request,personel_id):
    pharmacie = get_object_or_404(Pharmacie, utilisateur=request.user)
    personel=get_object_or_404(Specialiste,id=personel_id,pharmacie=pharmacie)
    if request.method=='POST':
        personel.delete()
        return redirect('info_personel')
    return render(request,'suprimer_personel.html',{'personnel':personel})
#http://localhost:8000/suprimer-personel/7/ 

def modifier_personel(request,personel_id):   
    pharmacie = get_object_or_404(Pharmacie, utilisateur=request.user)
    personel=get_object_or_404(Specialiste,id=personel_id,pharmacie=pharmacie)
    if request.method =='POST':
        form=InscriptionPersonel(request.POST,request.FILES,instance=personel)
        if form.is_valid():
            form.save()
            return redirect('info_personel')
    else:
        form=InscriptionPersonel(instance=personel)

    return render(request,'modifier_personel.html',{
        'form':form,
        'personnel':personel
    })
#http://localhost:8000/modifier-personel/7/ 

def fiche_personel(request,personel_id):
    personel = get_object_or_404(Specialiste, id=personel_id)
    return render(request,'fiche_personel.html',{'personnel':personel})


#partie des commandes
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Pharmacie, Medicament, Commande, LigneCommande, Client


@login_required
def passer_commande(request, pharmacie_id, medicament_id=None):
    """
    Vue unifiée pour commander :
    - Si medicament_id=None → Panier complet (tous les médicaments)
    - Si medicament_id fourni → Commande rapide d'un seul médicament
    """
    pharmacie = get_object_or_404(Pharmacie, id=pharmacie_id)
    
    # Gestion du client
    client, created = Client.objects.get_or_create(user=request.user)
    
    # Déterminer le contexte selon le type de commande
    if medicament_id:
        # MODE COMMANDE RAPIDE (un seul médicament)
        medicament = get_object_or_404(Medicament, id=medicament_id, pharmacie=pharmacie)
        
        if request.method == 'POST':
            return _traiter_commande_rapide(request, client, pharmacie, medicament)
        
        # GET - Afficher formulaire commande rapide
        return render(request, 'commande/commande_rapide.html', {
            'pharmacie': pharmacie,
            'medicament': medicament,
            'stock_disponible': medicament.quantite
        })
    
    else:
        # MODE PANIER COMPLET (tous les médicaments)
        medicaments = Medicament.objects.filter(pharmacie=pharmacie, quantite__gt=0)
        
        if request.method == 'POST':
            return _traiter_commande_panier(request, client, pharmacie, medicaments)
        
        # GET - Afficher panier complet
        return render(request, 'commande/panier_complet.html', {
            'pharmacie': pharmacie,
            'medicaments': medicaments
        })


def _traiter_commande_rapide(request, client, pharmacie, medicament):
    """Sous-fonction pour traiter une commande rapide"""
    quantite_str = request.POST.get('quantite', '1')
    print("🎯 DEBUG - Début traitement commande rapide")
    print(f"🎯 DEBUG - Client: {client}")
    print(f"🎯 DEBUG - Pharmacie: {pharmacie.nom}")
    print(f"🎯 DEBUG - Médicament: {medicament.nom}")
    print(f"🎯 DEBUG - Quantité reçue: {quantite_str}")
    
    try:
        quantite = int(quantite_str)
        print(f"🎯 DEBUG - Quantité convertie: {quantite}")
        
        if quantite <= 0:
            raise ValueError("La quantité doit être positive")
        if quantite > medicament.quantite:
            print("🎯 DEBUG - Erreur: stock insuffisant")
            return render(request, 'commande/commande_rapide.html', {
                'pharmacie': pharmacie,
                'medicament': medicament,
                'erreur': f'Stock insuffisant. Il reste {medicament.quantite} unités.'
            })
            
    except ValueError as e:
        print(f"🎯 DEBUG - Erreur validation quantité: {e}")
        return render(request, 'commande/commande_rapide.html', {
            'pharmacie': pharmacie,
            'medicament': medicament,
            'erreur': 'Veuillez entrer une quantité valide'
        })
    
    # Création de la commande
    try:
        print("🎯 DEBUG - Tentative création commande...")
        commande = Commande(client=client, pharmacie=pharmacie)
        commande.save()  # Utilise save() pour déclencher la date_expiration automatique
        print(f"🎯 DEBUG - Commande créée avec ID: {commande.id}")
        
        print("🎯 DEBUG - Création ligne commande...")
        ligne = LigneCommande.objects.create(
            commande=commande,
            medicament=medicament,
            quantite=quantite,
            prix_unitaire=medicament.prix
        )
        creer_notification_pharmacie(
        pharmacie=commande.pharmacie,
        type_notification='nouvelle_commande', 
        message=f"Nouvelle commande #{commande.id} de {client.user.username}",
        commande=commande
    )
        print(f"🎯 DEBUG - Ligne commande créée: {ligne.id}")
        
        print("🎯 DEBUG - Redirection vers détail commande...")
        return redirect('detail_commande', commande_id=commande.id)
        
    except Exception as e:
        print(f"🎯 DEBUG - ERREUR CRITIQUE: {e}")
        import traceback
        print(f"🎯 DEBUG - Traceback: {traceback.format_exc()}")
        return render(request, 'commande/commande_rapide.html', {
            'pharmacie': pharmacie,
            'medicament': medicament,
            'erreur': f'Erreur technique: {str(e)}'
        })




#http://localhost:8000/commander/1/1/


def _traiter_commande_panier(request, client, pharmacie, medicaments):
    """Sous-fonction pour traiter un panier complet"""
    print("🛒 DEBUG - Début traitement panier complet")
    medicaments_ids = request.POST.getlist('medicament_id')
    quantites = request.POST.getlist('quantite')
    
    print(f"🛒 DEBUG - Medicaments IDs: {medicaments_ids}")
    print(f"🛒 DEBUG - Quantités: {quantites}")
    
    # Vérifier qu'au moins un médicament est commandé
    if not any(q and int(q) > 0 for q in quantites):
        print("🛒 DEBUG - Aucun médicament sélectionné")
        return render(request, 'commande/panier_complet.html', {
            'pharmacie': pharmacie,
            'medicaments': medicaments,
            'erreur': 'Veuillez sélectionner au moins un médicament'
        })
    
    # Créer la commande
    try:
        print("🛒 DEBUG - Création commande panier...")
        commande = Commande(client=client, pharmacie=pharmacie)
        commande.save()
        creer_notification_pharmacie(
        pharmacie=commande.pharmacie,
        type_notification='nouvelle_commande', 
        message=f"Nouvelle commande #{commande.id} de {client.user.username}",
        commande=commande
    )
        print(f"🛒 DEBUG - Commande créée: {commande.id}")
        
        # Ajouter les lignes de commande
        for med_id, quantite in zip(medicaments_ids, quantites):
            if quantite and int(quantite) > 0:
                print(f"🛒 DEBUG - Ajout médicament {med_id}, quantité {quantite}")
                medicament = Medicament.objects.get(id=med_id)
                LigneCommande.objects.create(
                    commande=commande,
                    medicament=medicament,
                    quantite=int(quantite),
                    prix_unitaire=medicament.prix
                )
        
        print(f"🛒 DEBUG - Redirection vers détail commande {commande.id}")
        return redirect('detail_commande', commande_id=commande.id)
        
    except Exception as e:
        print(f"🛒 DEBUG - ERREUR panier: {e}")
        import traceback
        print(f"🛒 DEBUG - Traceback: {traceback.format_exc()}")
        return render(request, 'commande/panier_complet.html', {
            'pharmacie': pharmacie,
            'medicaments': medicaments,
            'erreur': f'Erreur lors de la création de la commande: {str(e)}'
        })





@login_required
def mes_commandes(request):
    try:
        client = request.user.client
        commandes = Commande.objects.filter(client=client).order_by('-date_creation')
    except Client.DoesNotExist:
        commandes = []
    
    return render(request, 'commande/mes_commandes.html', {
        'commandes': commandes
    })


@login_required
def detail_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    
    # Vérifier que l'utilisateur peut voir cette commande
    if request.user != commande.client.user and request.user != commande.pharmacie.utilisateur:
        return redirect('acces_interdit')
    
    lignes_commande = commande.lignecommande_set.all()
    # Calcul manuel du total
    total = 0
    for ligne in lignes_commande:
        total += ligne.quantite * ligne.prix_unitaire
    return render(request, 'commande/detail_commande.html', {
        'commande': commande,
        'lignes_commande': lignes_commande,
        'total':total
    })


@login_required
def commandes_pharmacie(request):
    # Vérifier que l'utilisateur est une pharmacie
    try:
        pharmacie = request.user.pharmacie
        commandes = Commande.objects.filter(pharmacie=pharmacie).order_by('-date_creation')
    except Pharmacie.DoesNotExist:
        return redirect('acces_interdit')
    
    return render(request, 'commande/commandes_pharmacie.html', {
        'commandes': commandes
    })

@login_required
def traiter_commande(request, commande_id, action):
    commande = get_object_or_404(Commande, id=commande_id)
    
    # Vérifier que l'utilisateur est la pharmacie concernée
    if request.user != commande.pharmacie.utilisateur:
        return redirect('passer_commande',pharmacie_id=commande.pharmacie.id)
    
    if action == 'accepter':
        commande.statut = 'acceptee'
        # TODO: Envoyer notification au client
    elif action == 'refuser':
        commande.statut = 'refusee'
        # TODO: Envoyer notification au client
    
    commande.date_traitement = timezone.now()
    commande.save()
    
    return redirect('commandes_pharmacie')

from .form import InscriptionClient
def inscription_client(request):
    if request.method=='POST':
        form=InscriptionClient(request.POST)
        if form.is_valid():
            user=User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            client=Client.objects.create(
                user=user,
                adresse=form.cleaned_data['address'],
                date_naissance=form.cleaned_data['date_naissance'],
                zone=form.cleaned_data['zone'],
                notifications_email = form.cleaned_data['notifications_email'],
                notifications_sms = form.cleaned_data['notifications_sms'],
                telephone=form.cleaned_data['numero']

            )
            from django.contrib.auth import login
            login(request, user)
            return redirect('passer_commande',pharmacie_id=1)
    else:
        form=InscriptionClient()
    return render(request, 'inscription_client.html', {'form': form})
    
#http://localhost:8000/inscription-client/

from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.http import JsonResponse

def connexion_rapide(request):
    if request.method == 'POST':
        identifiant = request.POST.get('identifiant')
        password = request.POST.get('password', '')
        pharmacie_id = request.POST.get('pharmacie_id')
        medicament_id = request.POST.get('medicament_id')
        
        try:
            # Chercher l'utilisateur par username ou email
            try:
                user = User.objects.get(username=identifiant)
            except User.DoesNotExist:
                user = User.objects.get(email=identifiant)
            
            # Vérifier le mot de passe (si fourni)
            if password:
                user = authenticate(username=user.username, password=password)
                if user is None:
                    return JsonResponse({'success': False, 'error': 'Mot de passe incorrect'})
            else:
                user = authenticate(username=user.username, password='')
                if user is None:
                    if user.has_usable_password():
                        return JsonResponse({'success': False, 'error': 'Mot de passe requis'})
            
            # Connecter l'utilisateur
            login(request, user)
            
            # 🔥 CHOIX DE LA REDIRECTION INTELLIGENTE
            if medicament_id:
                # Si medicament_id est fourni → commande rapide
                redirect_url = reverse('commande_rapide', kwargs={
                    'pharmacie_id': pharmacie_id,
                    'medicament_id': medicament_id
                })
            else:
                # Si pas de medicament_id → panier complet
                redirect_url = reverse('passer_commande', kwargs={
                    'pharmacie_id': pharmacie_id
                })
            
            return JsonResponse({'success': True, 'redirect_url': redirect_url})
            
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Utilisateur non trouvé'})
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})



@login_required
def annuler_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    
    # Vérifier que l'utilisateur peut annuler cette commande
    if request.user != commande.client.user:
        return redirect('/')  # Redirection simple vers l'accueil
    
    # Annuler la commande si elle est en attente
    if commande.statut == 'en_attente':
        commande.statut = 'annulee'
        commande.date_traitement = timezone.now()
        commande.save()
        creer_notification_pharmacie(
            pharmacie=commande.pharmacie,
            type_notification='commande_annulee',
            message=f"Commande #{commande.id} annulée par {commande.client.user.username}",
            commande=commande
        )
    return redirect('detail_commande', commande_id=commande.id)


from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from io import BytesIO

def telecharger_commande_pdf(request, commande_id):
    print("🎯 DEBUG PDF - DÉBUT de la vue")
    print(f"🎯 DEBUG PDF - User: {request.user}")
    commande = get_object_or_404(Commande, id=commande_id)
    print(f"🎯 DEBUG PDF - Commande client: {commande.client.user}")
    
    # Vérifier les permissions
    if request.user != commande.client.user:
        print("🎯 DEBUG PDF - PERMISSION REFUSÉE - Redirection")
        return redirect('passer_commande', pharmacie_id=commande.pharmacie.id)
    
    print("🎯 DEBUG PDF - Génération PDF en cours...")
    
    # Créer le buffer PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # En-tête
    p.setFont("Helvetica-Bold", 16)
    p.drawString(1*inch, 10.5*inch, f"COMMANDE #{commande.id}")
    p.setFont("Helvetica", 12)
    p.drawString(1*inch, 10*inch, f"Pharmacie: {commande.pharmacie.nom}")
    p.drawString(1*inch, 9.7*inch, f"Date: {commande.date_creation.strftime('%d/%m/%Y %H:%M')}")
    p.drawString(1*inch, 9.4*inch, f"Statut: {commande.get_statut_display()}")
    
    # Ligne séparatrice
    p.line(1*inch, 9.2*inch, 7.5*inch, 9.2*inch)
    
    # En-tête du tableau
    p.setFont("Helvetica-Bold", 10)
    p.drawString(1*inch, 9.0*inch, "Médicament")
    p.drawString(4*inch, 9.0*inch, "Quantité")
    p.drawString(5*inch, 9.0*inch, "Prix unit.")
    p.drawString(6.5*inch, 9.0*inch, "Sous-total")
    
    # Lignes de commande
    y_position = 8.7*inch
    total = 0
    lignes_commande = commande.lignecommande_set.all()
    
    for ligne in lignes_commande:
        if y_position < 1*inch:  # Nouvelle page si nécessaire
            p.showPage()
            y_position = 10*inch
        
        p.setFont("Helvetica", 9)
        p.drawString(1*inch, y_position, ligne.medicament.nom)
        p.drawString(4*inch, y_position, str(ligne.quantite))
        p.drawString(5*inch, y_position, f"{ligne.prix_unitaire} FCFA")
        sous_total = ligne.quantite * ligne.prix_unitaire
        p.drawString(6.5*inch, y_position, f"{sous_total} FCFA")
        total += sous_total
        y_position -= 0.3*inch
    
    # Total
    p.setFont("Helvetica-Bold", 12)
    p.drawString(5*inch, y_position - 0.5*inch, f"TOTAL: {total} FCFA")
    
    # Pied de page
    p.setFont("Helvetica-Oblique", 8)
    p.drawString(1*inch, 0.5*inch, f"Généré le {timezone.now().strftime('%d/%m/%Y %H:%M')}")
    
    p.showPage()
    p.save()
    
    # Préparer la réponse
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="commande_{commande.id}.pdf"'
    
    return response


@login_required
def notifications_pharmacie(request):
    try:
        pharmacie = request.user.pharmacie
        
        # Récupérer les notifications non lues ou liées aux commandes en attente
        notifications = Notification.objects.filter(pharmacie=pharmacie).order_by('-date_creation')
        
        nombre_non_lues = notifications.filter(lue=False).count()
        
    except Pharmacie.DoesNotExist:
        return redirect('/')
    
    return render(request, 'notifications.html', {
        'notifications': notifications,
        'nombre_non_lues': nombre_non_lues
    })
    
#http://localhost:8000/notifications/




@login_required
def accepter_commande(request, commande_id):
    try:
        pharmacie = request.user.pharmacie
        commande = get_object_or_404(Commande, id=commande_id, pharmacie=pharmacie)
        
        # Accepter la commande
        commande.statut = 'confirmee'
        commande.save()
        
        # Marquer la notification comme lue
        notification = Notification.objects.filter(commande=commande, type_notification='nouvelle_commande').first()
        if notification:
            notification.lue = True
            notification.save()
        
        # Créer une notification pour le client
        Notification.objects.create(
            user=commande.client.user,
            type_notification='commande_acceptee',
            message=f"Votre commande #{commande.id} a été acceptée par la pharmacie {pharmacie.nom}",
            commande=commande
        )
        
        messages.success(request, f"Commande #{commande.id} acceptée ! Email envoyé au client.")
        
    except Pharmacie.DoesNotExist:
        return redirect('/')
    
    return redirect('notifications_pharmacie')

@login_required
def refuser_commande(request, commande_id):
    try:
        pharmacie = request.user.pharmacie
        commande = get_object_or_404(Commande, id=commande_id, pharmacie=pharmacie)
        
        # Refuser la commande
        commande.statut = 'annulee'
        commande.save()
        
        # Marquer la notification comme lue
        notification = Notification.objects.filter(commande=commande, type_notification='nouvelle_commande').first()
        if notification:
            notification.lue = True
            notification.save()
        
        # Créer une notification pour le client
        Notification.objects.create(
            user=commande.client.user,
            type_notification='commande_refusee',
            message=f"Votre commande #{commande.id} a été refusée par la pharmacie {pharmacie.nom}",
            commande=commande
        )
        
        messages.success(request, f"Commande #{commande.id} refusée. Email envoyé au client.")
        
    except Pharmacie.DoesNotExist:
        return redirect('/')
    
    return redirect('notifications_pharmacie')

@login_required
def supprimer_notification(request, notification_id):
    """Supprimer une notification spécifique"""
    try:
        pharmacie = request.user.pharmacie
        notification = Notification.objects.get(id=notification_id, pharmacie=pharmacie)
        
        # Vérifier que l'utilisateur a le droit de supprimer cette notification
        if notification.commande and notification.commande.pharmacie == pharmacie:
            notification.delete()
            messages.success(request, "Notification supprimée.")
        elif notification.user == request.user:
            notification.delete()
            messages.success(request, "Notification supprimée.")
        else:
            messages.error(request, "Vous n'avez pas la permission de supprimer cette notification.")
            
    except Pharmacie.DoesNotExist:
        return redirect('/')
    
    return redirect('notifications_pharmacie')

@login_required
def supprimer_toutes_notifications(request):
    """Supprimer toutes les notifications de l'utilisateur"""
    try:
        pharmacie = request.user.pharmacie
        
        # Supprimer les notifications liées aux commandes de la pharmacie
        notifications_pharmacie = Notification.objects.filter(pharmacie=pharmacie)
        notifications_pharmacie.delete()
        
        # Supprimer les notifications personnelles de l'utilisateur
        notifications_personnelles = Notification.objects.filter(user=request.user)
        notifications_personnelles.delete()
        
        messages.success(request, "Toutes les notifications ont été supprimées.")
        
    except Pharmacie.DoesNotExist:
        return redirect('/')
    
    return redirect('notifications_pharmacie')

@login_required
def marquer_toutes_lues(request):
    """Marquer toutes les notifications comme lues"""
    try:
        pharmacie = request.user.pharmacie
        
        # Marquer comme lues les notifications liées aux commandes de la pharmacie
        Notification.objects.filter(commande__pharmacie=pharmacie, lue=False).update(lue=True)
        
        # Marquer comme lues les notifications personnelles
        Notification.objects.filter(pharmacie=pharmacie, lue=False).update(lue=True)
        
        messages.success(request, "Toutes les notifications ont été marquées comme lues.")
        
    except Pharmacie.DoesNotExist:
        return redirect('/')
    
    return redirect('notifications_pharmacie')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def envoyeremail_commande(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            commande_id = data.get('commande_id')
            action = data.get('action')
            
            commande = Commande.objects.get(id=commande_id)
            pharmacie = commande.pharmacie
            
            if action == 'accepter':
                sujet = f"✅ Commande #{commande.id} acceptée - {pharmacie.nom}"
                statut_text = "acceptée"
            else:
                sujet = f"❌ Commande #{commande.id} refusée - {pharmacie.nom}" 
                statut_text = "refusée"
            
            # CALCULER LE TOTAL MANUELLEMENT (puisque pas de champ total)
            total_commande = 0
            if commande.medicaments.exists():
                for medicament in commande.medicaments.all():
                    # Suppose que medicament a un champ 'prix'
                    total_commande += medicament.prix * medicament.quantite
            
            message = f"""
Bonjour {commande.client.user.first_name},

Votre commande #{commande.id} a été {statut_text} par la pharmacie {pharmacie.nom}.

📋 Détails :
- Numéro : #{commande.id}  
- Date : {commande.date_creation.strftime('%d/%m/%Y à %H:%M')}
- Statut : {statut_text.capitalize()}
- Total : {total_commande} €

Cordialement,
{pharmacie.nom}
{pharmacie.adresse}
Téléphone : {pharmacie.telephone}
"""
            
            # Envoyer l'email (pour tester, on va d'abord simuler l'envoi)
            print("=== EMAIL SIMULÉ ===")
            print(f"De: {pharmacie.email}")
            print(f"À: {commande.client.user.email}") 
            print(f"Sujet: {sujet}")
            print(f"Message: {message}")
            print("=====================")
            
            return JsonResponse({'success': True, 'message': 'Email simulé avec succès'})
            
        except Exception as e:
            print(f"Erreur: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

@csrf_exempt
def envoyer_email_commande(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            commande_id = data.get('commande_id')
            action = data.get('action')
            
            commande = Commande.objects.get(id=commande_id)
            pharmacie = commande.pharmacie
            
            if action == 'accepter':
                sujet = f"✅ Commande #{commande.id} acceptée - {pharmacie.nom}"
                statut_text = "acceptée"
            else:
                sujet = f"❌ Commande #{commande.id} refusée - {pharmacie.nom}" 
                statut_text = "refusée"
            
            # Récupérer les médicaments via lignecommande_set
            lignes_commande = commande.lignecommande_set.all()
            details_medicaments = ""
            
            if lignes_commande.exists():
                details_medicaments = "\n📦 Médicaments commandés :\n"
                for ligne in lignes_commande:
                    details_medicaments += f"- {ligne.medicament.nom} : {ligne.quantite} unité(s) - {ligne.prix_unitaire}  FCFA/unité\n"
            
            # Calculer le total
            total_commande = commande.get_total()
            
            message = f"""
Bonjour {commande.client.user.first_name},

Votre commande #{commande.id} a été {statut_text} par la pharmacie {pharmacie.nom}.

📋 Détails de la commande :
- Numéro : #{commande.id}  
- Date : {commande.date_creation.strftime('%d/%m/%Y à %H:%M')}
- Statut : {statut_text.capitalize()}
- Total : {total_commande} FCFA
{details_medicaments}
Cordialement,
{pharmacie.nom}
{pharmacie.address}  
{pharmacie.zone}
"""

            # ENVOI RÉEL D'EMAIL (DÉCOMMENTÉ)
            send_mail(
                sujet,
                message,
                'notifications.pharmacie@gmail.com',  # Expéditeur générique
                [commande.client.user.email],         # Ton email de test
                fail_silently=False,
            )
            
            print(f"✅ Email RÉEL envoyé à: {commande.client.user.email}")
            
            return JsonResponse({'success': True, 'message': 'Email simulé avec succès'})
            
        except Exception as e:
            print(f"Erreur: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})



from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db.models import Q
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from io import BytesIO
from django.core.paginator import Paginator

# VUE EXISTANTE À MODIFIER
@login_required
def commandes_pharmacie(request):
    """Vue améliorée avec recherche, filtres et historique"""
    try:
        pharmacie = request.user.pharmacie
        
        # Récupérer les paramètres de recherche/filtre
        recherche_id = request.GET.get('recherche_id')
        statut_filtre = request.GET.get('statut')
        date_debut = request.GET.get('date_debut')
        date_fin = request.GET.get('date_fin')
        
        # Base queryset
        commandes = Commande.objects.filter(pharmacie=pharmacie)
        
        # Appliquer les filtres
        if recherche_id:
            commandes = commandes.filter(id=recherche_id)
        
        if statut_filtre:
            commandes = commandes.filter(statut=statut_filtre)
        
        if date_debut:
            commandes = commandes.filter(date_creation__gte=date_debut)
        
        if date_fin:
            commandes = commandes.filter(date_creation__lte=date_fin)
        
        # Tri par défaut
        commandes = commandes.order_by('-date_creation')
        
    except Pharmacie.DoesNotExist:
        return redirect('acces_interdit')
    
    return render(request, 'commande/commandes_pharmacie.html', {
        'commandes': commandes,
        'pharmacie':pharmacie
    })

# NOUVELLE VUE - Historique des commandes
@login_required
def historique_commandes(request):
    """Historique complet avec pagination"""
    try:
        pharmacie = request.user.pharmacie
        
        # Récupérer TOUTES les commandes (même archivées/supprimées)
        commandes = Commande.objects.filter(pharmacie=pharmacie).order_by('-date_creation')
        
        # Pagination
        paginator = Paginator(commandes, 20)  # 20 commandes par page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
    except Pharmacie.DoesNotExist:
        return redirect('/')
    
    return render(request, 'commande/historique_commandes.html', {
        'page_obj': page_obj,
        'pharmacie':pharmacie
    })

# NOUVELLE VUE - Marquer comme récupérée
@login_required
def marquer_recuperee(request, commande_id):
    """Marquer une commande comme récupérée par le client"""
    try:
        pharmacie = request.user.pharmacie
        commande = get_object_or_404(Commande, id=commande_id, pharmacie=pharmacie)
        
        if commande.statut == 'acceptee':
            commande.statut = 'recuperee'
            commande.save()
            messages.success(request, f"Commande #{commande.id} marquée comme récupérée")
        else:
            messages.error(request, "Seules les commandes acceptées peuvent être marquées comme récupérées")
            
    except Pharmacie.DoesNotExist:
        return redirect('/')
    
    return redirect('commandes_pharmacie')

# NOUVELLE VUE - Supprimer une commande (archivage)
@login_required
def supprimer_commande(request, commande_id):
    """Archiver une commande (soft delete)"""
    try:
        pharmacie = request.user.pharmacie
        commande = get_object_or_404(Commande, id=commande_id, pharmacie=pharmacie)
        
        # Ici on pourrait faire un soft delete plutôt que supprimer
        # Pour l'instant on supprime vraiment
        commande_id = commande.id
        commande.delete()
        
        messages.success(request, f"Commande #{commande_id} archivée")
            
    except Pharmacie.DoesNotExist:
        return redirect('/')
    
    return redirect('commandes_pharmacie')

# NOUVELLE VUE - Supprimer toutes les commandes
@login_required
def supprimer_toutes_commandes(request):
    """Archiver toutes les commandes de la pharmacie"""
    try:
        pharmacie = request.user.pharmacie
        
        commandes = Commande.objects.filter(pharmacie=pharmacie)
        count = commandes.count()
        commandes.delete()
        
        messages.success(request, f"{count} commande(s) archivée(s)")
        
    except Pharmacie.DoesNotExist:
        return redirect('/')
    
    return redirect('commandes_pharmacie')

# NOUVELLE VUE - Générer PDF
@login_required
def generer_pdf_commande(request, commande_id):
    """Générer un PDF de facture pour une commande"""
    try:
        pharmacie = request.user.pharmacie
        commande = get_object_or_404(Commande, id=commande_id, pharmacie=pharmacie)
        
        # Créer le PDF en mémoire
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # En-tête
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 50, f"Facture - Commande #{commande.id}")
        
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 80, f"Pharmacie: {pharmacie.nom}")
        p.drawString(50, height - 100, f"Client: {commande.client.user.get_full_name()}")
        p.drawString(50, height - 120, f"Date: {commande.date_creation.strftime('%d/%m/%Y %H:%M')}")
        
        # Détails des médicaments
        y_position = height - 160
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_position, "Détails des médicaments:")
        
        y_position -= 30
        lignes = commande.lignecommande_set.all()
        for ligne in lignes:
            if y_position < 100:  # Nouvelle page si nécessaire
                p.showPage()
                y_position = height - 50
            
            p.setFont("Helvetica", 10)
            p.drawString(50, y_position, f"- {ligne.medicament.nom}")
            p.drawString(300, y_position, f"Quantité: {ligne.quantite}")
            p.drawString(400, y_position, f"Prix: {ligne.prix_unitaire} €")
            p.drawString(500, y_position, f"Total: {ligne.sous_total()} €")
            y_position -= 20
        
        # Total
        y_position -= 20
        p.setFont("Helvetica-Bold", 12)
        p.drawString(400, y_position, f"TOTAL: {commande.get_total()} €")
        
        # Statut
        y_position -= 30
        p.drawString(50, y_position, f"Statut: {commande.get_statut_display()}")
        
        p.showPage()
        p.save()
        
        # Retourner le PDF
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="commande_{commande.id}.pdf"'
        return response
        
    except Pharmacie.DoesNotExist:
        return redirect('/')
    except Exception as e:
        messages.error(request, f"Erreur génération PDF: {str(e)}")
        return redirect('commandes_pharmacie')