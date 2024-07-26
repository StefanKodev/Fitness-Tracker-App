from django.urls import path, include
from strypes_lab_project.web.views import RegisterUserView, LoginUserView, index, AboutListView,\
    select_workout_preferences, save_workout_preferences,\
    logout_user, CheckUserWorkouts, edit_profile, account_details,\
    add_exercise, manage_exercises, edit_exercise, remove_exercise, calculate_bmi,\
    bmi_history, select_exercises, my_workouts, workout_summary, recommended_exercises, \
    delete_workout, finish_profile



urlpatterns = [
    path('', index, name='home page'),
    path('register/', RegisterUserView.as_view(), name='register user'),
    path('login/', LoginUserView.as_view(), name='login user'),
    path('logout/', logout_user, name='logout user'),
    path('about/', AboutListView.as_view(), name='about page'),
    path('select-workout-preferences/', select_workout_preferences, name='select_workout_preferences'),
    path('save-workout-preferences/', save_workout_preferences, name='save_workout_preferences'),
    path('workout-plans/', CheckUserWorkouts.as_view(), name='workout_plans'),
    #path('workout-details/<str:muscle_group>/', workout_details, name='workout_details'),
    #path('start-workout/<str:muscle_group>/', start_workout, name='start_workout'),
    #path('current-exercise/', current_exercise, name='current_exercise'),
    #path('finish-exercise/', finish_exercise, name='finish_exercise'),
    #path('workout-complete/', workout_complete, name='workout_complete'),
    path('edit_profile', edit_profile, name='edit profile'),
    path('account_details', account_details, name='account details'),
    path('add_exercise/', add_exercise, name='add_exercise'),
    path('manage-exercises/', manage_exercises, name='manage_exercises'),
    path('edit-exercise/<int:pk>/', edit_exercise, name='edit_exercise'),
    path('trainer/remove-exercise/<int:pk>/', remove_exercise, name='remove_exercise'),
    #path('workout_session/', workout_session, name='workout_session'),
    #path('workout_completed/', workout_completed, name='workout_completed'),
    path('calculate_bmi/', calculate_bmi, name='calculate_bmi'),
    path('my_workouts/', my_workouts, name='workout_history'),
    path('bmi-history/', bmi_history, name='bmi_history'),
    path('select_exercises/<str:muscle_group>/', select_exercises, name='select exercises'),
    #path('my_workouts/', my_workouts, name='my workouts'),
    path('workout-summary/<int:workout_id>', workout_summary, name='workout summary'),
    #path('recommendation_exercises/<str:selected_muscle_group>', display_recommendations, name='display recommendations'),
    path('recommended_exercises/<str:muscle_group>', recommended_exercises, name='recommended exercises'),
    path('delete_workout/<int:workout_id>/', delete_workout, name='delete_workout'),
    path('finish_profile', finish_profile, name='finish profile')
]
