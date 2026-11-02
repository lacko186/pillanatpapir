from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('hitelugyintezo', '0010_dokumentumok_ocr_allapot_dokumentumok_ocr_jegyzet')]
    operations = [
        migrations.AddField('projekt', 'tulajdonos', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='projektjei', to=settings.AUTH_USER_MODEL)),
        migrations.AddField('zseb', 'tulajdonos', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='zsebei', to=settings.AUTH_USER_MODEL)),
        migrations.AddField('dokumentumok', 'tulajdonos', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='szamlai', to=settings.AUTH_USER_MODEL)),
    ]
