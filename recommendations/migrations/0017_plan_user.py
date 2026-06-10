import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommendations', '0016_appuser_authtoken'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='plans', to='recommendations.appuser'),
        ),
    ]
