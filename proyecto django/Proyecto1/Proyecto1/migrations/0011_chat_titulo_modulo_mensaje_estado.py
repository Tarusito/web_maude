# Generated by Django 5.0.2 on 2024-08-09 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Proyecto1', '0010_alter_moduloversion_chat'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='titulo_modulo',
            field=models.CharField(default='Sin título', max_length=255),
        ),
        migrations.AddField(
            model_name='mensaje',
            name='estado',
            field=models.CharField(choices=[('ninguno', 'Ninguno'), ('bien', 'Bien'), ('mal', 'Mal')], default='ninguno', max_length=7),
        ),
    ]
