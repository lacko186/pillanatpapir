from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from hitelugyintezo import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('szamlak/', views.dokumentumok_listaja, name='dokumentumok_listaja'),
    path('export/zip/', views.export_zip, name='export_zip'),
    path('ai/kerdes/', views.ai_kerdes, name='ai_kerdes'),
    path('kijelentkezes/', views.kijelentkezes, name='kijelentkezes'),
    path('szamla/<int:pk>/pdf/', views.szamla_pdf, name='szamla_pdf'),
    path('auth/google/', views.google_login, name='google_login'),
    path(
        'jelszo-visszaallitas/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='password_reset_confirm.html',
            success_url='/?ok=jelszo',   # sima szöveg, nem reverse_lazy
        ),
        name='password_reset_confirm',
    ),
]