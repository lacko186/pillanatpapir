from django.db import models
from datetime import date
from django.conf import settings
import uuid

class Profil(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='profil')
    nev = models.CharField(max_length=100)
    google_id = models.CharField(max_length=64, unique=True, null=True, blank=True)
    letrehozva = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nev


class Projekt(models.Model):
    tulajdonos = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='projektjei')
    nev = models.CharField(max_length=100, default='Házfelújítás')
    osszkeret = models.PositiveBigIntegerField(default=10_000_000)
    alapzsebek_kesz = models.BooleanField(default=False)

    def __str__(self):
        return self.nev


class Zseb(models.Model):
    tulajdonos = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='zsebei')
    nev = models.CharField(max_length=100)
    keret = models.PositiveIntegerField(default=100000)
    szin = models.CharField(max_length=7, default='#2563eb')
    aktiv = models.BooleanField(default=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.nev

def pdf_utvonal(instance, filename):
    return f'szamlak/{uuid.uuid4().hex}.pdf'


class Dokumentumok(models.Model):
    tulajdonos = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='szamlai')
    STATUSZ = [
        ('fizetve', 'Fizetve'),
        ('feldolgozas', 'Feldolgozás alatt'),
        ('folyamatban', 'Folyamatban'),
    ]
    OCR = [
        ('', 'Nincs ellenőrizve'),
        ('egyezik', 'PDF egyezik'),
        ('elteres', 'Eltérés a PDF-hez képest'),
        ('nem_olvashato', 'A PDF nem olvasható'),
    ]
    ocr_allapot = models.CharField(max_length=20, choices=OCR, blank=True, default='')
    ocr_jegyzet = models.TextField(blank=True, default='')



    szamlaszama = models.IntegerField(default=1)
    szamla_kelte = models.DateField(default=date.today)
    kivitelezo = models.CharField(max_length=100)
    adoszam = models.CharField(max_length=15)
    szamla_azonosito = models.CharField(max_length=100)
    afa = models.DecimalField(max_digits=5, decimal_places=2)
    szamla_brutto_osszege = models.IntegerField()

    zseb = models.ForeignKey(Zseb, null=True, blank=True,
                             on_delete=models.SET_NULL, related_name='szamlak')
    statusz = models.CharField(max_length=20, choices=STATUSZ, default='folyamatban')
    pdf = models.FileField(upload_to=pdf_utvonal, blank=True)

    def __str__(self) -> str:
        return f'Szamla - {self.kivitelezo}'
