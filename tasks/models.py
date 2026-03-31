from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# 1. TASK MODEL (Added this back to fix your ImportError!)
class Task(models.Model):
    title = models.CharField(max_length=200)
    link = models.URLField()
    reward = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    requires_proof = models.BooleanField(default=False)

    def __str__(self):
        return self.title

# 2. USER PROFILE (WALLET)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_bonus_date = models.DateTimeField(null=True, blank=True)
    referred_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')

    def __str__(self):
        return f"{self.user.username}'s Wallet"

# 3. SIGNALS (AUTOMATIC WALLET CREATION)
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# 4. WITHDRAWAL REQUESTS
class WithdrawalRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    payment_method = models.CharField(max_length=50, default="Telebirr")
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} ETB"
    
    # Add this to the bottom of your models.py
class TaskCompletion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)
    proof_image = models.ImageField(upload_to='proofs/', null=True, blank=True)
    status = models.CharField(max_length=20, default='Pending') # Pending, Approved, Rejected

    class Meta:
        unique_together = ('user', 'task') # This prevents double-claiming!

    def __str__(self):
        return f"{self.user.username} - {self.task.title}"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('Bonus', 'Bonus'),
        ('Task', 'Task'),
        ('Referral', 'Referral'),
        ('Withdrawal', 'Withdrawal'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} ({self.amount})"
    