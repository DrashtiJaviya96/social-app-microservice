from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, OpenApiExample, inline_serializer
from rest_framework import serializers


class TokenObtainPairExampleView(TokenObtainPairView):
    @extend_schema(
        tags=['Auth'],
        summary='Get JWT access and refresh tokens',
        request=inline_serializer(
            name='TokenRequest',
            fields={
                'username': serializers.CharField(default='alice'),
                'password': serializers.CharField(default='alice123'),
            },
        ),
        examples=[
            OpenApiExample(
                'Login Example',
                value={'username': 'alice', 'password': 'alice123'},
                request_only=True,
            )
        ],
        responses={
            200: inline_serializer(
                name='TokenResponse',
                fields={
                    'refresh': serializers.CharField(),
                    'access': serializers.CharField(),
                },
            )
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)