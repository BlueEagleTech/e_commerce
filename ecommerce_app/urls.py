
from django.urls import path
from django.contrib.auth.views import LoginView,LogoutView
from . import views

app_name="ecom_app"


urlpatterns = [
    path('',views.profile,name="index"),
    path('détail/<int:product_id>/',views.product_detail,name="détail"),
    path('update/<int:product_id>/',views.update_product,name="update"),
    path('delete/<int:product_id>/',views.delete_product,name="delete"),
    path('ajout/',views.ajout_produit,name="ajout"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/produits', views.liste_produits, name='produits'),
    path('dashboard/clients', views.liste_clients, name='clients'),
    path('dashboard/commandes', views.liste_commandes, name='commandes'),
    #path('dashboard/parametre', views.parametre, name='parametre'),
    path('inscriptions/',views.signup,name="signup"),
    path('connexion/',LoginView.as_view(),name="connexion"),
    path('déconnexion/',views.CustomLogoutView.as_view(next_page='ecom_app:connexion'),name="déconnexion"),
    path('profile/', views.profile, name='profile'),
    path('achat/<int:product_id>/',views.add_to_cart,name="achat"),
    path('panier',views.view_cart,name="panier"),
    path('valider-panier/', views.validate_cart, name='valider'),  # Vue pour valider le panier
     
]