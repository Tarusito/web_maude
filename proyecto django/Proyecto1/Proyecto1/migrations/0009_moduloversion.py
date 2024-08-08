# Generated by Django 5.0.2 on 2024-08-08 15:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Proyecto1', '0008_alter_modulo_imagen'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModuloVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=100)),
                ('codigo', models.TextField()),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Proyecto1.chat')),
            ],
        ),
    ]