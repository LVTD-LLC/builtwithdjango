from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from blog.models import Post
from builtwithdjango.analytics import capture
from projects.models import Like, Project

from .serializers import LikeSerializer, LikeSerializerNoId, PostSerializer


class CreateLikeProjectAPIView(generics.ListCreateAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["author", "project"]

    def perform_create(self, serializer):
        like = serializer.save()
        capture(
            self.request,
            "project liked" if like.like else "project unliked",
            properties={
                "project_id": like.project_id,
                "author_id": like.author_id,
                "like_id": like.id,
                "like_value": like.like,
            },
            groups={"project": str(like.project_id)},
        )


class UpdateLikeProjectAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializerNoId

    def perform_update(self, serializer):
        like = serializer.save()
        capture(
            self.request,
            "project liked" if like.like else "project unliked",
            properties={
                "project_id": like.project_id,
                "author_id": like.author_id,
                "like_id": like.id,
                "like_value": like.like,
            },
            groups={"project": str(like.project_id)},
        )

    def perform_destroy(self, instance):
        project_id = instance.project_id
        author_id = instance.author_id
        like_id = instance.id
        instance.delete()
        capture(
            self.request,
            "project like removed",
            properties={
                "project_id": project_id,
                "author_id": author_id,
                "like_id": like_id,
            },
            groups={"project": str(project_id)},
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def search_projects(request):
    query = request.GET.get("q", "")
    if not query:
        return Response([])

    projects = Project.objects.filter(
        Q(title__icontains=query) | Q(short_description__icontains=query), published=True, active=True
    ).order_by("-sponsored", "-updated_date")[:5]
    result_count = len(projects)
    capture(
        request,
        "project search performed",
        properties={
            "query": query[:120],
            "query_length": len(query),
            "result_count": result_count,
            "has_results": result_count > 0,
            "result_project_ids": [project.id for project in projects],
        },
    )

    results = [
        {
            "id": project.id,
            "title": project.title,
            "slug": project.slug,
            "short_description": project.short_description,
            "screenshot": project.homepage_screenshot.url if project.homepage_screenshot else None,
            "url": project.url,
        }
        for project in projects
    ]

    return Response(results)


class CreatePostAPIView(generics.CreateAPIView):
    """
    Create a new blog post.
    Only superusers can create posts.
    """

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        post = serializer.save()
        capture(
            self.request,
            "post created",
            properties={
                "post_id": post.id,
                "post_title": post.title,
                "post_slug": post.slug,
                "post_status": post.status,
                "post_type": post.type,
            },
        )
