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
from django.forms.widgets import TextInput      
class InscriptionClient(forms.Form):
    username = forms.CharField(max_length=150, label="Nom d'utilisateur")
    address = forms.CharField(max_length=280, label="Adresse")
    zone = forms.CharField(max_length=280, label="Zone/Quartier")
    date_naissance = forms.DateField(label="Date de naissance",required=False,
        widget=forms.DateInput(attrs={'placeholder': 'JJ/MM/AAAA', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'])
    numero=forms.CharField(max_length=280, label="Numero")
    # Informations de connexion
    email = forms.EmailField(
        label="Email",
        widget=TextInput(
            attrs={
                'placeholder': 'Entrer une adresse email valide',
                'class': 'form-control-custom' # Optionnel, si vous avez des classes CSS
            }
        )
    )
    password = forms.CharField(widget=forms.PasswordInput, 
        required=False,  # Mot de passe facultatif
        help_text="Laissez vide si vous ne voulez pas de mot de passe")#pas obligatoire
    confirm_password = forms.CharField(widget=forms.PasswordInput, 
        required=False)
    notifications_email = forms.BooleanField(label="Via email")
    notifications_sms =forms.BooleanField(label="Via SMS")
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password= cleaned_data.get("confirm_password")
        
        # Vérifier que les mots de passe correspondent si fournis
        if password and password != confirm_password:
            raise forms.ValidationError("Les mots de passe ne correspondent pas")
        
        return cleaned_data

from tamsPh.models import Specialiste

class InscriptionPersonel(forms.ModelForm):
    """nom_personel=forms.CharField(max_length=280,label="NOM")
    prenom_personel=forms.CharField(max_length=280,label="PRENOM")
    specialite=forms.CharField(max_length=280,label="SPECIALITE OU FONCTION")
    photo=forms.ImageField(
        label="PHOTO",
        required=False,  # Si facultatif
        help_text="Téléchargez votre photo (format JPG, PNG)"
    )"""
    class Meta:
        model = Specialiste
        fields = ['nom', 'prenom', 'specialite', 'photo']
        labels = {
            'nom': 'NOM',
            'prenom': 'PRENOM', 
            'specialite': 'SPECIALITE OU FONCTION',
            'photo': 'PHOTO'
        }
