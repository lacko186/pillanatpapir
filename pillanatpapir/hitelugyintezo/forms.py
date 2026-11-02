from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.core.validators import RegexValidator
from django.db.models import Q
from .models import Dokumentumok, Zseb


User = get_user_model()


class RegisterForm(forms.Form):
    nev = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=150)
    password1 = forms.CharField(strip=False)
    password2 = forms.CharField(strip=False)

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(username__iexact=email).exists():
            raise ValidationError('Ezzel az e-mail-címmel már van fiók.')
        return email

    def clean(self):
        data = super().clean()
        p1, p2 = data.get('password1'), data.get('password2')
        if p1 and p2:
            if p1 != p2:
                raise ValidationError('A két jelszó nem egyezik.')
            email = data.get('email', '')
            # a Django jelszó-szabályai: min. hossz, túl gyakori jelszavak, csak számok stb.
            validate_password(p1, user=User(username=email, email=email))
        return data

MEZOK = ['szamlaszama', 'szamla_azonosito', 'kivitelezo', 'szamla_kelte',
         'adoszam', 'afa', 'szamla_brutto_osszege', 'pdf']
PDF_MAX_BAJT = 10 * 1024 * 1024


class SzamlaForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        data = super().clean()
        if not data:
            return data
        qs = Dokumentumok.objects.filter(
            kivitelezo__iexact=data.get('kivitelezo', '').strip(),
            szamla_azonosito__iexact=data.get('szamla_azonosito', '').strip(),
            szamla_brutto_osszege=data.get('szamla_brutto_osszege'),
        )
        if self.user is not None:
            qs = qs.filter(tulajdonos=self.user)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Ez a számla már szerepel a nyilvántartásban (azonosító, kiállító és összeg alapján).')
        if data.get('szamlaszama') is not None and data['szamlaszama'] < 1:
            self.add_error('szamlaszama', 'A számlaszámnak pozitív egész számnak kell lennie.')
        if data.get('szamla_brutto_osszege') is not None and data['szamla_brutto_osszege'] < 0:
            self.add_error('szamla_brutto_osszege', 'Az összeg nem lehet negatív.')
        return data

    class Meta:
        model = Dokumentumok
        fields = MEZOK

    def clean_pdf(self):
        f = self.cleaned_data.get('pdf')
        # csak az újonnan feltöltött fájlt ellenőrizzük
        if isinstance(f, UploadedFile):
            if f.size > PDF_MAX_BAJT:
                raise ValidationError('A PDF legfeljebb 10 MB lehet.')
            if not f.name.lower().endswith('.pdf'):
                raise ValidationError('Csak PDF fájl tölthető fel.')
            fejlec = f.read(5)
            f.seek(0)
            if fejlec != b'%PDF-':
                raise ValidationError('A fájl tartalma nem érvényes PDF.')
            # A fejléc önmagában hamisítható; a PDF-parserrel is ellenőrizzük.
            try:
                import fitz
                doc = fitz.open(stream=f.read(), filetype='pdf')
                if doc.page_count > 200:
                    raise ValidationError('A PDF legfeljebb 200 oldalas lehet.')
                doc.close()
            except ValidationError:
                raise
            except Exception as exc:
                raise ValidationError('A PDF nem olvasható vagy sérült.') from exc
            finally:
                f.seek(0)
        return f


class UjSzamlaForm(SzamlaForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, user=user, **kwargs)
        self.fields['zseb'].queryset = Zseb.objects.filter(aktiv=True, tulajdonos=user)
    class Meta(SzamlaForm.Meta):
        fields = MEZOK + ['zseb', 'statusz']
