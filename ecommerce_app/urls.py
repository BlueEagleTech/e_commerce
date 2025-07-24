
from django.urls import path
from django.contrib.auth.views import LoginView,LogoutView
from . import views

app_name="ecom_app"


urlpatterns = [
    path('',views.index,name="index"),
    path('détail/<int:product_id>/',views.product_detail,name="détail"),
    path('ajout/',views.ajout_produit,name="ajout"),
    path('inscriptions/',views.signup,name="signup"),
    path('connexion/',LoginView.as_view(),name="connexion"),
    path('déconnexion/',views.CustomLogoutView.as_view(next_page='ecom_app:connexion'),name="déconnexion"),
    path('profile/', views.profile, name='profile'),
    path('achat/<int:product_id>/',views.add_to_cart,name="achat"),
    path('panier',views.view_cart,name="panier"),
    path('valider-panier/', views.validate_cart, name='valider'),  # Vue pour valider le panier
     
]