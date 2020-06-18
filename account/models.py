from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class AccoutUser(User):

    def func1(self):
        pass
        return

    class Meta:
        proxy = True
