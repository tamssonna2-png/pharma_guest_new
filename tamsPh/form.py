from django import forms
from django.contrib.auth.models import User
from .models import Medicament

class MedicamentForm(forms.ModelForm):
    class Meta:
        model = Medicament
        fields = ['nom', 'categorie', 'description', 'quantite', 'prix', 'image']


class InscriptionPharmacieForm(forms.Form):
    # Informations de la pharmacie
    nom_pharmacie = forms.CharField(max_length=280, label="Nom de la pharmacie")
    address = forms.CharField(max_length=280, label="Adresse")
    zone = forms.CharField(max_length=280, label="Zone/Quartier")
    
    latitude = forms.FloatField(
        widget=forms.HiddenInput(),
        required=False,
        label="Latitude"
    )
    longitude = forms.FloatField(
        widget=forms.HiddenInput(),
        required=False,
        label="Longitude"
    )

    # Informations de connexion
    username = forms.CharField(max_length=150, label="Nom d'utilisateur")
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password != confirm_password:
            raise forms.ValidationError("Les mots de passe ne correspondent pas")
        
        # Vérifier si l'username existe déjà
        if User.objects.filter(username=cleaned_data.get("username")).exists():
            raise forms.ValidationError("Ce nom d'utilisateur existe déjà")