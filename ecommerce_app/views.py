from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.views import LogoutView
from .models import Product,CartItem,Cart
from .forms import ProductForm,SignUpForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from e_commerce import settings
from django.contrib import messages
# Create your views here.

@login_required
def dashboard(request):
    if request.user.is_staff:
        # Accès admin
        return render(request, 'admin_dashboard.html')
    else:
        # Accès client
        return render(request, 'client_dashboard.html')

def index(request):
    product = Product.objects.all()
    return render(request,'ecommerce_app/liste.html',{'products':product})

def profile(request):
    product = Product.objects.all()
    return render(request,'ecommerce_app/liste.html',{'products':product})  

def product_detail(request,product_id):
    product = get_object_or_404(Product,id = product_id)
    return render(request,'ecommerce_app/detail.html',{'product':product})

@login_required
def ajout_produit(request):
    if request.user.is_staff:
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('ecom_app:index')
        else:
                form = ProductForm()
        return render(request,'ecommerce_app/ajout.html',{'form':form})


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = User.objects.create_user(username=username, email=email, password=password)
            messages.success(request,'Votre compte a été créé avec succés !')
            return redirect('ecom_app:connexion')  # Redirection vers la page de connexion
        else:
            messages.error(request,"Les informations fournies sont invalides")
            form = SignUpForm()
            return render(request, 'ecommerce_app/inscription.html', {'form': form})
    else:
        form = SignUpForm()
         

    return render(request, 'ecommerce_app/inscription.html', {'form': form})




class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Vous avez été déconnecté avec succès.")
        return super().dispatch(request, *args, **kwargs)
    
@login_required
def add_to_cart(request, product_id):
    # Récupérer le produit spécifique à partir de son ID
    product = get_object_or_404(Product, id=product_id)

    # Récupérer ou créer un panier pour l'utilisateur (panier non validé)
    cart, created = Cart.objects.get_or_create(user=request.user, is_ordered=False)

    # Vérifier si le produit existe déjà dans le panier
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    # Si le produit existe déjà, on augmente la quantité
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    # Redirection vers la page produit ou la page d'accueil après ajout au panier
    return redirect('ecom_app:index')


@login_required
def view_cart(request):
    # Récupérer le panier de l'utilisateur, s'il existe et n'est pas encore validé
    cart = Cart.objects.filter(user=request.user, is_ordered=False).first()

    # Si aucun panier n'est trouvé, on peut afficher un message ou rediriger vers la page d'accueil
    if not cart:
        return redirect('ecom_app:index')

    # Renvoyer le panier à la vue
    return render(request, 'ecommerce_app/panier.html', {'cart': cart})

@login_required
def validate_cart(request):
    cart = Cart.objects.filter(user=request.user, is_ordered=False).first()

    if not cart:
        # Si aucun panier n'existe, on redirige vers la page d'accueil
        return redirect('ecom_app:index')

    # Marquer le panier comme validé (commande confirmée)
    cart.is_ordered = True
    cart.ordered_at = timezone.now()  # Ajouter la date et heure de la commande
    cart.save()

    # Envoi de l'email à l'administrateur
    send_mail(
        subject=f'Nouvelle commande de {cart.user.username}',
        message=f"Un utilisateur a validé une commande.\n\nDétails de la commande :\n\n" +
                "\n".join([f"{item.quantity} x {item.product.name} - {item.get_total_price()}€" for item in cart.items.all()]) +
                f"\n\nTotal de la commande : {cart.get_total_price()}€",
        from_email=settings.EMAIL_HOST_USER,  # L'email qui envoie
        recipient_list=[settings.ADMIN_EMAIL],  # L'email de l'admin
    )

    # Ici tu peux ajouter une logique pour envoyer un email à l'admin, enregistrer la commande en base, etc.

    # Renvoyer une réponse qui confirme la commande
    return render(request, 'ecommerce_app/order_success.html', {'cart': cart})