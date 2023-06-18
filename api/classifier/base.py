from abc import ABC, abstractmethod


class BaseClassifier(ABC):
    @abstractmethod
    def classify(self, input: str) -> str:
        """Classifies user input intent"""

    @abstractmethod
    async def aclassify(self, input: str) -> str:
        """Asynchronously classifies user input intent"""
