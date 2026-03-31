from django.urls import include, path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
    path('register/', views.register, name='register'),
path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='tasks/change_password.html', success_url='/profile/'), name='password_change'),
path('complete/<int:task_id>/', views.complete_task, name='complete_task'),
path('complete/<int:task_id>/', views.complete_task, name='complete_task'),
path('withdraw/', views.withdraw_money, name='withdraw_money'),
path('claim-bonus/', views.claim_daily_bonus, name='claim_daily_bonus'),
path('submit-proof/<int:task_id>/', views.submit_task_proof, name='submit_task_proof'),

]