from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.contrib.admin.views.decorators import staff_member_required
from decimal import Decimal
from .models import Task, Profile, WithdrawalRequest, TaskCompletion, Transaction

# 1. UPDATED DASHBOARD (Now with Totals calculation)
@login_required
def task_list(request):
    all_tasks = Task.objects.all()
    user_profile, created = Profile.objects.get_or_create(user=request.user)
    
    # Count invitations
    referral_count = request.user.referrals.count()
    
    # Withdrawal History
    my_withdrawals = WithdrawalRequest.objects.filter(user=request.user).order_by('-created_at')

    # CALCULATE TOTALS (The part we were missing)
    # Using 'is_approved' because that matches your Admin functions below
    pending_money = my_withdrawals.filter(is_approved=False).aggregate(Sum('amount'))['amount__sum'] or 0.00
    approved_money = my_withdrawals.filter(is_approved=True).aggregate(Sum('amount'))['amount__sum'] or 0.00

    context = {
        'tasks': all_tasks,
        'profile': user_profile,
        'referral_count': referral_count,
        'withdrawals': my_withdrawals,
        'pending_money': pending_money,
        'approved_money': approved_money,
    }
    return render(request, 'tasks/task_list.html', context)

# 2. TASK DETAIL & COMPLETE TASKS
@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'tasks/task_detail.html', {'task': task})

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    user_profile = request.user.profile
    already_done = TaskCompletion.objects.filter(user=request.user, task=task).exists()
    
    if not already_done:
        TaskCompletion.objects.create(user=request.user, task=task)
        user_profile.balance += task.reward
        user_profile.save()
        Transaction.objects.create(user=request.user, amount=task.reward, transaction_type='Task')
        messages.success(request, f"Task completed! You earned {task.reward} ETB.")
    else:
        messages.warning(request, "You have already earned rewards for this task.")
    return redirect(task.link)

# 3. DAILY BONUS
@login_required
def claim_daily_bonus(request):
    profile = request.user.profile
    today = timezone.now().date()
    if profile.last_bonus_date is None or profile.last_bonus_date.date() < today:
        profile.balance += Decimal('1.00')
        profile.last_bonus_date = timezone.now()
        profile.save()
        Transaction.objects.create(user=request.user, amount=Decimal('1.00'), transaction_type='Bonus')
        messages.success(request, "Success! You claimed your daily bonus.")
    else:
        messages.warning(request, "You already claimed your bonus today. Come back tomorrow!")
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
            Transaction.objects.create(user=request.user, amount=-amount, transaction_type='Withdrawal')
            messages.success(request, "Withdrawal request sent!")
        else:
            messages.error(request, "Insufficient balance.")
        return redirect('tasks:task_list')
    return render(request, 'tasks/withdraw.html')

# 5. REGISTER & AUTH
def register(request):
    ref_username = request.GET.get('ref')
    if ref_username:
        request.session['recommended_by'] = ref_username
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            referrer_name = request.session.get('recommended_by')
            if referrer_name:
                try:
                    referrer_user = User.objects.get(username=referrer_name)
                    referrer_profile = referrer_user.profile
                    referrer_profile.balance += Decimal('2.00')
                    referrer_profile.save()
                    Transaction.objects.create(user=referrer_user, amount=Decimal('2.00'), transaction_type='Referral')
                    del request.session['recommended_by']
                except (User.DoesNotExist, Profile.DoesNotExist):
                    pass
            login(request, new_user)
            return redirect('tasks:task_list')
    else:
        form = UserCreationForm()
    return render(request, 'tasks/register.html', {'form': form})

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
def profile(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'tasks/profile.html', {'transactions': transactions})

# 6. ADMIN & PROOF LOGIC
@login_required
def submit_task_proof(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        already_submitted = TaskCompletion.objects.filter(user=request.user, task=task).exists()
        if already_submitted:
            messages.error(request, f"You have already submitted proof for '{task.title}'.")
            return redirect('tasks:task_list')
        proof_file = request.FILES.get('proof_image')
        if proof_file:
            TaskCompletion.objects.create(user=request.user, task=task, proof_image=proof_file, status='Pending')
            messages.success(request, "Proof submitted!")
        else:
            messages.error(request, "Please select an image file.")
    return redirect('tasks:task_list')
