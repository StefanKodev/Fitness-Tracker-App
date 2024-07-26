from datetime import datetime, timedelta
from enum import Enum
from django.contrib.auth import models as auth_models, get_user_model
import json
from django.db import models
from django.core import validators
from strypes_lab_project.web.validators import validate_only_letters_in_name
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Gender(Enum):
    MALE = 1
    FEMALE = 2
    OTHER = 3

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]

class FitnessUser(auth_models.AbstractUser):
    FIRST_NAME_MIN_LENGTH = 2
    LAST_NAME_MIN_LENGTH = 2
    FIRST_NAME_MAX_LENGTH = 30
    LAST_NAME_MAX_LENGTH = 30

    GOAL_CHOICES = [
        ('strength', 'Strength'),
        ('endurance', 'Endurance'),
        ('muscle_gain', 'Muscle Gain'),
        ('get_toned', 'Get Toned'),
    ]

    INTENSITY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    first_name = models.CharField(
        max_length=FIRST_NAME_MAX_LENGTH,
        validators=(
            validators.MinLengthValidator(FIRST_NAME_MIN_LENGTH,
                                          message=f"Name cannot be less than {FIRST_NAME_MIN_LENGTH} symbols!"),
            validators.MaxLengthValidator(FIRST_NAME_MAX_LENGTH,
                                          message=f"Name cannot be more than {FIRST_NAME_MAX_LENGTH} symbols!"),
            validate_only_letters_in_name,
        )
    )

    last_name = models.CharField(
        max_length=LAST_NAME_MAX_LENGTH,
        validators=(
            validators.MinLengthValidator(LAST_NAME_MIN_LENGTH,
                                          message=f"Name cannot be less than {LAST_NAME_MIN_LENGTH} symbols!"),
            validators.MaxLengthValidator(LAST_NAME_MAX_LENGTH,
                                          message=f"Name cannot be more than {LAST_NAME_MAX_LENGTH} symbols!"),
            validate_only_letters_in_name,
        )
    )

    email = models.EmailField(
        unique=True
    )

    gender = models.IntegerField(
        choices=Gender.choices(),
        default=Gender.OTHER.value,
    )

    is_trainer = models.BooleanField(
        default=False,
    )

    city = models.CharField(max_length=60, blank=True)

    selected_equipment = models.CharField(max_length=20, blank=True)
    selected_muscle_groups = models.JSONField(default=list, blank=True)

    goal = models.CharField(max_length=50, choices=GOAL_CHOICES, default='strength')
    intensity = models.CharField(max_length=50, choices=INTENSITY_CHOICES, default='medium')

    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)

    workout_history = models.JSONField(default=dict, blank=True)

    tracker = models.JSONField(default=dict, blank=True)

    def update_tracker(self, day, muscle_groups):
        tracker = json.loads(self.tracker)
        if day not in tracker:
            tracker[day] = {'workout': muscle_groups}
        else:
            if 'workout' not in tracker[day]:
                tracker[day]['workout'] = []
            tracker[day]['workout'].extend(muscle_groups)
        self.tracker = json.dumps(tracker)
        self.save()

    def get_yesterday_workout(self):
        today = datetime.now().date()
        yesterday = str(today - timedelta(days=1))
        tracker = json.loads(self.tracker)
        return tracker.get(yesterday, {}).get('workout', None)

    def __str__(self):
        return f"{self.first_name}, {self.last_name}"

class Exercise(models.Model):
    BODY_PART_CHOICES = [
        ('Arms', 'Arms'),
        ('Legs', 'Legs'),
        ('Abs', 'Abs'),
        ('Back', 'Back'),
        ('Shoulder', 'Shoulder'),
        ('Chest', 'Chest'),
        ('Butt', 'Butt'),
    ]

    EQUIPMENT_CHOICES = [
        ('Body weight', 'Body weight'),
        ('Fitness equipment', 'Fitness equipment'),
    ]

    name = models.CharField(max_length=50)
    body_part = models.CharField(max_length=50, choices=BODY_PART_CHOICES)
    equipment = models.CharField(max_length=50, choices=EQUIPMENT_CHOICES)
    is_weighted = models.BooleanField(default=False)
    weight = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name

class Workout(models.Model):
    user = models.ForeignKey(FitnessUser, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    muscle_group = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Workout on {self.date} by {self.user.username}"


class WorkoutDetail(models.Model):
    workout = models.ForeignKey(Workout, related_name='details', on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    reps = models.IntegerField()
    sets = models.IntegerField()
    weight = models.FloatField(null=True, blank=True)

    def __str__(self):
        print(self.exercise.is_weighted)
        if self.exercise.is_weighted:
            return f"{self.exercise.name} - {self.sets} sets of {self.reps} at {self.weight} kg."
        else:
            return f"{self.exercise.name} - {self.sets} sets of {self.reps}"

