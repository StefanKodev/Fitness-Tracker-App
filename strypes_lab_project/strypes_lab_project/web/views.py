import json
from datetime import date, timedelta, timezone, datetime

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy, reverse
from django.contrib.auth import views as auth_views, logout, login, get_user_model
from django.utils.dateparse import parse_date

from .models import Exercise, FitnessUser, Workout, WorkoutDetail
from django.views.generic import CreateView, ListView, DeleteView, UpdateView
from django.views import View, generic as views
from .forms import RegisterUserForm, EditProfileForm, ExerciseForm, BMICalculatorForm, FinishProfileForm
from django.contrib import messages
import requests
from django.contrib.auth.mixins import LoginRequiredMixin
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.neighbors import NearestNeighbors
from collections import Counter
# Create your views here.


class RegisterUserView(CreateView):
    template_name = 'web/create-profile.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('finish profile')

    def form_valid(self, form):
        if form.cleaned_data['password1'] != form.cleaned_data['password2']:
            messages.error(self.request, 'Passwords do not match. Please try again.')
            return self.form_invalid(form)

        result = super().form_valid(form)
        login(self.request, self.object)
        return redirect(reverse_lazy('finish profile'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['next'] = self.request.GET.get('next', '/')

        return context

    def get_success_url(self):
        return self.request.POST.get('next', self.success_url)


class AboutListView(ListView):
    model = FitnessUser
    template_name = 'web/about.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        trainerQueryset = FitnessUser.objects.filter(is_trainer=True)
        paginator = Paginator(trainerQueryset, 3)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context.update({
            'trainers': trainerQueryset,
            'paginator': paginator,
            'page_number': page_number,
            'page_obj': page_obj,
        })

        return context


class LoginUserView(auth_views.LoginView):
    template_name = 'web/log-in.html'

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)


def logout_user(request):
    logout(request)
    return redirect('home page')


@login_required(login_url='login user')
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('account details')
    else:
        form = EditProfileForm(instance=user)

    context = {
        'user': user,
        'form': form,
    }

    return render(request, 'web/edit_profile.html', context)

@login_required
def finish_profile(request):
    if request.method == 'POST':
        form = FinishProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('select_workout_preferences')
    else:
        form = FinishProfileForm(instance=request.user)

    return render(request, 'web/finish_profile.html', {'form': form})

@login_required(login_url='login user')
def account_details(request):
    user = request.user

    context = {
        'user': user,
    }

    return render(request, 'web/account_details.html', context)


class CheckUserWorkouts(LoginRequiredMixin, ListView):
    login_url = 'login user'
    model = Exercise
    template_name = 'web/workout_plans.html'
    context_object_name = 'exercises'
    paginate_by = 6


    def get_queryset(self):
        user = self.request.user
        selected_muscle_groups = user.selected_muscle_groups
        selected_equipment = user.selected_equipment

        workout_plans_by_muscle_group = {}
        for muscle_group in selected_muscle_groups:
            exercises_for_muscle_group = Exercise.objects.filter(body_part=muscle_group,
                                                                 equipment__in=selected_equipment)
            workout_plans_by_muscle_group[muscle_group] = exercises_for_muscle_group

        workout_plans_list = list(workout_plans_by_muscle_group.items())
        return workout_plans_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        selected_muscle_groups = user.selected_muscle_groups
        selected_equipment = user.selected_equipment

        all_exercises = Exercise.objects.filter(body_part__in=selected_muscle_groups, equipment=selected_equipment)

        workout_plans_by_muscle_group = {}

        for muscle_group in selected_muscle_groups:
            exercises_for_muscle_group = all_exercises.filter(body_part=muscle_group)
            workout_plans_by_muscle_group[muscle_group] = exercises_for_muscle_group

        today = str(datetime.now().date())
        context['workout_plans'] = workout_plans_by_muscle_group
        context['user'] = user
        tracker = user.tracker
        today_workout = tracker.get(today, {}).get('workout', None)
        context['today_workout'] = today_workout
        yesterday = str(datetime.now().date() - timedelta(days=1))
        yesterday_workout = tracker.get(yesterday, {}).get('workout', None)
        context['yesterday_workout'] = yesterday_workout

        # Paginate the list of muscle groups
        workout_plans_list = self.get_queryset()
        paginator = Paginator(workout_plans_list, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context.update({
            'user': user,
            'paginator': paginator,
            'page_obj': page_obj,
        })
        return context



@login_required
def calculate_bmi(request):
    if request.method == 'POST':
        form = BMICalculatorForm(request.POST)
        if form.is_valid():
            height = form.cleaned_data['height']
            weight = form.cleaned_data['weight']
            bmi = round(weight / (height ** 2), 2)
            today = str(datetime.now().date())
            user = request.user
            user.height = height
            user.weight = weight
            if today not in user.tracker:
                user.tracker[today] = {}
            if 'bmi' not in user.tracker[today]:
                user.tracker[today]['bmi'] = 0
            user.tracker[today]['bmi'] = bmi
            user.save()

            return redirect('home page')  # Replace 'profile' with your desired redirect URL
    else:
        form = BMICalculatorForm()

    return render(request, 'web/calculate_bmi.html', {'form': form})

@login_required
def select_workout_preferences(request):
    return render(request, 'web/select_workout.html')


@login_required
def save_workout_preferences(request):
    if request.method == 'POST':
        equipment = request.POST.get('equipment')
        muscle_groups = request.POST.getlist('muscle_groups')
        goal = request.POST.get('goal')
        intensity = request.POST.get('intensity')

        user_profile = request.user
        user_profile.selected_equipment = equipment
        user_profile.selected_muscle_groups = muscle_groups
        user_profile.goal = goal
        user_profile.intensity = intensity
        user_profile.save()

        if request.user.first_name is None:
            return redirect('edit profile')
        else:
            return redirect('home page')

    return redirect('select_workout_preferences')

"""
Unused
@login_required
def workout_plans(request):
    user = request.user
    selected_muscle_groups = user.selected_muscle_groups
    selected_equipment = user.selected_equipment

    all_exercises = Exercise.objects.filter(body_part__in=selected_muscle_groups, equipment=selected_equipment)


    workout_plans_by_muscle_group = {}


    for muscle_group in selected_muscle_groups:
        exercises_for_muscle_group = all_exercises.filter(body_part=muscle_group)
        workout_plans_by_muscle_group[muscle_group] = exercises_for_muscle_group

    print(workout_plans_by_muscle_group)

    return render(request, 'web/workout_plans.html', {'workout_plans': workout_plans_by_muscle_group, 'user': user})
"""

"""
Unused
@login_required(login_url='login user')
def select_workout(request):
    if request.method == 'POST':
        body_parts = request.POST.getlist('body_part')
        equipment = request.POST['equipment']

        user = request.user
        workout_plan = []
        day_counter = 1
        training_days = 0

        while training_days < len(body_parts) * 2:
            for body_part in body_parts:
                workout_plan_day = WorkoutPlan.objects.create(
                    user=user,
                    day_numer=day_counter,
                    body_part=body_part,
                    equipment=equipment,
                    date=date.today() + timedelta(days=day_counter-1)
                )

                exercises = Exercise.objects.filter(body_part=body_part, equipment=equipment)
                workout_plan_day.exercises.set(exercises)

                day_counter += 1
                training_days += 1

                if training_days > len(body_parts):
                    if training_days > 4:
                        WorkoutPlan.objects.create(user=user, day_numer=day_counter, body_part='Rest Day', equipment='None', date=date.today()+timedelta(days=day_counter-1))
                        day_counter += 1
                        WorkoutPlan.objects.create(user=user, day_number=day_counter, body_part='Rest Day',
                                                   equipment='None',  date=date.today() + timedelta(days=day_counter - 1))
                        day_counter += 1
                    else:
                        WorkoutPlan.objects.create(user=user, day_numer=day_counter, body_part='Rest Day',
                                                   equipment='None', date=date.today() + timedelta(days=day_counter-1))
                        day_counter += 1
                    training_days = 0

        return redirect('show_workout_plan')

    return render(request, 'web/select_workout.html')
"""
"""
@login_required(login_url='login user')
def workout_plan(request):
    user = request.user
    selected_muscle_groups = user.selected_muscle_groups
    selected_equipment = user.selected_equipment

    workout_plans = WorkoutPlan.objects.filter(user=request.user, body_part__in=selected_muscle_groups,
                                               equipment=selected_equipment)

    return render(request, 'web/workout_plans.html', {'workout_plans': workout_plans})

"""
"""
UNUSED
@login_required(login_url='login page')
def workout_details(request, muscle_group):
    user = request.user
    selected_equipment = user.selected_equipment

    today = str(datetime.now().date())
    yesterday = str(datetime.now().date() - timedelta(days=1))
    tracker = user.tracker
    today_workout = tracker.get(today, {}).get('workout', None)
    yesterday_workout = tracker.get(yesterday, {}).get('workout', None)

    exercises = Exercise.objects.filter(body_part=muscle_group, equipment=selected_equipment)

    return render(request, 'web/workout_details.html', {'muscle_group': muscle_group, 'exercises': exercises, 'today_workout': today_workout, 'yesterday_workout': yesterday_workout})


@login_required(login_url='login page')
def workout_history(request):
    user = request.user
    tracker = user.tracker or {}
    workout_history = []

    for date, data in tracker.items():
        if 'workout' in data:
            workout_history.append({
                'date': date,
                'workout': data['workout']
            })

    workout_history.sort(key=lambda x: x['date'], reverse=True)

    paginator = Paginator(workout_history, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }

    return render(request, 'web/workout_history.html', context)
"""

@login_required
def bmi_history(request):
    user = request.user
    tracker = user.tracker

    bmi_data = {}
    for date, data in tracker.items():
        if 'bmi' in data:
            bmi_data[date] = data['bmi']

    start_bmi = next(iter(bmi_data.values()), None)
    min_bmi_date, min_bmi = min(bmi_data.items(), key=lambda x: x[1], default=(None, None))
    max_bmi_date, max_bmi = max(bmi_data.items(), key=lambda x: x[1], default=(None, None))

    context = {
        'bmi_data': json.dumps(bmi_data),
        'start_bmi': start_bmi,
        'min_bmi': min_bmi,
        'min_bmi_date': min_bmi_date,
        'max_bmi': max_bmi,
        'max_bmi_date': max_bmi_date
    }
    return render(request, 'web/bmi_history.html', context)

"""
UNUSED
@login_required(login_url='login page')
def start_workout(request, muscle_group):
    user = request.user
    exercises = Exercise.objects.filter(body_part=muscle_group, equipment=user.selected_equipment)
    request.session['workout'] = {
        'muscle_group': muscle_group,
        'exercises': list(exercises.values('id', 'name', 'sets', 'reps')),
        'current_exercise': 0,
        'current_set': 1
    }
    return redirect('workout_session')


@login_required
def workout_session(request):
    workout = request.session.get('workout')
    if not workout:
        return redirect('workout_plans')

    exercise = workout['exercises'][workout['current_exercise']]
    break_time = request.session.get('break_time', False)

    context = {
        'exercise': exercise,
        'set': workout['current_set'],
        'break_time': break_time,
    }

    context['break_time'] = False

    if request.method == "POST":
        if break_time:
            request.session['break_time'] = False
        else:
            workout['current_set'] += 1
            if workout['current_set'] > exercise['sets']:
                workout['current_set'] = 1
                workout['current_exercise'] += 1
                if workout['current_exercise'] >= len(workout['exercises']):
                    save_workout_to_tracker(request, workout['muscle_group'])
                    return redirect('workout_completed')
            request.session['workout'] = workout
            request.session['break_time'] = True

        context['break_time'] = request.session['break_time']


    return render(request, 'web/workout_session.html', context)


@login_required
def workout_completed(request):
    return render(request, 'web/workout_completed.html')
"""

@login_required
def select_exercises(request, muscle_group):
    user = request.user
    if request.method == 'POST':
        workout = Workout.objects.create(user=request.user, muscle_group=muscle_group)
        exercises = request.POST.getlist('exercise[]')
        reps_list = request.POST.getlist('reps[]')
        sets_list = request.POST.getlist('sets[]')
        weights_list = request.POST.getlist('weight[]')

        for exercise, reps, sets, weight in zip(exercises, reps_list, sets_list, weights_list):
            exercise = Exercise.objects.get(id=exercise)
            if exercise.is_weighted and weight:
                weight = float(weight)
            else:
                weight = None
            WorkoutDetail.objects.create(workout=workout, exercise=exercise, reps=int(reps), sets=int(sets),
                                         weight=weight)
        workout.completed = True
        workout.save()
        return redirect('workout summary', workout_id=workout.id)
    exercises = Exercise.objects.filter(body_part=muscle_group, equipment=user.selected_equipment)
    return render(request, 'web/select_exercises.html', {'exercises': exercises, 'muscle_group': muscle_group})


@login_required
def recommended_exercises(request, muscle_group):
    if request.method == 'POST':
        workout = Workout.objects.create(user=request.user, muscle_group=muscle_group)
        exercises = request.POST.getlist('exercise[]')
        reps_list = request.POST.getlist('reps[]')
        sets_list = request.POST.getlist('sets[]')
        print(exercises)
        for exercise_id, reps, sets in zip(exercises, reps_list, sets_list):
            exercise = Exercise.objects.get(id=exercise_id)
            WorkoutDetail.objects.create(workout=workout, exercise=exercise, reps=int(reps), sets=int(sets))
        workout.completed = True
        workout.save()
        return redirect('workout summary', workout_id=workout.id)
    else:
        recommended_exercises_ids = recommendation_model(request.user.id, muscle_group)
        recommended_exs = Exercise.objects.filter(id__in=recommended_exercises_ids)
        print(recommended_exs)
        return render(request, 'web/recommended_exercises.html', {
            'recommended_exercises': recommended_exs,
            'muscle_group': muscle_group
        })



@login_required
def my_workouts(request):
    BODY_PART_CHOICES = [
        ('Arms', 'Arms'),
        ('Legs', 'Legs'),
        ('Abs', 'Abs'),
        ('Back', 'Back'),
        ('Shoulder', 'Shoulder'),
        ('Chest', 'Chest'),
        ('Butt', 'Butt'),
    ]

    selected_date = request.GET.get('date')


    muscle_group = request.GET.get('muscle_group')
    filters = {}
    workout_list = Workout.objects.filter(user=request.user).order_by('-date')
    if muscle_group:
        workout_list = Workout.objects.filter(user=request.user, muscle_group=muscle_group).order_by('-date')
        filters['muscle_group'] = muscle_group

    if selected_date:
        date = parse_date(selected_date)
        workout_list = workout_list.filter(date=date)
        filters['date'] = selected_date

    #workout_list = Workout.objects.filter(user=request.user).order_by('-date')
    paginator = Paginator(workout_list, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'web/my_workouts.html', {'page_obj': page_obj, 'muscle_groups': [choice[0] for choice in BODY_PART_CHOICES], 'muscle_group': muscle_group, 'filters': filters})

@login_required
def delete_workout(request, workout_id):
    if request.method == 'POST':
        workout = get_object_or_404(Workout, id=workout_id, user=request.user)
        workout.delete()
        return redirect('workout_history')
    return redirect('workout_history')

@login_required()
def workout_summary(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id)
    details = workout.details.all()
    print("workout details fetched:", details)
    return render(request, 'web/workout_summary.html', {'workout': workout, 'details': details, 'workout_id': workout_id})
"""
UNUSED
def save_workout_to_tracker(request, muscle_group):
    user = request.user
    today = str(datetime.now().date())
    workout = request.session.get('workout')
    if not workout:
        return
    if today not in user.tracker:
        user.tracker[today] = {}
    if 'workout' not in user.tracker[today]:
        user.tracker[today]['workout'] = []
    user.tracker[today]['workout'].append(muscle_group)
    user.save()
    del request.session['workout']
"""

"""UNUSED TO BE REMOVED
@login_required(login_url='login page')
def current_exercise(request):
    exercises = Exercise.objects.filter(id__in=request.session['exercises'])
    current_exercise_index = request.session['current_exercise']
    if current_exercise_index < len(exercises):
        current_exercise = exercises[current_exercise_index]
    else:
        return redirect('workout_complete')

    return render(request, 'web/current_exercise.html', {'exercise': current_exercise})

@login_required(login_url='login page')
def finish_exercise(request):
    request.session['current_exercise'] += 1
    return redirect('current_exercise')


@login_required(login_url='login page')
def workout_complete(request):
    workout_plan_id = request.session['workout_plan_id']
    workout_plan = get_object_or_404(WorkoutPlan, id=workout_plan_id)

    user_profile = request.user.profile
    workout_history = user_profile.workout_history

    # Get the current date
    date_str = timezone.now().strftime('%Y-%m-%d')

    # Save workout details to the workout history
    workout_details = {
        'body_part': workout_plan.body_part,
        'equipment': workout_plan.equipment,
        'exercises': [
            {
                'name': exercise.name,
                'sets': exercise.sets,
                'reps': exercise.reps
            }
            for exercise in workout_plan.exercises.all()
        ]
    }

    if date_str not in workout_history:
        workout_history[date_str] = []

    workout_history[date_str].append(workout_details)
    user_profile.workout_history = workout_history
    user_profile.save()

    del request.session['exercises']
    del request.session['current_exercise']
    del request.session['workout_plan_id']

    return render(request, 'web/workout_complete.html', {'workout_plan': workout_plan, 'date': timezone.now()})


@login_required(login_url='login user')
def show_workout_plan(request):
    user = request.user
    selected_muscle_groups = user.selected_muscle_groups
    selected_equipment = user.selected_equipment

    workout_plans = WorkoutPlan.objects.filter(user=user, body_part__in=selected_muscle_groups,
                                              equipment=selected_equipment)
    return render(request, 'web/workout_plans.html', {'workout_plans': workout_plans})

"""

def index(request):
    user = request.user
    city_name = 'Sofia'
    today = str(datetime.now().date())
    today_date = date.today()
    if user.is_authenticated:
        city_name = user.city if user.city else 'Sofia'

        today_workout_details = Workout.objects.filter(user=user, date=today).prefetch_related('details__exercise')
    else:
        today_workout_details = []
    muscle_groups_today = []
    for workout in today_workout_details:
        for detail in workout.details.all():
            if workout.muscle_group not in muscle_groups_today:
                muscle_groups_today.append(workout.muscle_group)

    weather = get_weather(city_name)
    if user.is_authenticated:
        tracker = user.tracker
    else:
        tracker = {}
    today_workout = tracker.get(today, {}).get('workout', None)
    today_bmi = tracker.get(today, {}).get('bmi', None)

    context = {
        'user': user,
        'temperature': weather['temperature'],
        'conditions': weather['conditions'],
        'city': weather['city'],
        'today_workout': muscle_groups_today,
        'today_bmi': today_bmi,
    }
    return render(request, 'web/index.html', context)


def get_weather(city):
    city_name = city
    api_key = '0bea6ab1ab03451986c03403233008'
    url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={city_name}'

    response = requests.get(url)
    data = response.json()

    if 'error' in data:
        city_name = 'Sofia'
        response = requests.get(f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={city_name}')
        data = response.json()

    temperature = data['current']['temp_c']
    conditions = data['current']['condition']['text']

    return {'temperature': temperature, 'conditions': conditions, 'city': city_name}


def is_trainer(user):
    return user.is_authenticated and user.is_trainer


@user_passes_test(is_trainer)
def add_exercise(request):
    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_exercises')
    else:
        form = ExerciseForm()
    return render(request, 'web/add_exercise.html', {'form': form})


@user_passes_test(is_trainer)
def manage_exercises(request):
    muscle_group = request.GET.get('muscle_group')
    filters = {}
    if muscle_group:
        exercises = Exercise.objects.filter(body_part=muscle_group)
        filters['muscle_group'] = muscle_group
    else:
        exercises = Exercise.objects.all()

    paginator = Paginator(exercises, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    muscle_groups = Exercise.objects.values_list('body_part', flat=True).distinct()

    context = {
        'exercises': page_obj,
        'page_obj': page_obj,
        'muscle_groups': muscle_groups,
        'filters': filters,
    }
    return render(request, 'web/manage_exercises.html', context)


@user_passes_test(is_trainer)
def edit_exercise(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    if request.method == 'POST':
        form = ExerciseForm(request.POST, instance=exercise)
        if form.is_valid():
            form.save()
            return redirect('manage_exercises')
    else:
        form = ExerciseForm(instance=exercise)
    return render(request, 'web/edit_exercise.html', {'form': form})


@user_passes_test(is_trainer)
def remove_exercise(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    exercise.delete()
    return redirect('manage_exercises')


def recommendation_model(user_id, selected_muscle_group):
    user = get_user_model()
    current_user = FitnessUser.objects.get(pk=user_id)
    current_user_equipment = current_user.selected_equipment
    print(current_user_equipment)
    users = list(FitnessUser.objects.filter(is_trainer=False).values('id', 'age', 'height', 'weight', 'intensity', 'goal'))

    user_ids = [user['id'] for user in users]

    user_data = np.array([[user['age'], user['height'], user['weight'], user['intensity'], user['goal']] for user in users])

    """
    for user in users:
        user_data.append([
            user['age'],
            user['height'],
            user['weight'],
            user['intensity'],
            user['goal']
        ])
        """
    data_array = np.array(user_data)

    exercise_names = sorted(set(Exercise.objects.values_list('name', flat=True)))

    feature_names = ['age', 'height', 'weight', 'intensity', 'goal', *exercise_names]

    data_array = np.array(user_data)

    preproccessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), [0, 1, 2]),
            ('cat', OneHotEncoder(), [3, 4])
        ],
        remainder='passthrough'
    )

    data_transformed = preproccessor.fit_transform(user_data)

    knn = NearestNeighbors(n_neighbors=2, algorithm='brute', metric='cosine')
    knn.fit(data_transformed)

    def get_recommendation(user_id, selected_muscle_group, selected_equipment):
        user_index = user_ids.index(user_id) if user_id in user_ids else None

        if user_index is None:
            return "User not found"

        distances, indices = knn.kneighbors([data_transformed[user_index]])

        recommended_exercises = []
        print(indices)
        print(user_ids)
        for idx in indices[0]:
            neighbor_id = user_ids[idx]
            neighbor_exercises = WorkoutDetail.objects.filter(
                workout__user_id=neighbor_id,
                exercise__body_part=selected_muscle_group,
                exercise__equipment=current_user_equipment,
            ).values_list('exercise__id', flat=True)
            recommended_exercises.extend(neighbor_exercises)

        to_recommend = (Counter(recommended_exercises).most_common(4))
        recommended_names = [exercise[0] for exercise in to_recommend]
        print(recommended_names)
        return recommended_names

    recommendations = get_recommendation(user_id, selected_muscle_group, current_user_equipment)
    print(recommendations)
    return recommendations


"""UNUSED
def display_recommendations(request, selected_muscle_group):
    user_id = request.user.id
    print(user_id)
    recommendations = recommendation_model(user_id, selected_muscle_group)
    return render(request, 'web/recommendations.html', {'recommendations' : recommendations})
    
    """