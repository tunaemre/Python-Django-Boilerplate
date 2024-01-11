import uuid
from typing import List, Any, Optional

from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, force_insert: bool = False, force_update: bool = False, using: Any = None,  # type: ignore
             update_fields: Optional[List[str]] = None) -> None:
        if force_update and update_fields is None:
            update_fields = []
        if update_fields is not None:
            update_fields.append('modified_date')

        super(BaseModel, self).save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )


class BaseEnum(models.Model):
    name = models.CharField(max_length=30, null=False, blank=False)

    class Meta:
        abstract = True
