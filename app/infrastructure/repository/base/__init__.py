from typing import TypeVar

from app.infrastructure.entity.base.base_model import BaseModel

BaseModelType = TypeVar('BaseModelType', bound=BaseModel)
