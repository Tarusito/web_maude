# Generated by Django 5.0.2 on 2024-08-09 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Proyecto1', '0011_chat_titulo_modulo_mensaje_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='mensaje',
            name='titulo_modulo',
            field=models.CharField(default='Desconocido', max_length=255),
        ),
    ]
