# Generated by Django 5.0.3 on 2024-04-26 11:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Proyecto1', '0005_rename_cod_modulo_chat_modulo'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModuloMaude',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255, unique=True, verbose_name='Nombre del Módulo')),
                ('descripcion', models.TextField(verbose_name='Descripción')),
                ('codigo_maude', models.TextField(verbose_name='Código Maude')),
                ('imagen', models.ImageField(upload_to='modulos_maude', verbose_name='Imagen del Módulo')),
                ('activo', models.BooleanField(default=False, verbose_name='Activo para No Administradores')),
                ('creador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modulos_creados', to=settings.AUTH_USER_MODEL, verbose_name='Usuario Creador')),
            ],
        ),
    ]
