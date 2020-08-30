from django.db import models
from django.contrib.auth.models import AbstractUser
from db.base_model import BaseModel


class User(AbstractUser, BaseModel):
    """用户模型类"""

    class Meta:
        db_table = 'sm_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


