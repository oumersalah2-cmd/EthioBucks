from django.contrib import admin
from .models import Task, Profile, WithdrawalRequest, TaskCompletion, Transaction
from django.utils.html import format_html

class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'phone_number', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    actions = ['approve_requests']

    def approve_requests(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "Selected requests have been marked as paid!")
    
    approve_requests.short_description = "Mark selected requests as Paid/Approved"

class TaskCompletionAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'status', 'completed_at', 'proof_preview']
    list_filter = ['status', 'completed_at']
    actions = ['approve_tasks', 'reject_tasks']

    def proof_preview(self, obj):
        if obj.proof_image:
            return format_html('<a href="{}" target="_blank"><img src="{}" style="height: 50px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" /></a>', obj.proof_image.url, obj.proof_image.url)
        return "No Proof"
    proof_preview.short_description = "Screenshot Proof"

    def approve_tasks(self, request, queryset):
        count = 0
        for completion in queryset.filter(status='Pending'):
            profile = completion.user.profile
            profile.balance += completion.task.reward
            profile.save()
            Transaction.objects.create(user=completion.user, amount=completion.task.reward, transaction_type='Task')
            completion.status = 'Approved'
            completion.save()
            count += 1
        self.message_user(request, f"{count} task submissions have been securely Approved & Paid Out!")
    approve_tasks.short_description = "Approve selected proof submissions and Pay user"

    def reject_tasks(self, request, queryset):
        changed = queryset.filter(status='Pending').update(status='Rejected')
        self.message_user(request, f"{changed} task submissions were rejected.")
    reject_tasks.short_description = "Reject selected proof submissions (No payout)"

class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'amount', 'timestamp']
    list_filter = ['transaction_type', 'timestamp']

admin.site.register(Task)
admin.site.register(Profile)
admin.site.register(WithdrawalRequest, WithdrawalRequestAdmin)
admin.site.register(TaskCompletion, TaskCompletionAdmin)
admin.site.register(Transaction, TransactionAdmin)