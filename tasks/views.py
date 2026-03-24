from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Task, Profile, WithdrawalRequest, TaskCompletion
from decimal import Decimal
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import get_object_or_404 # Essential for finding the task
from .models import Task, TaskCompletion # Essential for saving the proof
from django.contrib.admin.views.decorators import staff_member_required
from datetime import timedelta
from django.contrib.admin.views.decorators import staff_member_required


# 1. DASHBOARD
@login_required
def task_list(request):
    all_tasks = Task.objects.all()
    user_profile, created = Profile.objects.get_or_create(user=request.user)
    
    # ADD THIS LINE RIGHT HERE:
    my_withdrawals = WithdrawalRequest.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'tasks/task_list.html', {
        'tasks': all_tasks,
        'profile': user_profile,
        'withdrawals': my_withdrawals # AND ADD THIS TO THE LIST
    })

# 2. COMPLETE TASKS
@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    user_profile = request.user.profile
    
    # Check if they already did this task
    already_done = TaskCompletion.objects.filter(user=request.user, task=task).exists()
    
    if not already_done:
        # Create a "receipt" so they can't do it again
        TaskCompletion.objects.create(user=request.user, task=task)
        # Give them the money
        user_profile.balance += task.reward
        user_profile.save()
        messages.success(request, f"Task completed! You earned {task.reward} ETB.")
    else:
        messages.warning(request, "You have already earned rewards for this task.")
        
    return redirect(task.link)

# 3. DAILY BONUS
@login_required
def claim_daily_bonus(request):
    user_profile = request.user.profile
    now = timezone.now()

    # Check if they have claimed it in the last 24 hours
    if user_profile.last_bonus_date:
        if now < user_profile.last_bonus_date + timedelta(hours=24):
            messages.error(request, "You already claimed your bonus today! Come back tomorrow.")
            return redirect('tasks:task_list')

    # If it's their first time or 24 hours have passed:
    user_profile.balance += Decimal('1.00')
    user_profile.last_bonus_date = now
    user_profile.save()

    messages.success(request, "1.00 ETB added to your balance!")
    return redirect('tasks:task_list')
# 4. WITHDRAW
@login_required
def withdraw_money(request):
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount'))
        phone = request.POST.get('phone_number')
        user_profile = request.user.profile 

        if user_profile.balance >= amount:
            WithdrawalRequest.objects.create(user=request.user, amount=amount, phone_number=phone)
            user_profile.balance -= amount
            user_profile.save()
            messages.success(request, "Withdrawal request sent!")
        else:
            messages.error(request, "Insufficient balance.")
        return redirect('tasks:task_list')
    return render(request, 'tasks/withdraw.html')

# 5. REGISTER
def register(request):
    # Look for a 'ref' in the URL (e.g., /register/?ref=admin)
    ref_username = request.GET.get('ref') 
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.as_p:
            user = form.save()
            profile = user.profile
            
            # If there was a referral link, reward the referrer
            if ref_username:
                try:
                    referrer = User.objects.get(username=ref_username)
                    profile.referred_by = referrer
                    profile.save()
                    
                    # Give the referrer 2 ETB bonus
                    referrer_profile = referrer.profile
                    referrer_profile.balance += 2.00
                    referrer_profile.save()
                except User.DoesNotExist:
                    pass
                    
            return redirect('tasks:login')
    else:
        form = UserCreationForm()
    return render(request, 'tasks/register.html', {'form': form})

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('tasks:task_list')
    else:
        form = AuthenticationForm()
    return render(request, 'tasks/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('tasks:login')

@login_required
def submit_task_proof(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        
        # 1. CHECK IF THEY ALREADY SUBMITTED THIS TASK
        already_submitted = TaskCompletion.objects.filter(user=request.user, task=task).exists()
        
        if already_submitted:
            messages.error(request, f"You have already submitted proof for '{task.title}'. Please wait for admin review.")
            return redirect('tasks:task_list')

        # 2. IF NOT SUBMITTED, PROCEED WITH UPLOAD
        proof_file = request.FILES.get('proof_image')
        if proof_file:
            TaskCompletion.objects.create(
                user=request.user,
                task=task,
                proof_image=proof_file,
                status='Pending'
            )
            messages.success(request, "Proof submitted! We will review it soon.")
        else:
            messages.error(request, "Please select an image file.")
            
    return redirect('tasks:task_list')

@staff_member_required
def admin_dashboard(request):
    # Only get completions that haven't been approved or rejected yet
    pending_tasks = TaskCompletion.objects.filter(status='Pending').order_error_by('-completed_at')
    return render(request, 'tasks/admin_dashboard.html', {'pending_tasks': pending_tasks})

@staff_member_required
def approve_task(request, completion_id):
    completion = get_object_or_404(TaskCompletion, id=completion_id)
    
    # Give the user the reward money
    profile = completion.user.profile
    profile.balance += completion.task.reward
    profile.save()
    
    # Mark task as approved
    completion.status = 'Approved'
    completion.save()
    
    messages.success(request, f"Approved {completion.user.username}'s task. Money sent!")
    return redirect('tasks:admin_dashboard')
@staff_member_required
def reject_task(request, completion_id):
    completion = get_object_or_404(TaskCompletion, id=completion_id)
    
    # Mark as rejected so it disappears from your pending list
    completion.status = 'Rejected'
    completion.save()
    
    messages.warning(request, f"Rejected {completion.user.username}'s task. No money was sent.")
    return redirect('tasks:admin_dashboard')

@staff_member_required
def admin_dashboard(request):
    pending_tasks = TaskCompletion.objects.filter(status='Pending')
    # Fetch all withdrawals that haven't been approved yet
    pending_withdrawals = WithdrawalRequest.objects.filter(is_approved=False).order_by('-created_at')
    
    return render(request, 'tasks/admin_dashboard.html', {
        'pending_tasks': pending_tasks,
        'pending_withdrawals': pending_withdrawals
    })

@staff_member_required
def approve_withdrawal(request, withdrawal_id):
    withdrawal = get_object_or_404(WithdrawalRequest, id=withdrawal_id)
    withdrawal.is_approved = True
    withdrawal.save()
    
    messages.success(request, f"Withdrawal for {withdrawal.user.username} marked as Paid!")
    return redirect('tasks:admin_dashboard')