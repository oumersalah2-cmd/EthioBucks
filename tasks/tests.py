from django.shortcuts import render
from .models import Task

# Create your views here.

def task_list(request):
    # Task.objects.all() - This fetches all tasks from the database
    tasks = Task.objects.all()
    
    # render - This sends the tasks data to the HTML template
    return render(request, 'tasks/task_list.html', {'tasks': tasks})