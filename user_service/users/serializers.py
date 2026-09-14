from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import UserProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', min_length=3)
    first_name = serializers.CharField(source='user.first_name', required=False, allow_blank=True)
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True)
    email = serializers.EmailField(source='user.email')
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = UserProfile
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
        ]

    def validate(self, data):
        user_data = data.get('user', {})
        username = user_data.get('username')
        email = user_data.get('email')
        password = data.get('password')

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': 'Username already exists.'})

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Email already exists.'})

        validate_password(password)
        return data

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            username=user_data['username'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            email=user_data['email'],
            password=password,
        )

        return UserProfile.objects.create(user=user, **validated_data)

class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        return super().get_token(user)

    def validate(self, attrs):
        data = super().validate(attrs)

        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email,
        }

        return data

class UserListSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user_id', 'username']

class UserDetailSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'user_id',
            'username',
            'first_name',
            'last_name',
            'email',
            'created_at',
        ]

class UserUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False, allow_blank=True)
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True)
    email = serializers.EmailField(source='user.email', required=False)
    username = serializers.CharField(source='user.username', required=False, min_length=3)

    class Meta:
        model = UserProfile
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
        ]

    def validate(self, data):
        user_data = data.get('user', {})
        instance = self.instance

        username = user_data.get('username')
        email = user_data.get('email')

        if username:
            qs = User.objects.filter(username=username)
            if instance:
                qs = qs.exclude(id=instance.user.id)
            if qs.exists():
                raise serializers.ValidationError({'username': 'Username already exists.'})

        if email:
            qs = User.objects.filter(email=email)
            if instance:
                qs = qs.exclude(id=instance.user.id)
            if qs.exists():
                raise serializers.ValidationError({'email': 'Email already exists.'})

        return data

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user

        if 'username' in user_data:
            user.username = user_data['username']
        if 'first_name' in user_data:
            user.first_name = user_data['first_name']
        if 'last_name' in user_data:
            user.last_name = user_data['last_name']
        if 'email' in user_data:
            user.email = user_data['email']

        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)

    def validate_new_password(self, value):
        validate_password(value)
        return value

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, min_length=6)

    def validate_new_password(self, value):
        validate_password(value)
        return value