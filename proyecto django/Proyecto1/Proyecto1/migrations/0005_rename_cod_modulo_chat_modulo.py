# Generated by Django 5.0.2 on 2024-03-18 12:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Proyecto1', '0004_alter_chat_cod_modulo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chat',
            old_name='cod_modulo',
            new_name='modulo',
        ),
    ]
