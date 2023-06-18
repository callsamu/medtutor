from typing import List
from cohere.responses.classify import Example


CONVERSATIONAL = "conversational"
QUESTION = "question"
DOMAIN_SPECIFIC_QUESTION = "domain_specific_question"
DOMAIN_SPECIFIC_TASK = "domain_specific_task"


def _conversational(text: str) -> Example:
    return Example(text, CONVERSATIONAL)


def _question(text: str) -> Example:
    return Example(text, QUESTION)


def _ds_question(text: str) -> Example:
    return Example(text, DOMAIN_SPECIFIC_QUESTION)


def _ds_task(text: str) -> Example:
    return Example(text, DOMAIN_SPECIFIC_TASK)


classifier_examples: List[Example] = [
    _conversational("Hello"),
    _conversational("Olá"),
    _conversational("Hola"),

    _question("How are you?"),
    _question("Como está você?"),
    _question("Você pode me ajudar no meu TCC?"),
    _question("Dengue cases in Brasil increased by 70%. Do you understand?"),

    _ds_question("What is an acute lung edema?"),
    _ds_question("What dosage of furosemide is adequate for acute lung edema"),
    _ds_question("What is yellow fever"),
    _ds_question("Quais são os sintomas de um AVC?"),

    _ds_task("Explain me how is an acute myocardial infarction treated"),
    _ds_task("List some symptoms of yellow fever"),
]
