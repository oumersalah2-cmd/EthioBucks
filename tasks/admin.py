from django.contrib import admin
from .models import Task, Profile, WithdrawalRequest, TaskCompletion
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages


# This makes the Withdrawal list look like a spreadsheet
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'phone_number', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at'] # Adds a sidebar to filter by date
    actions = ['approve_requests']

    def approve_requests(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "Selected requests have been marked as paid!")
    
    approve_requests.short_description = "Mark selected requests as Paid/Approved"

admin.site.register(Task)
admin.site.register(Profile)
admin.site.register(WithdrawalRequest, WithdrawalRequestAdmin)
admin.site.register(TaskCompletion)