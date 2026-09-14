from rest_framework import generics, mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample
from .models import Post
from .serializers import PostSerializer


@extend_schema(
    tags=['Posts'],
    summary='List posts or create a post',
    examples=[
        OpenApiExample(
            'Create Post Example',
            value={
                'title': 'My first JWT post',
                'content': 'Created from authenticated user token.'
            },
            request_only=True,
        ),
        OpenApiExample(
            'Create Post Response Example',
            value={
                'id': 1,
                'title': 'My first JWT post',
                'content': 'Created from authenticated user token.',
                'author_user_id': 1,
                'created_at': '2026-04-08T10:15:00Z',
                'updated_at': '2026-04-08T10:15:00Z'
            },
            response_only=True,
        ),
    ],
)
class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author_user_id=self.request.user.id)


@extend_schema(
    tags=['Posts'],
    summary='Retrieve, update, or delete one post',
)
class PostDetailView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


@extend_schema(
    tags=['Health'],
    summary='Health check',
    responses={
        200: {
            'type': 'object',
            'properties': {
                'status': {'type': 'string', 'example': 'ok'},
                'service': {'type': 'string', 'example': 'post_service'},
            }
        }
    },
)
class HealthView(APIView):
    def get(self, request):
        return Response({"status": "ok", "service": "post_service"})