from .models import Product
from django.contrib.auth.models import User
from django import forms
from .models import Profile

class AddressForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['address']
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse de livraison'}),
        }
        labels = {'address': 'Adresse de livraison'}

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name','price','stock','description','images']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control','placeholder':'Entrer le nom du produit'}),
            'price': forms.NumberInput(attrs={'class': 'form-control','placeholder':'Mettez votre prix'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control','placeholder':'Entrer la quantité'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,'placeholder':'Une petite description du produit'}),
            'images': forms.ClearableFileInput(attrs={'class': 'form-control'}),
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