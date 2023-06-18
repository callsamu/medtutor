from os import environ
from cohere import Client
from .examples import classifier_examples


class Classifier:
    cohere: Client

    def __init__(self):
        key = environ.get("COHERE_API_KEY") or ""
        self.cohere = Client(api_key=key)

    def classify(self, input: str) -> str:
        result = self.cohere.classify(
            inputs=[input],
            examples=classifier_examples,
            model="embed-multilingual-v2.0",
        )
        [classification] = result.classifications
        return classification.prediction
