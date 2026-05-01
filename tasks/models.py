from django.conf import settings
from django.db import models
from django.utils import timezone


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_projects',
        on_delete=models.CASCADE,
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Membership',
        related_name='projects',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def is_admin(self, user):
        return self.membership_set.filter(user=user, role=Membership.Role.ADMIN).exists()

    def is_member(self, user):
        return self.members.filter(pk=user.pk).exists()


class Membership(models.Model):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        MEMBER = 'MEMBER', 'Member'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['user', 'project']]
        ordering = ['project', 'user']

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} - {self.project.name} ({self.role})'


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = 'TODO', 'To Do'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        DONE = 'DONE', 'Done'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'

    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='assigned_tasks',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    due_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_tasks',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', 'priority', 'title']

    def __str__(self):
        return f'{self.title} [{self.project.name}]'

    @property
    def is_overdue(self):
        return self.due_date and self.due_date < timezone.localdate() and self.status != Task.Status.DONE
