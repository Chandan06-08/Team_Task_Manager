from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    AddMemberForm,
    LoginForm,
    ProjectForm,
    SignupForm,
    TaskForm,
    TaskStatusForm,
)
from .models import Membership, Project, Task


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Your account has been created.')
            return redirect('dashboard')
    else:
        form = SignupForm()
    return render(request, 'tasks/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'tasks/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard_view(request):
    tasks = Task.objects.filter(project__members=request.user).select_related('project', 'assignee')
    total_tasks = tasks.count()
    status_counts = tasks.values('status').annotate(count=Count('id'))
    assignee_counts = tasks.values('assignee__username').annotate(count=Count('id'))
    overdue_tasks = tasks.filter(due_date__lt=timezone.localdate(), status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS]).count()

    stats = {
        'todo': next((item['count'] for item in status_counts if item['status'] == Task.Status.TODO), 0),
        'in_progress': next((item['count'] for item in status_counts if item['status'] == Task.Status.IN_PROGRESS), 0),
        'done': next((item['count'] for item in status_counts if item['status'] == Task.Status.DONE), 0),
    }

    return render(request, 'tasks/dashboard.html', {
        'projects': request.user.projects.all(),
        'total_tasks': total_tasks,
        'status_counts': stats,
        'assignee_counts': assignee_counts,
        'overdue_tasks': overdue_tasks,
    })


@login_required
def project_list_view(request):
    projects = request.user.projects.all()
    return render(request, 'tasks/project_list.html', {'projects': projects})


@login_required
def create_project_view(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.creator = request.user
            project.save()
            Membership.objects.create(user=request.user, project=project, role=Membership.Role.ADMIN)
            messages.success(request, 'Project created successfully.')
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm()
    return render(request, 'tasks/project_form.html', {'form': form, 'title': 'Create Project'})


@login_required
def project_detail_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if not project.is_member(request.user):
        raise PermissionDenied()

    membership = get_object_or_404(Membership, project=project, user=request.user)
    tasks = project.tasks.select_related('assignee').all()
    members = project.members.all()

    return render(request, 'tasks/project_detail.html', {
        'project': project,
        'tasks': tasks,
        'members': members,
        'membership': membership,
    })


@login_required
def add_member_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if not project.is_admin(request.user):
        raise PermissionDenied()

    if request.method == 'POST':
        form = AddMemberForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']
            user = User.objects.filter(email__iexact=email).first()
            if not user:
                messages.error(request, 'User with that email was not found.')
            else:
                membership, created = Membership.objects.get_or_create(user=user, project=project, defaults={'role': role})
                if not created:
                    membership.role = role
                    membership.save()
                    messages.info(request, 'Existing member role updated.')
                else:
                    messages.success(request, f'{user.get_full_name() or user.username} added to project.')
                return redirect('project_detail', project_id=project.id)
    else:
        form = AddMemberForm()

    return render(request, 'tasks/member_form.html', {'form': form, 'project': project})


@login_required
def remove_member_view(request, project_id, user_id):
    project = get_object_or_404(Project, pk=project_id)
    if not project.is_admin(request.user):
        raise PermissionDenied()

    member = get_object_or_404(User, pk=user_id)
    if member == request.user:
        messages.error(request, 'You cannot remove yourself from the project.')
    else:
        Membership.objects.filter(project=project, user=member).delete()
        messages.success(request, f'{member.get_full_name() or member.username} has been removed.')
    return redirect('project_detail', project_id=project.id)


@login_required
def create_task_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if not project.is_admin(request.user):
        raise PermissionDenied()

    if request.method == 'POST':
        form = TaskForm(project=project, data=request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.created_by = request.user
            task.save()
            messages.success(request, 'Task created successfully.')
            return redirect('project_detail', project_id=project.id)
    else:
        form = TaskForm(project=project)
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Create Task', 'project': project})


@login_required
def update_task_view(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    project = task.project
    if not project.is_member(request.user):
        raise PermissionDenied()

    user_is_admin = project.is_admin(request.user)
    user_is_assignee = task.assignee == request.user
    if not (user_is_admin or user_is_assignee):
        raise PermissionDenied()

    if request.method == 'POST':
        if user_is_admin:
            form = TaskForm(project=project, data=request.POST, instance=task)
        else:
            form = TaskStatusForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully.')
            return redirect('project_detail', project_id=project.id)
    else:
        form = TaskForm(project=project, instance=task) if user_is_admin else TaskStatusForm(instance=task)

    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Update Task', 'project': project, 'task': task})
