from django.contrib.auth.models import User
from rest_framework import permissions, routers, serializers, viewsets

from .models import Membership, Project, Task


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'email']


class MembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Membership
        fields = ['user', 'role', 'joined_at']


class ProjectSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'creator', 'members', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    assignee = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True, required=False)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'project',
            'title',
            'description',
            'assignee',
            'status',
            'priority',
            'due_date',
            'created_by',
            'created_at',
            'updated_at',
        ]

    def validate_project(self, value):
        request = self.context.get('request')
        if request and not value.is_member(request.user):
            raise serializers.ValidationError('You must be a member of the selected project.')
        return value

    def validate_assignee(self, value):
        project = self.initial_data.get('project')
        if value and project:
            try:
                project_obj = Project.objects.get(pk=project)
            except Project.DoesNotExist:
                raise serializers.ValidationError('Project does not exist.')
            if not project_obj.members.filter(pk=value.pk).exists():
                raise serializers.ValidationError('Assignee must be a member of the project.')
        return value


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.order_by('username')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.none()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(members=self.request.user)

    def perform_create(self, serializer):
        project = serializer.save(creator=self.request.user)
        Membership.objects.create(user=self.request.user, project=project, role=Membership.Role.ADMIN)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.none()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(project__members=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register('projects', ProjectViewSet)
router.register('tasks', TaskViewSet)
