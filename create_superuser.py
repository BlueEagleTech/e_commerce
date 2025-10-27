# create_superuser.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "e_commerce.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username="Admin").exists():
    User.objects.create_superuser("Admin", "mba898127@gmail.com", "@lkr33m66")
    print("Superuser créé !")
else:
    print("Le superuser existe déjà.")
