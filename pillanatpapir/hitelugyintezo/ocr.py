import re
from datetime import date

import fitz  # PyMuPDF
import pytesseract
from django.conf import settings
from PIL import Image

if settings.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

MAX_OLDAL = 3


def szoveg_kinyeres(pdf_bajtok):
    """Előbb a beágyazott szöveg, ha nincs, akkor OCR."""
    doc = fitz.open(stream=pdf_bajtok, filetype='pdf')
    reszek = []
    for i, oldal in enumerate(doc):
        if i >= MAX_OLDAL:
            break
        szoveg = oldal.get_text().strip()
        if len(szoveg) < 40:
            pix = oldal.get_pixmap(dpi=200)
            kep = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
            szoveg = pytesseract.image_to_string(kep, lang='hun+eng', timeout=60)
        reszek.append(szoveg)
    return '\n'.join(reszek)


def adoszam_ervenyes(adoszam):
    """Ellenőrző számjegy: csak figyelmeztetés, nem tiltás."""
    jegyek = re.sub(r'\D', '', adoszam)[:8]
    if len(jegyek) != 8:
        return False
    suly = [9, 7, 3, 1, 9, 7, 3, 1]
    return sum(int(a) * b for a, b in zip(jegyek, suly)) % 10 == 0


def _osszegek(szoveg):
    tiszta = re.sub(r'(?<=\d)[ .\u00a0](?=\d{3}\b)', '', szoveg)   # ezres tagolás ki
    return {int(x) for x in re.findall(r'\d+', tiszta)}


def _datum_szerepel(szoveg, datum):
    if not isinstance(datum, date):
        return False
    tiszta = re.sub(r'\.\s+', '.', szoveg)
    alakok = [datum.strftime('%Y.%m.%d'), datum.strftime('%Y-%m-%d'), datum.strftime('%Y/%m/%d')]
    return any(a in tiszta for a in alakok)


def ellenoriz(szamla):
    """Visszaad: (allapot, jegyzet). A beírt adatokat veti össze a PDF-fel."""
    try:
        with szamla.pdf.open('rb') as f:
            szoveg = szoveg_kinyeres(f.read())
    except Exception:
        return 'nem_olvashato', 'A PDF-et nem sikerült beolvasni.'

    if len(szoveg.strip()) < 20:
        return 'nem_olvashato', 'A PDF-ből nem sikerült szöveget kinyerni.'

    hibak = []
    if not _datum_szerepel(szoveg, szamla.szamla_kelte):
        hibak.append('A számla kelte nem található a PDF-ben.')

    ado = re.sub(r'\D', '', szamla.adoszam)
    if len(ado) < 8 or ado[:8] not in re.sub(r'\D', '', szoveg):
        hibak.append('Az adószám nem található a PDF-ben.')
    if not adoszam_ervenyes(szamla.adoszam):
        hibak.append('Az adószám ellenőrző számjegye nem stimmel (elírás?).')

    if int(szamla.szamla_brutto_osszege) not in _osszegek(szoveg):
        hibak.append('A bruttó összeg nem található a PDF-ben.')

    if hibak:
        return 'elteres', ' '.join(hibak)
    return 'egyezik', 'A dátum, az adószám és az összeg megegyezik a PDF-fel.'