"""All the views related to users exist here."""
import logging
from datetime import timezone, datetime
import json

from django.contrib.auth import get_user_model, password_validation
from django.db import IntegrityError
from django_rest_passwordreset.views import (
    ResetPasswordConfirm,
    ResetPasswordRequestToken,
    ResetPasswordValidateToken,
)
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.tokens import RefreshToken


from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError, AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.utils import get_md5_hash_password
from rest_framework_simplejwt.views import TokenViewBase
from django.utils.translation import gettext_lazy as _
from rest_framework.views import APIView

from .models import FeedBack, BaseUser
from referrals.models import Referral
from users.serializers import (
    UserRegisterSerializer,
    UserSerializer,
)

from chathistory.views import create_chat_util

from django.core.signing import Signer
from django.core.mail import send_mail
from django.urls import reverse
from django.core.signing import BadSignature, Signer
from django.shortcuts import redirect

signer = Signer()

UserModel = get_user_model()
logger = logging.getLogger(__name__)


class FeedbackViewSet(viewsets.ViewSet):
    """Viewset responsible for user feedback crud"""
    
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    @swagger_auto_schema(
        method="post",
    )
    @action(
        detail=False,
        methods=["post", "get"],
    )
    def insert_feedback(self, request):
        request_data = request.data
        try:
            """Insert Feedback"""
            user_id = request_data["user"]
            user = UserModel.objects.filter(id=user_id)
            feedback = FeedBack.objects.create(
                comment = request_data["comment"],
                user = user.first(),
                timestamp = datetime.now()
            )
            feedback.save()
        except Exception as e:
            return Response(
                {"errors": json.dumps(e)}, status=status.HTTP_412_PRECONDITION_FAILED
            )
        return Response(status=status.HTTP_200_OK, data=request.data)
    def get_feedbacks(self, request):
        
        if not request.user.is_superuser:
            # If not, return an HTTP 403 Forbidden response
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)
            
        try:
            userfeedback = []
            feedbacks = FeedBack.objects.all().order_by('-timestamp')
            users_count = UserModel.objects.all().count()
            for feedback in feedbacks:
                userfeedback.append({
                    "comment": feedback.comment,
                    "user": feedback.user.get_full_name(),
                    "datetime": feedback.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                })
            return Response(json.dumps(
                {
                    "feedback_list": userfeedback,
                    "user_count": users_count
                }
            ), status=status.HTTP_200_OK)              
        except Exception as e:
            return Response(
                {"errors": json.dumps(e)}, status=status.HTTP_412_PRECONDITION_FAILED
            )    

@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def verify_email(request, token):
    signer = Signer()
    try:
        user_id = signer.unsign(token)
        user = BaseUser.objects.get(pk=user_id)
        user.email_confirmed = True
        user.save()
        # Redirect to a success page or login page
        return redirect('verification_success')
    except (BadSignature, BaseUser.DoesNotExist):
        # Redirect to an invalid token page
        return redirect('verification_fail')

class UserRegisterViewSet(viewsets.ViewSet):
    """Viewset responsible for registering the user."""
    @swagger_auto_schema(
        method="post",
        request_body=UserRegisterSerializer(),
    )
    @action(
        detail=False,
        methods=["post"],
    )
    def register_user(self, request):
    
        """Register User."""
        serializer = UserRegisterSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            password_validation.validate_password(serializer.validated_data["password"])

            user = UserModel.objects.create(
                first_name=serializer.validated_data["first_name"],
                last_name=serializer.validated_data["last_name"],
                email=serializer.validated_data["email"],
                phone=serializer.validated_data["phone"],
                username=serializer.validated_data["email"],
            )

            user.set_password(serializer.validated_data["password"])
            user.save()
            refresh = RefreshToken.for_user(user)
            token = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            
            create_chat_util(user)
            
            # self.send_verification_email(request, user)
            # Handle referral logic if referral_uuid is present
            referral_uuid = serializer.validated_data.get('referral_uuid')
            if referral_uuid:
                try:
                    referrer = UserModel.objects.get(uuid=referral_uuid)
                    try:
                        Referral.objects.create(referrer=referrer, referred=user)
                    except IntegrityError:
                        return Response({'error': 'Duplicate referral detected.'}, status=status.HTTP_400_BAD_REQUEST)
                
                except ObjectDoesNotExist:
                    return Response({'error': 'Invalid referral UUID.'}, status=status.HTTP_400_BAD_REQUEST)
        
        except ValidationError as e:
            logger.error(e)
            if serializer.errors:
                error_list = [
                    serializer.errors[error][0].replace("This", error).replace("base user", "User")
                    for error in serializer.errors
                ]
                return Response(
                    {"errors": error_list}, status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {"errors": e.args}, status=status.HTTP_412_PRECONDITION_FAILED
                )
        except IntegrityError as e:
            if "unique constraint" in str(e).lower():
                # Handle the unique email error here
                # You can log the error, provide a user-friendly message, or take other actions as needed
                return Response(
                    {"errors": ["Email already exists"]}, status=status.HTTP_412_PRECONDITION_FAILED
                )
            else:
                # Handle other IntegrityErrors or unexpected errors
                print("An unexpected error occurred:", str(e))
        except Exception as e:
            return Response(
                {"errors": e}, status=status.HTTP_412_PRECONDITION_FAILED
            )

        return Response( {'status': 'User registered successfully.', 'user': UserSerializer(user).data, 'token': token}, status=status.HTTP_200_OK)
    
    def send_verification_email(self, request, user):
        signer = Signer()
        token = signer.sign(user.pk)
        verify_url = request.build_absolute_uri(reverse('email_verify', args=[token]))
        subject = 'Verify your account'
        message = f'Please click the following link to verify your email: {verify_url}'
        print("About to send verification email")
        send_mail(subject, message, 'from@example.com', [user.email], fail_silently=False)

    
