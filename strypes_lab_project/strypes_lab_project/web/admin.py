from django.contrib import admin
from django.contrib.auth import get_user_model
from .forms import UserAdminForm, ExerciseAdminForm
from .models import Exercise


# Register your models here.

UserModel = get_user_model()

@admin.register(UserModel)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'gender', 'selected_equipment',
                    'selected_muscle_groups', 'city', 'is_trainer', 'goal', 'intensity', 'height', 'weight', 'tracker')

    search_fields = ('username', 'email', 'first_name', 'last_name', 'gender', 'tracker')
    ordering = ('-is_trainer',)
    form = UserAdminForm


@admin.register(Exercise)
class ExerciseModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'body_part', 'equipment')
    list_filter = ('name', 'body_part', 'equipment',)
    search_fields = ('name', 'body_part', 'equipment')
    ordering = ('name',)
    form = ExerciseAdminForm
