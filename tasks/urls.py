from django.urls import include, path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list, name='task_list'),
path('register/', views.register, name='register'),
path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
path('complete/<int:task_id>/', views.complete_task, name='complete_task'),
path('complete/<int:task_id>/', views.complete_task, name='complete_task'),
path('withdraw/', views.withdraw_money, name='withdraw_money'),
path('claim-bonus/', views.claim_daily_bonus, name='claim_daily_bonus'),
path('submit-proof/<int:task_id>/', views.submit_task_proof, name='submit_task_proof'),
path('owner-dashboard/', views.admin_dashboard, name='admin_dashboard'),
path('approve-task/<int:completion_id>/', views.approve_task, name='approve_task'),
path('reject-task/<int:completion_id>/', views.reject_task, name='reject_task'),
path('approve-withdrawal/<int:withdrawal_id>/', views.approve_withdrawal, name='approve_withdrawal'),
path('accounts/', include('django.contrib.auth.urls')),
]