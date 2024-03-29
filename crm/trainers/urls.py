from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login_page'),
    path('login', views.log_in, name='login'),
    path('logout', views.log_out, name='logout'),
    path('main', views.main, name='main'),
    path('main/mark', views.mark, name='mark'),
    path('main/area_creation', views.area_creation, name='area_creation'),
    path('main/role_creation', views.role_creation, name='role_creation'),
    path('main/trainer_state_creation', views.trainer_state_creation, name='trainer_state_creation'),
    path('main/client_state_creation', views.client_state_creation, name='client_state_creation'),
    path('main/abonement_creation', views.abonement_creation, name='abonement_creation'),
    path('main/sport_type_creation', views.sport_type_creation, name='sport_type_creation'),
    path('clients', views.clients, name='clients'),
    path('client/<int:client_id>', views.client_info, name='client_info'),
    path('client/add/action', views.client_add_action, name='client_add_action'),
    path('clients/team_creation', views.team_creation, name='team_creation'),
    path('trainers', views.trainers, name='trainers'),
    path('trainers/add_action', views.trainers_add_action, name='trainers_add_action'),
    path('schedule', views.schedule, name='schedule')
    ]