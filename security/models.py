import random
import string
from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Channel(models.Model):
  def create_random_name():
    # Generate random channel name
    name = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return name
  sender_user = models.ForeignKey(User, related_name="sent_channels",  on_delete=models.CASCADE)
  recipient_user = models.ForeignKey(User,related_name="received_channels", on_delete=models.CASCADE,)
  name = models.CharField(max_length=100, default=create_random_name)
  accepted = models.BooleanField(default=False)
  initial_sender_secret = models.CharField(max_length=300, blank=True)
  initial_recipient_secret = models.CharField(max_length=300, blank=True)
  