class UserViewSet(viewsets.ViewSet):
    """Viewset that creates the Apis for listing and retrieving the users."""

    @swagger_auto_schema(tags=["Users"])
    def list(self, request):
        """List all the users in the DB."""
        queryset = UserModel.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(tags=["Users"])
    def retrieve(self, request, pk=None):
        """Retrieve a user using the primary key."""
        queryset = UserModel.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    

class TokenObtainUserSerializer(TokenObtainPairSerializer):
    """User login serializer."""

    def validate(self, attrs):
        """Validate the user and return the user instance and access token if user is valid."""
        self.error_messages["no_active_account"] = {
            "errors": ["No user found with the given credentials"]
        }
        data = super().validate(attrs)
        data["token"] = {"access": data["access"], "refresh": data["refresh"]}
        del data["access"]
        del data["refresh"]
        data["user"] = UserSerializer(self.user).data
        self.user.last_login = datetime.now(tz=timezone.utc)
        return data


class TokenObtainUserView(TokenViewBase):
    """API for user login."""

    serializer_class = TokenObtainUserSerializer

    def post(self, request, *args, **kwargs):
        """Request Login."""
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        except ValidationError as e:
            error_list = [
                serializer.errors[error][0].replace("This", error)
                for error in serializer.errors
            ]
            return Response({"errors": error_list}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class CustomResetPasswordRequestToken(ResetPasswordRequestToken):
    """API for user Reset Password."""

    def post(self, request, *args, **kwargs):
        """Request for Password Rest."""
        try:
            response = super().post(request, *args, **kwargs)
        except ValidationError as e:
            error_list = []
            if "email" in e.args[0]:
                error_message = e.args[0]["email"]
                error_list.append(error_message[0].replace("This", "email"))

            return Response({"errors": error_list}, status=status.HTTP_400_BAD_REQUEST)

        return response


class CustomResetPasswordValidateToken(ResetPasswordValidateToken):
    """API for validating the reset password."""

    def post(self, request, *args, **kwargs):
        """Request for reset password token validation."""
        try:
            response = super().post(request, *args, **kwargs)
        except ValidationError as e:
            error_list = []
            if "token" in e.args[0]:
                error_message = e.args[0]["token"]
                error_list.append(error_message[0].replace("This", "token"))
            return Response({"errors": error_list}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"errors": e.args}, status=status.HTTP_400_BAD_REQUEST)

        return response


class CustomResetPasswordConfirm(ResetPasswordConfirm):
    """Confirm change password using reset token."""

    def post(self, request, *args, **kwargs):
        """If token is valid reset the password to new password."""
        try:
            response = super().post(request, *args, **kwargs)
        except ValidationError as e:
            error_list = []
            if "token" in e.args[0]:
                error_message = e.args[0]["token"]
                error_list.append(error_message[0].replace("This", "token"))
            if "password" in e.args[0]:
                error_message = e.args[0]["password"]
                error_list.append(error_message[0].replace("This", "password"))
            return Response({"errors": error_list}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"errors": e.args}, status=status.HTTP_400_BAD_REQUEST)

        return response
    
