from .models import Product
from django.contrib.auth.models import User
from django import forms
from .models import Profile
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import Product

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': "Nom d'utilisateur"
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': "Mot de passe"
    }))

class AddressForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['address','numero']
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse de livraison'}),
            'numero':forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Numero de téléphone'})
        }
        labels = {'address': 'Adresse de livraison','nomero':'Numero de téléphone'}



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock', 'description', 'images', 'category', 'featured']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrer le nom du produit'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Mettez votre prix'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Entrer la quantité'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Une petite description du produit'}),
            'images': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Entrer un mot de passe'}))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Confirmer votre mot de passe'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control','placeholder':'Entrer un nom d\'utilisateur'}),
            'email': forms.EmailInput(attrs={'class': 'form-control','placeholder':'Entrer votre email'}),
            }

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password != password_confirm:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return password_confirm