# Generated by Django 5.1.5 on 2025-06-26 18:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_app', '0006_alter_associationprofile_logo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='annonce',
            name='association',
        ),
        migrations.AddField(
            model_name='annonce',
            name='id_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='annonces', to=settings.AUTH_USER_MODEL),
        ),
    ]
