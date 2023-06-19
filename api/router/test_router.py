from langchain import PromptTemplate
from langchain.llms.fake import FakeListLLM
from langchain.chains import LLMChain

from router import ClassifyRouterChain
from classifier import (
    MockClassifier,

    CONVERSATIONAL,
    QUESTION,
    DOMAIN_SPECIFIC_QUESTION,
)


def test_classify_router():
    responses = ["FOO", "BAR", "FOOBAR", "FOOBARXYZ"]
    llms = [FakeListLLM(responses=[response]) for response in responses]

    prompt = PromptTemplate.from_template("Say {input}: ")
    chains = [LLMChain(llm=llm, prompt=prompt) for llm in llms]

    mapping = {
        CONVERSATIONAL: chains[0],
        QUESTION: chains[1],
        DOMAIN_SPECIFIC_QUESTION: chains[2],
    }

    classifier = MockClassifier()
    router = ClassifyRouterChain(
        classifier=classifier,
        destination_chains=mapping,
        default_chain=chains[3],
    )

    result = router({"input": "foo"})
    assert result["text"] == responses[0]

    result = router({"input": "bar"})
    assert result["text"] == responses[1]

    result = router({"input": "foobar"})
    assert result["text"] == responses[2]

    result = router({"input": "foobarxyz"})
    assert result["text"] == responses[3]
