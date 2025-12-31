from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type
from pydantic import BaseModel

class BaseNormalizer(ABC):
    """
    Abstract Base Class for Data Normalizers.
    Transforms Raw Dicts -> Standard Pydantic Models.
    """

    @abstractmethod
    def normalize(self, raw_record: Dict[str, Any]) -> BaseModel:
        """
        Converts a single raw record into a standardized model.
        """
        pass

    @property
    @abstractmethod
    def target_model(self) -> Type[BaseModel]:
        """Returns the Pydantic model class this normalizer produces."""
        pass
