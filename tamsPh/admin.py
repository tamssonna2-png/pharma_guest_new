from django.contrib import admin
from .models import Medicament, Specialiste, Pharmacie

# Register your models here.
@admin.register(Medicament)
class MedicamentAdmin(admin.ModelAdmin):
    list_display = ['nom', 'categorie', 'quantite', 'prix']
    list_filter = ['categorie']
    search_fields = ['nom']

@admin.register(Specialiste)
class SpecialisteAdmin(admin.ModelAdmin):
    list_display = ['nom', 'specialite', 'Disponible']
    list_filter = ['specialite', 'Disponible']
    search_fields = ['nom']

@admin.register(Pharmacie)
class PharmacieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'zone', 'deGarde']
    list_filter = ['zone', 'deGarde']
    search_fields = ['nom']