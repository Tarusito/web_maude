# Generated by Django 5.0.2 on 2024-08-10 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Proyecto1', '0016_entrega_corregido_entrega_nota'),
    ]

    operations = [
        migrations.RenameField(
            model_name='entrega',
            old_name='fecha_entrega',
            new_name='fecha',
        ),
        migrations.AlterField(
            model_name='entrega',
            name='nota',
            field=models.TextField(blank=True, null=True),
        ),
    ]
