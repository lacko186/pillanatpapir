from django.contrib import messages
from django.db.models import Prefetch
from django.forms import modelform_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Dokumentumok, Zseb, Projekt

MEZOK = ['szamla_szama', 'szamla_azonosito', 'kivitelezo', 'szamla_kelte',
         'adoszam', 'afa', 'szamla_brutto_osszege']

ZsebForm = modelform_factory(Zseb, fields=['nev', 'keret', 'szin'])
SzerkForm = modelform_factory(Dokumentumok, fields=MEZOK)
UjForm = modelform_factory(Dokumentumok, fields=MEZOK + ['zseb', 'statusz'])

STATUSZ_SZIN = {'fizetve': '#16a34a', 'feldolgozas': '#f59e0b', 'folyamatban': '#2563eb'}

# (név, javasolt keret, szín)
ALAPZSEBEK = [
    ('Bontás', 500000, '#78716c'),
    ('Tetőszerkezet', 1500000, '#b45309'),
    ('Falazás és vakolás', 1200000, '#a16207'),
    ('Nyílászárók', 1000000, '#0e7490'),
    ('Villanyszerelés', 800000, '#ca8a04'),
    ('Vízszerelés és fűtés', 1200000, '#0369a1'),
    ('Burkolás', 1000000, '#2563eb'),
    ('Festés és mázolás', 600000, '#be185d'),
    ('Asztalos munkák', 700000, '#92400e'),
    ('Kert és külső', 800000, '#15803d'),
    ('Egyéb', 700000, '#6b7280'),
]


def _projekt():
    projekt, _ = Projekt.objects.get_or_create(pk=1)
    if not projekt.alapzsebek_kesz:
        for nev, keret, szin in ALAPZSEBEK:
            # a már meglévő zseb (pl. Burkolás) aktív és érintetlen marad
            Zseb.objects.get_or_create(
                nev=nev, defaults={'keret': keret, 'szin': szin, 'aktiv': False})
        projekt.alapzsebek_kesz = True
        projekt.save(update_fields=['alapzsebek_kesz'])
    return projekt


def _szam(ertek):
    try:
        return float(str(ertek).replace(' ', '').replace(',', '.'))
    except (ValueError, TypeError):
        return 0.0


def _vissza(zseb_pk=None):
    url = reverse('dokumentumok_listaja')
    return redirect(f'{url}?zseb={zseb_pk}' if zseb_pk else url)


def _hiba(request, form):
    reszletek = '; '.join(f'{mezo}: {hibak[0]}' for mezo, hibak in form.errors.items())
    messages.error(request, f'Hibás adat, nem mentődött. {reszletek}')


def _diagram(szamlak, keret):
    """Közös számítás a zsebeknek és a teljes projektnek."""
    osszegek = {kulcs: 0.0 for kulcs, _ in Dokumentumok.STATUSZ}
    for sz in szamlak:
        osszegek[sz.statusz] = osszegek.get(sz.statusz, 0.0) + _szam(sz.szamla_brutto_osszege)

    osszes = sum(osszegek.values())
    nevezo = keret or 1
    skala = min(1.0, nevezo / osszes) if osszes else 1.0   # túllépésnél is 100%-ig rajzol

    reszek, kezdet = [], 0.0
    for kulcs, nev in Dokumentumok.STATUSZ:
        hossz = osszegek[kulcs] / nevezo * 100 * skala
        reszek.append({
            'kulcs': kulcs, 'nev': nev, 'szin': STATUSZ_SZIN[kulcs],
            'osszeg': osszegek[kulcs],
            'szazalek': round(osszegek[kulcs] / nevezo * 100),
            'hossz': f'{hossz:.2f}', 'offset': f'{-kezdet:.2f}',
        })
        kezdet += hossz

    return {
        'reszek': reszek, 'osszes': osszes, 'keret': keret,
        'szazalek': round(osszes / nevezo * 100),
        'fizetve_szazalek': round(osszegek['fizetve'] / nevezo * 100),
        'tullepve': osszes > keret,
        'kulonbseg': abs(keret - osszes),
    }


