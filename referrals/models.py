from django.db import models
from users.models import BaseUser

class Referral(models.Model):
    referrer = models.ForeignKey(BaseUser, related_name='made_referrals', on_delete=models.CASCADE)
    referred = models.ForeignKey(BaseUser, related_name='received_referrals', on_delete=models.CASCADE, unique=True)

    def __str__(self):
        return f"Referrer: {self.referrer.username}, Referred: {self.referred.username}"
