# Generated by Django 5.0.2 on 2024-08-10 18:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Proyecto1', '0014_entrega'),
    ]

    operations = [
        migrations.AddField(
            model_name='entrega',
            name='remitente',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='entregas_enviadas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='entrega',
            name='titulo',
            field=models.CharField(default='Nombre titulo default', max_length=255, verbose_name='Título de la Entrega'),
        ),
    ]
