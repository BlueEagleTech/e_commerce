from django.contrib import admin
from .models import Product
from .models import Cart, CartItem
# Register your models here.



@admin.register(Product)

#une classe ProductAdmin qui hérite du model Product pour personnaliser sa visualisation dans page admin
class ProductAdmin(admin.ModelAdmin):
    #les colonnes à afficher
    list_display = ['name','price','stock','created_at','id']
    #champ de recherches
    list_search = ['name','description']
    #filtre latéral
    list_filter=['created_at']

# Enregistrement du modèle Cart dans l'admin
class CartItemInline(admin.TabularInline):  # Utilisation de TabularInline pour afficher les éléments dans le même formulaire
    model = CartItem
    extra = 0  # Nombre d'items à ajouter par défaut

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'is_ordered', 'ordered_at')  # Champs à afficher dans la liste
    search_fields = ('user__username',)  # Recherche par nom d'utilisateur
    inlines = [CartItemInline]  # Afficher les CartItems associés sous le formulaire du panier

# Enregistrement des modèles dans l'admin
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem)


