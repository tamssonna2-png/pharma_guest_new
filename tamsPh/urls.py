# tamsPh/urls.py (FICHIER DE L'APPLICATION)

from django.urls import path
from django.views.generic import RedirectView
from . import views # Maintenant, cette ligne est correcte ! Elle importe les vues de l'application tamsPh

urlpatterns = [
    # Définition de l'URL pour la recherche de proximité
    path('', views.accueil, name='accueil'),
    path('pharmacies-proximite/', views.index, name='recherche_pharmacies_gps'),
    path('mes-medicaments/', views.mes_medicaments_connecte, name='mes_medicaments_perso'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('ajouter-medicament/', views.ajouter_medicament, name='ajouter_medicament'),
    path('supprimer-medicament/<int:medicament_id>/', views.supprimer_medicament, name='supprimer_medicament'),
    path('modifier-medicament/<int:medicament_id>/', views.modifier_medicament, name='modifier_medicament'),
    path('inscription/', views.inscription_pharmacie, name='inscription'),
    path('resultat-rechercher-medicament-pharmacie/',views.rechercher_medicament,name='Recherche_medicament_pharmacie'),
    path('recherche-medicament-pharmacie/', views.rechercher_medicament_page, name='recherche_medicament_page'),
    path('rechercher-medicament-client/', views.medicament_client, name='rechercher_medicament_client'),
    path('medicament-client-recherche/',views.medicament_client_recherche,name='medicament_client_recherche'),
    path('info-pharamcie/<int:pharmacie_id>/',views.info_pharmacie,name='info_pharmacie'),
    path('modif-info-pharmacie/',views.modifier_pharmacie,name='modifier_pharmacie'),
    path('accounts/profile/', RedirectView.as_view(url='/mes-medicaments/')),

    #path('recherche-ia/', views.recherche_intelligente, name='recherche_ia'),
    path('recherche-ia/', views.recherche_intelligente_pharmacie, name='recherche_ia'),
    #path('tableau-bord-ia/', views.tableau_bord_ia, name='tableau_bord_ia'),
    path('tableau-bord-ia/', views.tableau_bord_pharmacien, name='tableau_bord_ia'),
    # path('accueil/', views.index, name='index'), # Exemple d'une autre URL
    #path('test-ia/', views.test_ia, name='test_ia'),
    #path('lister-modeles',views.lister_modeles,name='lister_modeles'),
    path('pharmacie/<int:pharmacie_id>/chat-ia/', views.chat_ia, name='chat_ia'),
]
