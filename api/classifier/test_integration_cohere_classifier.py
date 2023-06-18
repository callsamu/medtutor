from .cohere_classifier import CohereClassifier
from .examples import (
    CONVERSATIONAL,
    DOMAIN_SPECIFIC_QUESTION,
    DOMAIN_SPECIFIC_TASK,
    QUESTION
)


def test_classifier():
    classifier = CohereClassifier()

    got = classifier.classify("HELLO")
    assert got == CONVERSATIONAL

    got = classifier.classify("HOW WAS YOUR DAY?")
    assert got == QUESTION

    got = classifier.classify("WHAT IS ACUTE MIOCARDIAL INFACTION")
    assert got == DOMAIN_SPECIFIC_QUESTION

    got = classifier.classify("LIST SYMPTOMS OF YELLOW FEVER")
    assert got == DOMAIN_SPECIFIC_TASK
