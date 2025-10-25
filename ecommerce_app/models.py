from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
# Create your models here.
User = get_user_model()



from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):

    # Catégories possibles
    CATEGORY_CHOICES = [
        ('maquillage', 'Maquillage'),
        ('creme_beaute', 'Crème de Beauté'),
        ('vetement', 'Vêtement'),
        ('accessoire', 'Accessoire'),
        ('parfum', 'Parfum'), 
        ('soin_cheveux', 'Soin Cheveux'),
        ('chaussure', 'Chaussure'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    images = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='vetement')
    featured = models.BooleanField(default=False)  # pour mettre en avant certains produits
    is_active = models.BooleanField(default=True)  # utile si le produit n'est plus disponible
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # pour savoir quand le produit a été modifié
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    date_ordered = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'En attente'),
            ('confirmed', 'Confirmée'),
            ('shipped', 'Expédiée'),
            ('delivered', 'Livrée'),
            ('cancelled', 'Annulée'),
        ],
        default='pending'
    )

    def __str__(self):
        return f"Commande {self.id} - {self.user.username}"  
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_ordered = models.BooleanField(default=False)
    ordered_at = models.DateTimeField(null=True, blank=True)
    is_delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(null=True, blank=True)

    # Champs pour invités
    guest_name = models.CharField(max_length=255, blank=True, null=True)
    guest_email = models.EmailField(blank=True, null=True)
    guest_address = models.TextField(blank=True, null=True)
    guest_phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Panier de {self.user.username if self.user else self.guest_name or 'Invité'}"

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())
    
    def confirm_order(self):
        if self.is_ordered:
            raise ValueError("Cette commande a déjà été validée.")

        with transaction.atomic():
            for item in self.items.select_related('product').all():
                if item.quantity > item.product.stock:
                    raise ValueError(f"Stock insuffisant pour {item.product.name}")
                item.product.stock -= item.quantity
                item.product.save()

            self.is_ordered = True
            self.ordered_at = timezone.now()
            self.save()

    
    def mark_as_delivered(self):
        """Marquer la commande comme livrée"""
        if not self.is_ordered:
            raise ValueError("Cette commande n'a pas encore été validée.")
        if self.is_delivered:
            raise ValueError("Cette commande a déjà été livrée.")
        self.is_delivered = True
        self.delivered_at = timezone.now()
        self.save()
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        return self.product.price * self.quantity

class Profile(models.Model):
    ROLE_CHOICES = (
        ('acheteur', 'Acheteur'),
        ('vendeur', 'Vendeur'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='acheteur')
    address = models.CharField(max_length=255, blank=True, null=True)  # ⚡ Nouveau
    numero = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    

class Commentaire(models.Model):
    nom = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)