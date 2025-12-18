# tamsPh/urls.py (FICHIER DE L'APPLICATION)

from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
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
    path('rechercher-medicament-client/', views.medicament_client, name='rechercher_medicament_client'),
    path('info-pharamcie/<int:pharmacie_id>/',views.info_pharmacie,name='info_pharmacie'),
    path('modif-info-pharmacie/',views.modifier_pharmacie,name='modifier_pharmacie'),
    path('accounts/profile/', RedirectView.as_view(url='/mes-medicaments/')),

    #path('recherche-ia/', views.recherche_intelligente, name='recherche_ia'),
    path('recherche-ia/', views.recherche_intelligente_pharmacie, name='recherche_ia'),
    #path('tableau-bord-ia/', views.tableau_bord_ia, name='tableau_bord_ia'),
    path('tableau-bord-ia/', views.tableau_bord_pharmacien, name='tableau_bord_ia'),
    # path('accueil/', views.index, name='index'), # Exemple d'une autre URL
    path('test-ia/', views.test_ia, name='test_ia'),
    path('lister-modeles',views.lister_modeles,name='lister_modeles'),
    path('pharmacie/<int:pharmacie_id>/chat-ia/', views.chat_ia, name='chat_ia'),
    path('inscription-personel/',views.inscription_personel,name='inscription_personel'),
    path('info-personel/',views.info_personel,name='info_personel'),
    path('suprimer-personel/<int:personel_id>/',views.suprimer_personel,name='suprimer_personel'),
    path('modifier-personel/<int:personel_id>/',views.modifier_personel,name='modifier_personel'),
    path('fiche-personel/<int:personel_id>/',views.fiche_personel,name='fiche_personel'),
    path('commander/<int:pharmacie_id>/', views.passer_commande, name='passer_commande'),
    path('commander/<int:pharmacie_id>/<int:medicament_id>/',views.passer_commande,name='commande_rapide'),
    path('mes-commandes/', views.mes_commandes, name='mes_commandes'),
    path('commande/<int:commande_id>/annuler/', views.annuler_commande, name='annuler_commande'),
    path('commande/<int:commande_id>/pdf/', views.telecharger_commande_pdf, name='telecharger_commande_pdf'),
    path('commande/<int:commande_id>/', views.detail_commande, name='detail_commande'),
    path('pharmacie/commandes/', views.commandes_pharmacie, name='commandes_pharmacie'),
    path('commande/<int:commande_id>/<str:action>/', views.traiter_commande, name='traiter_commande'),
    path('inscription-client/<int:pharmacie_id>/',views.inscription_client,name='inscription_client'),
    path('connexion-rapide/<int:phar_id>/', views.connexion_rapide, name='connexion_rapide'), 
    path('notifications/', views.notifications_pharmacie, name='notifications_pharmacie'),
    path('commande/<int:commande_id>/accepter/', views.accepter_commande, name='accepter_commande'),
    path('commande/<int:commande_id>/refuser/', views.refuser_commande, name='refuser_commande'),
    path('notification/<int:notification_id>/supprimer/', views.supprimer_notification, name='supprimer_notification'),
    path('notifications/tout-supprimer/', views.supprimer_toutes_notifications, name='supprimer_toutes_notifications'),
    path('notifications/tout-marquer-lu/', views.marquer_toutes_lues, name='marquer_toutes_lues'),
    path('api/envoyer-email-commande/', views.envoyer_email_commande, name='envoyer_email_commande'),
    path('commandes/supprimer/<int:commande_id>/', views.supprimer_commande, name='supprimer_commande'),
    path('commandes/supprimer-toutes/', views.supprimer_toutes_commandes, name='supprimer_toutes_commandes'),
    path('commandes/marquer-recuperee/<int:commande_id>/', views.marquer_recuperee, name='marquer_recuperee'),
    path('commandes/historique/', views.historique_commandes, name='historique_commandes'),
    path('commandes/pdf/<int:commande_id>/', views.generer_pdf_commande, name='generer_pdf_commande'),
    path('test-email-config/', views.test_email_config, name='test_email_config'),
]
