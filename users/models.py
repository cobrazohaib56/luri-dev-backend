import uuid as uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from django.core.validators import RegexValidator


class BaseUser(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    email = models.EmailField(_("email address"), unique=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=17, null=True, blank=True)
    # email_confirmed = models.BooleanField(default=False)
    
    # def __str__(self):
    #     return self.email

class FeedBack(models.Model):
    comment = models.TextField(null=False, blank=False)
    user = models.ForeignKey(BaseUser, related_name="feedbacks", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)