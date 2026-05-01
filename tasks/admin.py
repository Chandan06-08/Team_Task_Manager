from django.contrib import admin

from .models import Membership, Project, Task


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'created_at')
    search_fields = ('name', 'description', 'creator__username')


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'role', 'joined_at')
    list_filter = ('role',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assignee', 'status', 'priority', 'due_date')
    list_filter = ('status', 'priority')
    search_fields = ('title', 'description', 'assignee__username')
