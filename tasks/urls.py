from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('projects/', views.project_list_view, name='project_list'),
    path('projects/create/', views.create_project_view, name='create_project'),
    path('projects/<int:project_id>/', views.project_detail_view, name='project_detail'),
    path('projects/<int:project_id>/members/add/', views.add_member_view, name='add_member'),
    path('projects/<int:project_id>/members/<int:user_id>/remove/', views.remove_member_view, name='remove_member'),
    path('projects/<int:project_id>/tasks/create/', views.create_task_view, name='create_task'),
    path('tasks/<int:task_id>/update/', views.update_task_view, name='update_task'),
]
