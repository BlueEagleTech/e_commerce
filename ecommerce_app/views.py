from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.views import LogoutView
from .models import Product,CartItem,Cart,Order
from .forms import ProductForm,SignUpForm
from .forms import AddressForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from e_commerce import settings
from django.contrib import messages
# Create your views here.

#DASHBOARD
@login_required
def dashboard(request):
    if request.user.is_staff:
         if request.user.profile.role in ['vendeur', 'admin']:
            total_products = Product.objects.count()
            total_clients = User.objects.count()
            produits = Product.objects.all()
            commandes = Cart.objects.count()
            return render(request, 'ecommerce_app/vendeur_dashboard.html', {
                "total_products": total_products,
                "total_orders": commandes,
                "total_clients": total_clients
            })
    else:
        # Accès client
        return redirect('ecom_app:index')


########################################PAGE INDEX SELECTIF############################################
def index(request):
    if request.user.profile.role in ['vendeur', 'admin']:
        return redirect("ecom_app:dashboard")
    product = Product.objects.all()
    return render(request,'ecommerce_app/liste.html',{'products':product})

########################################PAGE PROFILE POUR LES CLIENTS####################################
def profile(request):
    product = Product.objects.all()
    return render(request,'ecommerce_app/liste.html',{'products':product})

#DETAIL D'UN PRODUIT
def product_detail(request,product_id):
    product = get_object_or_404(Product,id = product_id)
    return render(request,'ecommerce_app/detail.html',{'product':product})

#AJOUTER UN PRODUIT
@login_required
def ajout_produit(request):
    if request.user.is_staff:
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
               product = form.save(commit=False)  # ne sauvegarde pas encore
               product.user = request.user       # lie le produit à l'utilisateur
               product.save()
               form.save()
               return redirect('ecom_app:index')
            
        else:
            form = ProductForm()
        return render(request,'ecommerce_app/ajout.html',{'form':form})
    else:
        return redirect('ecom_app:profile')

#MODIFIER UN PRODUIT
@login_required
def update_product(request,product_id):
    product = get_object_or_404(Product,id= product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        form.save()
        return redirect('ecom_app:index')
    else:
        form = ProductForm(instance=product)
        return render(request,'ecommerce_app/update.html',{'form':form,'product':product})


#SUPPRIMER UN PRODUIT
@login_required
def delete_product(request,product_id):
    product = get_object_or_404(Product,id=product_id)
    if request.method== 'POST':
        product.delete()
        return redirect('ecom_app:index')
    else:
        form = ProductForm(instance=product)
        return render(request,'ecommerce_app/delete.html',{'form':form,'product':product})
    
#VUE D'INSCRIPTION
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
    cart = Cart.objects.filter(user=request.user, is_ordered=False).first()
    if not cart:
        return redirect('ecom_app:index')

    # Pré-remplir le formulaire avec l'adresse existante
    profile = request.user.profile
    form = AddressForm(instance=profile)

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            # Confirmer le panier
            cart.confirm_order()
            return redirect('ecom_app:panier')  # ou page confirmation

    return render(request, 'ecommerce_app/panier.html', {'cart': cart, 'form': form})

@login_required
def validate_cart(request):
    cart = Cart.objects.filter(user=request.user, is_ordered=False).first()

    if not cart:
        # Si aucun panier n'existe, on redirige vers la page d'accueil
        return redirect('ecom_app:index')

    # Valider la commande et réduire le stock
    try:
        cart.confirm_order()  # ← c’est ici que le stock diminue
    except ValueError as e:
        # Gérer le cas où le stock est insuffisant
        return render(request, 'ecommerce_app/order_error.html', {'error': str(e)})

    # Envoi de l'email à l'administrateur
    send_mail(
        subject=f'Nouvelle commande de {cart.user.username}',
        message=f"Un utilisateur a validé une commande.\n\nDétails de la commande :\n\n" +
                "\n".join([f"{item.quantity} x {item.product.name} - {item.get_total_price()}€" for item in cart.items.all()]) +
                f"\n\nTotal de la commande : {cart.get_total_price()}€",
        from_email=settings.EMAIL_HOST_USER,  # L'email qui envoie
        recipient_list=[settings.ADMIN_EMAIL],  # L'email de l'admin
    )

    
    # Renvoyer une réponse qui confirme la commande
    return render(request, 'ecommerce_app/order_success.html', {'cart': cart})
##############################################VUE POUR DASHBOARD########################################
################################################MANIPULER LES PRODUITS#################################
def liste_produits(request):
    if request.user.profile.role != "admin":
        return redirect("ecom_app:index")
    products = Product.objects.all()
    return render(request,'ecommerce_app/dashboard/produits.html',{'products':products})

def liste_clients(request):
    if request.user.profile.role != "admin":
        return redirect("ecom_app:index")
    clients = User.objects.all()
    return render(request,'ecommerce_app/dashboard/clients.html',{'clients':clients})

def liste_commandes(request):
    if request.user.profile.role not in ['vendeur', 'admin']:
        return redirect('ecom_app:profile')

    commandes = Cart.objects.all().order_by('-created_at')

    # Vérifier si on a demandé de marquer une commande comme livrée
    if request.method == "POST":
        cart_id = request.POST.get('cart_id')
        cart = get_object_or_404(Cart, id=cart_id)
        try:
            cart.mark_as_delivered()
        except ValueError as e:
            # tu peux gérer un message flash ici si besoin
            pass
        return redirect('ecom_app:commandes')

    return render(request, 'ecommerce_app/dashboard/commandes.html', {'commandes': commandes})


#def parametre(request):
    if request.user.profile.role != "admin":
        return redirect("ecom_app:index")
    return render(request,'ecommerce_app/dashboard/parametre.html')
##############################################MANIPULER LES PRODUITS#################################
##############################################MANIPULER LES COMMANDES################################

##############################################MANIPULER LES COMMANDES################################
##############################################VUE POUR DASHBOARD########################################
#---------------------------------------------CREATION DES API--------------------------------------------------------------

#API D'INSCRIPTIONS
