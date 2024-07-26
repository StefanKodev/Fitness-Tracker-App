# Generated by Django 5.0.6 on 2024-06-28 16:41

import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import strypes_lab_project.web.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('body_part', models.CharField(choices=[('Arms', 'Arms'), ('Legs', 'Legs'), ('Abs', 'Abs'), ('Back', 'Back'), ('Shoulder', 'Shoulder'), ('Chest', 'Chest'), ('Butt', 'Butt')], max_length=50)),
                ('equipment', models.CharField(choices=[('Body weight', 'Body weight'), ('Fitness equipment', 'Fitness equipment')], max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='FitnessUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('first_name', models.CharField(max_length=30, validators=[django.core.validators.MinLengthValidator(2, message='Name cannot be less than 2 symbols!'), django.core.validators.MaxLengthValidator(30, message='Name cannot be more than 30 symbols!'), strypes_lab_project.web.validators.validate_only_letters_in_name])),
                ('last_name', models.CharField(max_length=30, validators=[django.core.validators.MinLengthValidator(2, message='Name cannot be less than 2 symbols!'), django.core.validators.MaxLengthValidator(30, message='Name cannot be more than 30 symbols!'), strypes_lab_project.web.validators.validate_only_letters_in_name])),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('gender', models.IntegerField(choices=[(1, 'MALE'), (2, 'FEMALE'), (3, 'OTHER')], default=3)),
                ('is_trainer', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='BMI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('height', models.FloatField()),
                ('weight', models.FloatField()),
                ('bmi', models.FloatField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WorkoutPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_numer', models.IntegerField()),
                ('body_part', models.CharField(choices=[('Arms', 'Arms'), ('Legs', 'Legs'), ('Abs', 'Abs'), ('Back', 'Back'), ('Shoulder', 'Shoulder'), ('Chest', 'Chest'), ('Butt', 'Butt')], max_length=50)),
                ('equipment', models.CharField(choices=[('Body weight', 'Body weight'), ('Fitness equipment', 'Fitness equipment')], max_length=50)),
                ('date', models.DateField()),
                ('exercises', models.ManyToManyField(to='web.exercise')),
                ('user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='user_plan', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DailyWorkout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('exercises', models.ManyToManyField(to='web.exercise')),
                ('workout_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.workoutplan')),
            ],
        ),
    ]
