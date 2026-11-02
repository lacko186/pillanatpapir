from django.contrib import admin
from .models import Dokumentumok, Zseb, Projekt
from .models import Profil

admin.site.register(Profil)
admin.site.register(Dokumentumok)
admin.site.register(Zseb)
admin.site.register(Projekt)