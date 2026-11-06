# Pillanatpapír

A **Pillanatpapír** egy Django-alapú, magyar nyelvű webalkalmazás hitelügyintézéshez és építkezési projektek pénzügyi adminisztrációjához. Segítségével a számlák és a hozzájuk tartozó PDF-dokumentumok egy helyen kezelhetők, az építkezés költségei pedig projektenként és munkafolyamatonként követhetők.

## Főbb funkciók

- regisztráció, e-mailes bejelentkezés, jelszó-visszaállítás és opcionális Google-belépés;
- felhasználónként elkülönített projekt- és számlaadatok;
- teljes projektkeret és munkafolyamatonkénti **zsebek** kezelése;
- számlák rögzítése, szerkesztése, keresése, szűrése és státusz szerinti kezelése;
- számlákhoz PDF-fájl feltöltése és megtekintése;
- PDF-ek szövegének kinyerése beágyazott szövegből vagy OCR-rel;
- a számla dátumának, adószámának és bruttó összegének összevetése a PDF tartalmával;
- költségösszesítők és vizuális keretkihasználtsági kimutatások;
- számlák exportja ZIP-csomagba, zsebek szerinti mappákkal és Excel-összesítővel;
- opcionális, Ollama-alapú magyar nyelvű házfelújítási segéd (Blinky).

## Technológiai háttér

- Python és Django
- SQLite fejlesztési adatbázis
- PyMuPDF, Pillow és Tesseract OCR a PDF-feldolgozáshoz
- `openpyxl` az Excel-exporthoz
- Ollama a helyi AI-segédhez
- Google Identity Services a Google-belépéshez

## Projekt felépítése

```text
pillanatpapir/
├── README.md
├── pillanatpapir/
│   ├── manage.py              # Django kezelőparancsok
│   ├── db.sqlite3             # fejlesztési adatbázis
│   ├── media/                 # feltöltött számla-PDF-ek
│   ├── hitelugyintezo/        # fő Django-alkalmazás
│   │   ├── models.py          # profilok, projektek, zsebek, számlák
│   │   ├── views.py           # oldalak, műveletek és exportok
│   │   ├── forms.py           # regisztrációs és számlaűrlapok
│   │   ├── ocr.py             # PDF-szövegkinyerés és ellenőrzés
│   │   ├── templates/         # HTML-sablonok
│   │   └── migrations/        # adatbázis-migrációk
│   └── pillanatpapir/         # Django-projektbeállítások
│       ├── settings.py
│       └── urls.py
└── .gitignore
```

## Telepítés és indítás

A parancsokat a projekt gyökeréből, vagyis abból a könyvtárból kell futtatni, ahol ez a README található.

### 1. Virtuális környezet létrehozása

Windows PowerShell:

```powershell
cd pillanatpapir
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
cd pillanatpapir
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Python-csomagok telepítése

```bash
pip install django google-auth openpyxl ollama pymupdf pytesseract pillow argon2-cffi
```

Az OCR-funkcióhoz külön telepíteni kell a [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) programot és a magyar nyelvi csomagot (`hun`). A Tesseract elérési útja a `TESSERACT_CMD` környezeti változóval állítható.

### 3. Adatbázis előkészítése és fejlesztői szerver

```bash
cd pillanatpapir
python manage.py migrate
python manage.py runserver
```

Az alkalmazás alapértelmezés szerint a <http://127.0.0.1:8000/> címen érhető el.

## Környezeti változók

Fejlesztéskor a projekt alapértelmezett beállításokkal is elindul. Éles környezetben legalább a titkos kulcsot és az engedélyezett hostokat meg kell adni.

| Változó | Leírás |
| --- | --- |
| `DJANGO_SECRET_KEY` | Django titkos kulcs; éles környezetben kötelező |
| `DJANGO_DEBUG` | `1` fejlesztéshez, `0` éles módhoz |
| `DJANGO_ALLOWED_HOSTS` | Éles módban engedélyezett hostok, vesszővel elválasztva |
| `GOOGLE_CLIENT_ID` | Opcionális Google OAuth kliensazonosító |
| `TESSERACT_CMD` | A Tesseract futtatható fájljának elérési útja |
| `OLLAMA_HOST` | Ollama címe, alapértelmezés: `http://127.0.0.1:11434` |
| `OLLAMA_MODEL` | Használt modell, alapértelmezés: `qwen2.5:7b` |

Az AI-segéd használatához telepített és futó Ollama szükséges, valamint a beállított modellnek is elérhetőnek kell lennie, például:

```bash
ollama pull qwen2.5:7b
```

## Adatbiztonsági megjegyzés

A számlák és a feltöltött PDF-ek felhasználónként vannak elválasztva. Éles használat előtt gondoskodni kell a titkos kulcsok biztonságos kezeléséről, HTTPS-ről, rendszeres adatbázis- és `media/`-mentésről, valamint az SQLite helyett a környezetnek megfelelő éles adatbázis használatáról.

## Tesztelés

```bash
cd pillanatpapir
python manage.py test
```

## Állapot

A projekt fejlesztés alatt áll. A README a jelenlegi kódszerkezetet és a már elérhető funkciókat dokumentálja.
