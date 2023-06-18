from os import environ
from .base import BaseClassifier
from .examples import classifier_examples
from cohere import Client, AsyncClient


class CohereClassifier(BaseClassifier):
    cohere: Client
    api_key: key

    def __init__(self):
        self.api_key = environ.get("COHERE_API_KEY") or ""
        self.cohere = Client(api_key=self.api_key)

    def classify(self, input: str) -> str:
        result = self.cohere.classify(
            inputs=[input],
            examples=classifier_examples,
            model="embed-multilingual-v2.0",
        )
        [classification] = result.classifications

        return classification.prediction

    async def aclassify(self, input: str) -> str:
        async with AsyncClient(api_key=self.api_key) as cohere:
            result = await cohere.classify(
                inputs=[input],
                examples=classifier_examples,
                model="embed-multilingual-v2.0",
            )
            [classification] = result.classifications

            return classification.prediction


