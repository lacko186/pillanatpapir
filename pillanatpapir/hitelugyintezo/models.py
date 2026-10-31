from django.db import models


class Projekt(models.Model):
    nev = models.CharField(max_length=100, default='Házfelújítás')
    osszkeret = models.PositiveBigIntegerField(default=10_000_000)
    alapzsebek_kesz = models.BooleanField(default=False)

    def __str__(self):
        return self.nev


class Zseb(models.Model):
    nev = models.CharField(max_length=100)
    keret = models.PositiveIntegerField(default=100000)
    szin = models.CharField(max_length=7, default='#2563eb')
    aktiv = models.BooleanField(default=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.nev


class Dokumentumok(models.Model):
    STATUSZ = [
        ('fizetve', 'Fizetve'),
        ('feldolgozas', 'Feldolgozás alatt'),
        ('folyamatban', 'Folyamatban'),
    ]

    # ↓↓↓ IDE A RÉGI MEZŐID (a tényleges típusokkal) ↓↓↓
    szamla_szama = models.CharField(max_length=100)
    szamla_azonosito = models.CharField(max_length=100, blank=True)
    kivitelezo = models.CharField(max_length=200)
    szamla_kelte = models.DateField(null=True, blank=True)
    adoszam = models.CharField(max_length=50, blank=True)
    afa = models.CharField(max_length=50, blank=True)
    szamla_brutto_osszege = models.CharField(max_length=50)

    zseb = models.ForeignKey(Zseb, null=True, blank=True,
                             on_delete=models.SET_NULL, related_name='szamlak')
    statusz = models.CharField(max_length=20, choices=STATUSZ, default='folyamatban')

    def __str__(self):
        return f'{self.szamla_szama} – {self.kivitelezo}'