def dokumentumok_listaja(request):
    projekt = _projekt()

    if request.method == 'POST':
        action = request.POST.get('action')
        zseb_pk = None

        if action == 'osszkeret_mentes':
            try:
                uj = int(float(request.POST.get('osszkeret', '').replace(' ', '').replace(',', '.')))
                if uj < 0:
                    raise ValueError
                projekt.osszkeret = uj
                projekt.save(update_fields=['osszkeret'])
                messages.success(request, 'Az összes keret módosítva.')
            except ValueError:
                messages.error(request, 'Az összes keretnek pozitív számnak kell lennie.')

        elif action == 'aktival':
            zseb = get_object_or_404(Zseb, pk=request.POST.get('pk'))
            try:
                zseb.keret = max(0, int(float(request.POST.get('keret', zseb.keret))))
            except ValueError:
                pass
            zseb.aktiv = True
            zseb.save(update_fields=['keret', 'aktiv'])
            messages.success(request, f'A(z) {zseb.nev} zseb aktiválva.')
            zseb_pk = zseb.pk

        elif action == 'deaktival':
            zseb = get_object_or_404(Zseb, pk=request.POST.get('pk'))
            if zseb.szamlak.exists():
                messages.error(request, 'Ebben a zsebben még vannak számlák. Előbb helyezd át őket másik zsebbe.')
                zseb_pk = zseb.pk
            else:
                zseb.aktiv = False
                zseb.save(update_fields=['aktiv'])
                messages.success(request, f'A(z) {zseb.nev} zseb deaktiválva.')

        elif action == 'uj_zseb':
            form = ZsebForm(request.POST)
            if form.is_valid():
                zseb_pk = form.save().pk
                messages.success(request, 'Az új zseb létrejött.')
            else:
                _hiba(request, form)

        elif action == 'zseb_mentes':
            zseb = get_object_or_404(Zseb, pk=request.POST.get('pk'))
            form = ZsebForm(request.POST, instance=zseb)
            if form.is_valid():
                form.save()
                messages.success(request, 'A zseb módosítva.')
            else:
                _hiba(request, form)
            zseb_pk = zseb.pk

        elif action == 'zseb_torles':
            zseb = get_object_or_404(Zseb, pk=request.POST.get('pk'))
            zseb.delete()   # a számlák megmaradnak, besorolatlanok lesznek
            messages.success(request, 'A zseb törölve, a számlái besorolatlanok lettek.')

        elif action == 'uj_szamla':
            form = UjForm(request.POST)
            if form.is_valid():
                zseb_pk = form.save().zseb_id
                messages.success(request, 'A számla felvéve.')
            else:
                _hiba(request, form)
                zseb_pk = request.POST.get('zseb')

        elif action == 'szamla_mentes':
            sz = get_object_or_404(Dokumentumok, pk=request.POST.get('pk'))
            form = SzerkForm(request.POST, instance=sz)
            if form.is_valid():
                form.save()
                messages.success(request, 'A számla módosítva.')
            else:
                _hiba(request, form)
            zseb_pk = sz.zseb_id

        elif action == 'statusz':
            sz = get_object_or_404(Dokumentumok, pk=request.POST.get('pk'))
            uj = request.POST.get('statusz')
            if uj in dict(Dokumentumok.STATUSZ):
                sz.statusz = uj
                sz.save(update_fields=['statusz'])
            zseb_pk = sz.zseb_id

        elif action == 'athelyez':
            sz = get_object_or_404(Dokumentumok, pk=request.POST.get('pk'))
            sz.zseb = Zseb.objects.filter(pk=request.POST.get('zseb'), aktiv=True).first()
            sz.save(update_fields=['zseb'])
            messages.success(request, 'A számla áthelyezve.')
            zseb_pk = sz.zseb_id

        elif action == 'szamla_torles':
            sz = get_object_or_404(Dokumentumok, pk=request.POST.get('pk'))
            zseb_pk = sz.zseb_id
            sz.delete()
            messages.success(request, 'A számla törölve.')

        return _vissza(zseb_pk)

    szamla_lekerdezes = Dokumentumok.objects.order_by('-szamla_kelte', '-pk')
    aktiv = list(Zseb.objects.filter(aktiv=True)
                 .prefetch_related(Prefetch('szamlak', queryset=szamla_lekerdezes)))

    zsebek = []
    for z in aktiv:
        szamlak = list(z.szamlak.all())
        adat = _diagram(szamlak, z.keret)
        adat.update({'zseb': z, 'szamlak': szamlak})
        zsebek.append(adat)

    # Teljes projekt: minden számla (a besorolatlanok is), az összes kerethez mérve
    osszes_diagram = _diagram(list(szamla_lekerdezes), projekt.osszkeret)
    zsebekbe_osztva = sum(z.keret for z in aktiv)
    osszes_diagram.update({
        'zsebekbe_osztva': zsebekbe_osztva,
        'szabad_keret': projekt.osszkeret - zsebekbe_osztva,
        'szabad_abs': abs(projekt.osszkeret - zsebekbe_osztva),
        'tulosztva': zsebekbe_osztva > projekt.osszkeret,
    })

    return render(request, 'szamlak.html', {
        'projekt': projekt,
        'ossz': osszes_diagram,
        'zsebek': zsebek,
        'inaktiv': Zseb.objects.filter(aktiv=False),
        'zseb_lista': Zseb.objects.filter(aktiv=True),
        'besorolatlan': szamla_lekerdezes.filter(zseb__isnull=True),
        'statuszok': Dokumentumok.STATUSZ,
    })