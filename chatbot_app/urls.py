"""chatbot_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from users.views import (
    CustomResetPasswordConfirm,
    CustomResetPasswordRequestToken,
    CustomResetPasswordValidateToken,
    TokenObtainUserView,
    UserRegisterViewSet,
    FeedbackViewSet,
    verify_email,
)

from .utils import BothHttpAndHttpsSchemaGenerator
from .views import chat_with_bot, chats_by_user, clear_chat, create_custom_chat, get_buttons

from chathistory.views import ActiveUsersAPIView


admin.site.site_header = "Chatbot Admin"
admin.site.site_title = "Chatbot Admin Portal"
admin.site.index_title = "Welcome to Chatbot Admin Portal"

urlpatterns = [
            path("admin/", admin.site.urls),
            path("auth/login/", TokenObtainUserView.as_view(), name="token_obtain_pair"),
            path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
            path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
            path(
                "auth/register/",
                UserRegisterViewSet.as_view({"post": "register_user"}),
                name="register_user",
            ),
            path(
                "api/userfeedback/",
                FeedbackViewSet.as_view({"post": "insert_feedback"}),
                name="insert_feedback"
            ),
            path(
                "api/get_feedbacks/",
                FeedbackViewSet.as_view({"get": "get_feedbacks"}),
                name="get_feedbacks"
            ),
            path(
                "auth/password-reset/validate_token/",
                CustomResetPasswordValidateToken.as_view(),
                name="reset-password-validate",
            ),
            path(
                "auth/password-reset/confirm/",
                CustomResetPasswordConfirm.as_view(),
                name="reset-password-confirm",
            ),
            path(
                "auth/password-reset/",
                CustomResetPasswordRequestToken.as_view(),
                name="password_reset",
            ),
            # path("api/save_initial_conversation/", save_initial_server_thread, name="save_initial_server_thread"),
            path("api/chat_request/", chat_with_bot, name="chat_request"),
            path("api/chats_by_user/", chats_by_user, name="fetch_all_chats"),
            path("api/clear_chat/", clear_chat, name="clear_chat"),
            
            path("api/create_custom_chat/", create_custom_chat, name="clear_custom_chat"),
            
            path('api/active_users/', ActiveUsersAPIView.as_view(), name='active-users'),
            
            path('verify-email/<token>/', verify_email, name='email_verify'),
            
            path("api/get_buttons/", get_buttons, name="get_buttons"),
            
        ]

urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))

schema_view = get_schema_view(
    openapi.Info(
        title="Chatbot API",
        default_version="v1",
        description="API documentation for Chatbot APP",
    ),
    public=True,
    generator_class=BothHttpAndHttpsSchemaGenerator,
    permission_classes=(IsAuthenticated, IsAdminUser),
)

urlpatterns.extend(
    [
        re_path(
            r"swagger(?P<format>\.json|\.yaml)$",
            schema_view.without_ui(cache_timeout=0),
            name="schema-json",
        ),
        path(
            "swagger/",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        path(
            "redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
        ),
    ]
)
