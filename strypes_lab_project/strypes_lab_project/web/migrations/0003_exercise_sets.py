# Generated by Django 5.0.6 on 2024-06-28 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_exercise_reps'),
    ]

    operations = [
        migrations.AddField(
            model_name='exercise',
            name='sets',
            field=models.IntegerField(default=4),
            preserve_default=False,
        ),
    ]