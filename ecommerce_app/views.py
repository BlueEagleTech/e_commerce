from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.views import LogoutView
from .models import Product,CartItem,Cart,Order,Commentaire
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
    return render(request,'ecommerce_app/Accueil1.html',{'products':product})

########################################PAGE PROFILE POUR LES CLIENTS####################################
def profile(request):
    produits = Product.objects.all()
    return render(request,'ecommerce_app/Accueil1.html',{'produits':produits})

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
               product = form.save(commit=False)
               product.user = request.user
               product.save()  # c'est suffisant
               return redirect('ecom_app:index')
        else:
            form = ProductForm()
        return render(request,'ecommerce_app/ajout.html',{'form':form})
    else:
        return redirect('ecom_app:profile')


# MODIFIER UN PRODUIT
@login_required
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('ecom_app:index')
    else:
        form = ProductForm(instance=product)

    context = {
        'form': form,
        'product': product
    }
    return render(request, 'ecommerce_app/update.html', context)


# SUPPRIMER UN PRODUIT
@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product.delete()
        return redirect('ecom_app:index')

    context = {
        'product': product
    }
    return render(request, 'ecommerce_app/delete.html', context)    


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
    
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user, is_ordered=False)
    else:
        # Panier invité stocké dans session
        cart_id = request.session.get('guest_cart_id')
        if cart_id:
            cart = Cart.objects.filter(id=cart_id, is_ordered=False).first()
        else:
            cart = Cart.objects.create(is_ordered=False)
            request.session['guest_cart_id'] = cart.id

    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
        

    return redirect('ecom_app:blog')



def view_cart(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_ordered=False).first()
        form = AddressForm(instance=request.user.profile)
    else:
        cart_id = request.session.get('guest_cart_id')
        cart = Cart.objects.filter(id=cart_id, is_ordered=False).first() if cart_id else None
        form = None

    if not cart or not cart.items.exists():
        return redirect('ecom_app:index')

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = AddressForm(request.POST, instance=request.user.profile)
            if form.is_valid():
                form.save()
        else:
            # Remplir les champs guest_* depuis POST
            cart.guest_name = request.POST.get('name')
            cart.guest_email = request.POST.get('email')
            cart.guest_address = request.POST.get('address')
            cart.guest_phone = request.POST.get('phone')
            cart.save()

        # Confirmer la commande
        cart.confirm_order()
        return redirect('ecom_app:valider')  # page confirmation

    return render(request, 'ecommerce_app/panier.html', {'cart': cart, 'form': form})

def remove_from_cart(request, item_id):
    if request.user.is_authenticated:
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    else:
        cart_id = request.session.get('guest_cart_id')
        cart = Cart.objects.filter(id=cart_id, is_ordered=False).first()
        item = get_object_or_404(CartItem, id=item_id, cart=cart)

    item.delete()
    messages.success(request, f"❌ {item.product.name} a été retiré du panier.")
    return redirect('ecom_app:panier')


def validate_cart(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_ordered=False).first()
    else:
        cart_id = request.session.get('guest_cart_id')
        cart = Cart.objects.filter(id=cart_id, is_ordered=False).first() if cart_id else None

    if not cart:
        return redirect('ecom_app:index')

    try:
        cart.confirm_order()
    except ValueError as e:
        return render(request, 'ecommerce_app/order_error.html', {'error': str(e)})

    # Préparer les infos client
    client_info = f"{cart.user.username}" if cart.user else f"{cart.guest_name} ({cart.guest_email})"

    # Email à l'admin
    send_mail(
        subject=f'Nouvelle commande de {client_info}',
        message=f"Détails de la commande :\n" +
                "\n".join([f"{item.quantity} x {item.product.name} - {item.get_total_price()}€" for item in cart.items.all()]) +
                f"\n\nTotal : {cart.get_total_price()}€",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.ADMIN_EMAIL],
    )

    return render(request, 'ecommerce_app/order_success.html', {'cart': cart})
##############################################VUE POUR DASHBOARD########################################
################################################MANIPULER LES PRODUITS#################################
def liste_produits(request):
    if request.user.is_authenticated and request.user.profile.role != "vendeur":
        return redirect("ecom_app:index")
    produits = Product.objects.all()
    return render(request,'ecommerce_app/dashboard/produits.html',{'produits':produits})

def liste_clients(request):
    if request.user.profile.role == "acheteur":
        return redirect("ecom_app:index")
    clients = User.objects.filter(profile__role='acheteur').order_by('-date_joined')
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

#############################
########BLOG PRODUCT#########
#############################
def blog(request):
    produits = Product.objects.filter(is_active=True)  # tous les produits actifs

    context = {
        'produits': produits,
    }
    return render(request, 'ecommerce_app/blog.html', context)

##############################################MANIPULER LES PRODUITS#################################
##############################################MANIPULER LES COMMANDES################################

##############################################MANIPULER LES COMMANDES################################
##############################################VUE POUR DASHBOARD########################################
#---------------------------------------------CREATION DES API--------------------------------------------------------------

#API D'INSCRIPTIONS


#####################################
#########CONTACT ET COMMENTAIRES#####
#####################################
def contact(request):
    commentaire = Commentaire.objects.all()
    return render(request,'ecommerce_app/Contact.html',{'commentaire':commentaire})

def commentaire(request):
    if request.method == 'POST':
        nom = request.POST['nom']
        email = request.POST['email']
        message = request.POST['message']
        if nom and message:
            Commentaire.objects.create(nom=nom,email=email,message=message)
            return redirect('ecom_app:Contact')
    return redirect('ecom_app:Contact')

def a_propos(request):
    return render(request,'ecommerce_app/Apropos.html')