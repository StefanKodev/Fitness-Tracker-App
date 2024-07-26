from django.contrib.auth import forms as auth_forms, get_user_model
from .models import Exercise, Workout, WorkoutDetail
from .validators import validate_only_letters_in_name
from django import forms

UserModel = get_user_model()


class RegisterUserForm(auth_forms.UserCreationForm):
    class Meta:
        model = UserModel
        fields = ('username', 'email', 'password1', 'password2')


class SelectWorkoutForm(forms.Form):
    EQUIPMENT_CHOICES = [
        ('Body weight', 'Body weight'),
        ('Fitness equipment', 'Fitness equipment'),
    ]

    equipment = forms.ChoiceField(choices=EQUIPMENT_CHOICES, widget=forms.RadioSelect)
    muscle_groups = forms.MultipleChoiceField(
        choices=[
            ('Arms', 'Arms'),
            ('Legs', 'Legs'),
            ('Abs', 'Abs'),
            ('Back', 'Back'),
            ('Shoulder', 'Shoulder'),
            ('Chest', 'Chest'),
            ('Butt', 'Butt'),
            ],
            widget=forms.CheckboxSelectMultiple
    )


class FinishProfileForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['first_name', 'last_name', 'height', 'weight', 'age', 'city']
        widgets = {
            'height': forms.NumberInput(attrs={'step': "0.01"}),
            'weight': forms.NumberInput(attrs={'step': "0.01"}),
            'age': forms.NumberInput(attrs={'min': "0", 'max': "100"}),
        }

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['username', 'first_name', 'last_name', 'email', 'gender', 'height', 'weight', 'age', 'city']


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'body_part', 'equipment', 'is_weighted']


class AccountDeleteConfirmForm(forms.Form):
    confirm_delete = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )


class BMICalculatorForm(forms.Form):
    height = forms.FloatField(label='Height (in meters)', min_value=0.1)
    weight = forms.FloatField(label='Weight (in kilograms)', min_value=1)

class UserAdminForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'gender', 'selected_equipment', 'selected_muscle_groups', 'city', 'is_trainer', 'tracker',
                  'height', 'weight', 'age', 'intensity', 'goal')

    def clean_first_name(self):
        validate_only_letters_in_name(self.cleaned_data["first_name"])

        return self.cleaned_data["first_name"]

    def clean_last_name(self):
        validate_only_letters_in_name(self.cleaned_data["last_name"])

        return self.cleaned_data["last_name"]


class ExerciseAdminForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = '__all__'