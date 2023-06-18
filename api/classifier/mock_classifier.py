from .base import BaseClassifier
from .examples import (
    CONVERSATIONAL,
    QUESTION,
    DOMAIN_SPECIFIC_TASK,
    DOMAIN_SPECIFIC_QUESTION,
)


class MockClassifier(BaseClassifier):
    def _classify(self, user_input: str) -> str:
        table = {
            "foo": CONVERSATIONAL,
            "bar": QUESTION,
            "foobar": DOMAIN_SPECIFIC_QUESTION,
            "foobarxyz": DOMAIN_SPECIFIC_TASK,
        }

        if user_input not in table:
            return CONVERSATIONAL

        return table[user_input]

    def classify(self, user_input: str) -> str:
        return self._classify(user_input)

    async def aclassify(self, user_input: str) -> str:
        return self._classify(user_input)
