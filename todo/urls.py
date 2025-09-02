# urls.py (main project)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('todo.urls')),  # Include your app URLs
]

# todo/urls.py (app-specific URLs)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.signup, name='signup'),  # Root path for signup
    path('login/', views.login_view, name='login'),  # Login page
    path('todopage/', views.todo_page, name='todo'),  # Todo page
    path('edit_todo/<int:srno>/', views.edit_todo, name='edit_todo'),
    path('delete_todo/<int:srno>/', views.delete_todo, name='delete_todo'),
    path('logout/', views.logout_view, name='logout'),
]