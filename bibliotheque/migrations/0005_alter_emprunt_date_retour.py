# Generated by Django 5.2 on 2025-05-01 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bibliotheque', '0004_book_genre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emprunt',
            name='date_retour',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
