# views.py - Fixed version with proper CSRF handling
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token
from .models import Todo
from .forms import SignupForm

@csrf_protect
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return redirect('signup')

            user = User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, "Account created successfully!")
            return redirect('login')
        else:
            messages.error(request, "Invalid form data.")
            return redirect('signup')
    else:
        form = SignupForm()
    
    # Ensure CSRF token is available in the template
    csrf_token = get_token(request)
    return render(request, 'signup.html', {
        'form': form, 
        'csrf_token': csrf_token
    })

@csrf_protect
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return redirect('login')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('todo')
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('login')
    
    # Ensure CSRF token is available
    csrf_token = get_token(request)
    return render(request, "login.html", {'csrf_token': csrf_token})

@login_required(login_url='login')
@csrf_protect
def todo_page(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        if title and title.strip():
            obj = Todo(title=title.strip(), user=request.user)
            obj.save()
            messages.success(request, "Task added successfully!")
            return redirect('todo')
        else:
            messages.error(request, "Task title cannot be empty.")
    
    # Fetch and display all tasks for the logged-in user
    res = Todo.objects.filter(user=request.user).order_by('-id')
    csrf_token = get_token(request)
    return render(request, 'todo.html', {
        'todos': res,
        'csrf_token': csrf_token
    })

@login_required(login_url='login')
@csrf_protect
def delete_todo(request, srno):
    if request.method == 'POST':
        try:
            todo_item = get_object_or_404(Todo, id=srno, user=request.user)
            todo_title = todo_item.title
            todo_item.delete()
            messages.success(request, f"Task '{todo_title}' deleted successfully!")
        except Todo.DoesNotExist:
            messages.error(request, "Task not found.")
        except Exception as e:
            messages.error(request, f"Error deleting task: {str(e)}")
    
    return redirect('todo')

@login_required(login_url='login')
@csrf_protect
def edit_todo(request, srno):
    todo_item = get_object_or_404(Todo, id=srno, user=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        
        if title and title.strip():
            old_title = todo_item.title
            todo_item.title = title.strip()
            todo_item.save()
            messages.success(request, f"Task updated from '{old_title}' to '{todo_item.title}'!")
            return redirect('todo')
        else:
            messages.error(request, "Title cannot be empty.")
    
    csrf_token = get_token(request)
    return render(request, 'edit_todo.html', {
        'todo': todo_item,
        'csrf_token': csrf_token
    })

@login_required(login_url='login')
def logout_view(request):
    username = request.user.username
    logout(request)
    messages.success(request, f"Goodbye {username}! You have been logged out successfully.")
    return redirect('login')

# settings.py - Make sure these middleware are enabled
"""
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # This is crucial for CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
"""