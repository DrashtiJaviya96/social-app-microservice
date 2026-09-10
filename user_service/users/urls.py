from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    HealthView,
    RegisterView,
    LoginView,
    UserListView,
    UserDetailView,
    UserUpdateView,
    UserDeleteView,
    LogoutView,
    ChangePasswordView,
    ForgotPasswordView,
    ResetPasswordView,
)

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),

    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', ResetPasswordView.as_view(), name='reset_password'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    path('users-list/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/',UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/update/',  UserUpdateView.as_view(), name='user-update'),
    path('users/<int:pk>/delete/',  UserDeleteView.as_view(), name='user-delete')
]