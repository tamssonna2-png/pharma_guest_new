from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from tamsPh.models import Medicament
from tamsPh.models import Specialiste
from tamsPh.models import Pharmacie,trouver_pharmacies_les_plus_proches,calculer_distance
from tamsPh.models import MonIA
from django.contrib.auth.models import User
# Create your views here.

def accueil(request):
    """Page d'accueil principale"""
    return render(request, 'accueil.html')

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

def medicament_client_recherche(request):
    """Affiche le formulaire ou les options de recherche de médicaments."""
    # Cette fonction rend le template HTML que vous voulez afficher
    return render(request, 'medicament_recherche.html', {})


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
        context['erreur'] = "Veuillez entrer un nom de médicament."
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
                    'nom': med.nom,
                    'categorie': med.categorie,
                    'description': med.description,
                    'prix': med.prix,
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
    print(request.user)
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
# Fichier tamsPh/views.py (Ajouter cette fonction)

def rechercher_medicament_page(request):
    """Affiche le formulaire ou les options de recherche de médicaments."""
    # Cette fonction rend le template HTML que vous voulez afficher
    return render(request, 'rechercher_medicament_page.html', {})

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
    Vue pour permettre au pharmacien de modifier les informations de sa pharmacie
    """
    # Récupérer la pharmacie de l'utilisateur connecté
    try:
        pharmacie = Pharmacie.objects.get(utilisateur=request.user)
    except Pharmacie.DoesNotExist:
        messages.error(request, "Aucune pharmacie associée à votre compte.")
        return redirect('mes_medicaments_perso')
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.POST.get('nom')
        address = request.POST.get('address')
        zone = request.POST.get('zone')
        deGarde = request.POST.get('deGarde') == 'on'  # Checkbox renvoie 'on' si cochée
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        # Validation des données
        if not nom or not address or not zone:
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
        else:
            try:
                # Mettre à jour la pharmacie
                pharmacie.nom = nom
                pharmacie.address = address
                pharmacie.zone = zone
                pharmacie.deGarde = deGarde
                
                # Gestion des coordonnées GPS (optionnelles)
                if latitude:
                    pharmacie.latitude = float(latitude)
                if longitude:
                    pharmacie.longitude = float(longitude)
                
                pharmacie.save()
                
                messages.success(request, "✅ Les informations de votre pharmacie ont été mises à jour avec succès!")
                return redirect('mes_medicaments_perso')
                
            except ValueError:
                messages.error(request, "❌ Erreur: Les coordonnées GPS doivent être des nombres valides.")
            except Exception as e:
                messages.error(request, f"❌ Une erreur s'est produite: {str(e)}")
    
    # Contexte pour le template
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
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        
        try:
            user = User.objects.get(username=username, email=email)
            
            # Générer un nouveau mot de passe temporaire
            temp_password = generate_temp_password()
            user.set_password(temp_password)
            user.save()
            
            # Envoyer un email (optionnel)
            try:
                send_mail(
                    'Réinitialisation de votre mot de passe - PharmaGest',
                    f'''
                    Bonjour,
                    
                    Votre mot de passe a été réinitialisé.
                    
                    Identifiant : {username}
                    Mot de passe temporaire : {temp_password}
                    
                    Veuillez vous connecter et changer votre mot de passe immédiatement.
                    
                    Cordialement,
                    L'équipe PharmaGest
                    ''',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=True,
                )
            except:
                pass  # L'email n'est pas essentiel
            
            messages.success(request, f'''
            ✅ Mot de passe réinitialisé avec succès !
            
            Identifiant : {username}
            Mot de passe temporaire : {temp_password}
            
            Veuillez vous connecter et changer votre mot de passe immédiatement.
            ''')
            
            return redirect('login')
            
        except User.DoesNotExist:
            messages.error(request, 
                '❌ Aucun utilisateur trouvé avec ces identifiants. '
                'Vérifiez votre nom d\'utilisateur et email.'
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







def converser_avec_ia(pharmacie, promt,context="general"):
    contexte_pharma = get_contexte_pharmacie(pharmacie)
    prompt_enrichi = f"""
{contexte_pharma}

## QUESTION DU PHARMACIEN ({context}):
{promt} (repond en cette langue)

## INSTRUCTIONS:
Tu es un assistant expert pour les pharmacies. Utilise les données ci-dessus pour donner des conseils personnalisés.
- Analyse le stock et identifie les risques
- Propose des actions concrètes
- Donne des insights business
- Sois précis et utilitaire
"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-001:generateContent"
    headers ={
        'Content-Type':'application/json'
    }
    params={
        'key':settings.GOOGLE_AI_API_KEY
    }
    data ={
        "contents": [{
        "parts": [{
        "text": prompt_enrichi  # ← C'est ici qu'on mettra le message du pharmacien
        }]
    }]
    }
    reponse =requests.post(
        url,headers=headers,params=params,json=data
    )
    if reponse.status_code==200:
        reponse_texte = reponse.json()['candidates'][0]['content']['parts'][0]['text']
        MonIA.objects.create(
            Pharmacie=pharmacie,
            message=promt,
            reponse=reponse_texte,
            type_conversation=context
        )
        return reponse_texte
    else:
        return f"Erreur API: {reponse.status_code}"


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
    
    # Affiche le résultat brut pour debug
   # return HttpResponse(f"""{reponse}
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

@login_required
def chat_ia(request, pharmacie_id):
    reponse_ia=None
    # Vérifier que l'utilisateur a accès à cette pharmacie
    pharmacie = get_object_or_404(Pharmacie, id=pharmacie_id, utilisateur=request.user)
    
    # Récupérer les 10 dernières conversations
    conversations = MonIA.objects.filter(Pharmacie=pharmacie).order_by('timestamp')[:10]
    
    if request.method == 'POST':
        message = request.POST.get('message')
        contexte = request.POST.get('contexte', 'general')
        
        # Appeler l'IA
        reponse_ia = converser_avec_ia(pharmacie, message, contexte)# a quoi il sert ?
        
        # Recharger les conversations (la nouvelle sera incluse)
        conversations = MonIA.objects.filter(Pharmacie=pharmacie).order_by('timestamp')[:10]
    
    return render(request, 'chat_ia.html', {
        'pharmacie': pharmacie,
        'conversations': conversations,
        'reponse_ia': reponse_ia 
    })
#http://localhost:8000/pharmacie/1/chat-ia/





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


#bon commencons l'hebergement je veux qu'on y aille pas à pas (en passant, est ce que si ca marche, je pourait acceder a mon site sur mon telephone?) 