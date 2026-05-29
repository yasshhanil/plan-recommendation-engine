from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommendations', '0014_remove_plan_plans_city_feff8f_idx_alter_plan_city'),
    ]

    operations = [
        migrations.CreateModel(
            name='Wishlister',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(db_index=True, max_length=254, unique=True)),
                ('city', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'wishlisters',
                'ordering': ['-created_at'],
            },
        ),
    ]
