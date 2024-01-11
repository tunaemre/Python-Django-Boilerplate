from django.db import models

from app.infrastructure.entity.base.base_model import BaseModel


# Create your models here.

class Guest(BaseModel):
    name = models.CharField(max_length=50, null=False)
    surname = models.CharField(max_length=50, null=False)
    email = models.EmailField(null=False, unique=True)
    attend_on = models.DateField(auto_now_add=True)
    reference = models.ForeignKey('workshop.Guest',
                                  null=True,
                                  related_name='references_to',
                                  on_delete=models.PROTECT)
