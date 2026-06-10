from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommendations', '0017_plan_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='appuser',
            name='password',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
