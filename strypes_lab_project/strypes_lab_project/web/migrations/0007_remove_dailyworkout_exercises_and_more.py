# Generated by Django 5.0.6 on 2024-07-03 18:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0006_fitnessuser_tracker'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dailyworkout',
            name='exercises',
        ),
        migrations.RemoveField(
            model_name='dailyworkout',
            name='workout_plan',
        ),
        migrations.RemoveField(
            model_name='workoutplan',
            name='exercises',
        ),
        migrations.RemoveField(
            model_name='workoutplan',
            name='user',
        ),
        migrations.RemoveField(
            model_name='exercise',
            name='reps',
        ),
        migrations.RemoveField(
            model_name='exercise',
            name='sets',
        ),
        migrations.AddField(
            model_name='fitnessuser',
            name='goal',
            field=models.CharField(choices=[('strength', 'Strength'), ('endurance', 'Endurance'), ('muscle_gain', 'Muscle Gain'), ('get_toned', 'Get Toned')], default='strength', max_length=50),
        ),
        migrations.AddField(
            model_name='fitnessuser',
            name='height',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='fitnessuser',
            name='intensity',
            field=models.CharField(choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], default='medium', max_length=50),
        ),
        migrations.AddField(
            model_name='fitnessuser',
            name='weight',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Workout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('completed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WorkoutDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reps', models.IntegerField()),
                ('sets', models.IntegerField()),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.exercise')),
                ('workout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='web.workout')),
            ],
        ),
        migrations.DeleteModel(
            name='BMI',
        ),
        migrations.DeleteModel(
            name='DailyWorkout',
        ),
        migrations.DeleteModel(
            name='WorkoutPlan',
        ),
    ]
