# projects/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Project
from .serializers import ProjectListSerializer, ProjectDetailSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView


class ProjectListView(ListAPIView):
    serializer_class = ProjectListSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user).order_by('-created_at')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_get(request):
    project_id = request.query_params.get('id')
    if not project_id:
        return Response({'error': '缺少 id 参数'}, status=400)

    try:
        project = Project.objects.get(id=project_id, user=request.user)
        serializer = ProjectDetailSerializer(project)
        return Response(serializer.data)
    except Project.DoesNotExist:
        return Response({'error': '项目不存在'}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def project_create(request):
    project = Project.objects.create(user=request.user, project_type=request.data.get("type", "未知类型"),
                                     name=request.data.get('name', '未命名课程表'))
    return Response({'success': True, 'project_id': project.id})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def project_edit(request):
    try:
        project = Project.objects.get(id=request.data['id'], user=request.user)
        project.config = request.data.get('config', {})
        project.save()
        return Response({'success': True})
    except Project.DoesNotExist:
        return Response({'error': '项目不存在'}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def project_delete(request):
    try:
        project = Project.objects.get(id=request.data['id'], user=request.user)
        project.delete()
        return Response({'success': True})
    except Project.DoesNotExist:
        return Response({'error': '项目不存在'}, status=404)
