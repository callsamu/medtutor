import asyncio
import json
from typing import AsyncIterable, Awaitable

from langchain.llms import Cohere
from langchain.chat_models import ChatOpenAI
from langchain.chains.llm import LLMChain
from langchain.schema import BaseRetriever
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain

import prompts
import classifier
from router import ClassifyRouterChain


Result = dict[str, str]


class AI:
    chat_history = []
    classify: classifier.BaseClassifier

    def __init__(self, retriever: BaseRetriever):
        self.retriever = retriever
        self.classify = classifier.CohereClassifier()

    def _load_router(
        self,
        callbacks: list[BaseCallbackHandler] = []
    ) -> ClassifyRouterChain:
        llm = Cohere(client=None, model='command-light', temperature=0.3)

        streaming_llm = ChatOpenAI(
            client=None,
            temperature=0.5,
            streaming=True,
            callbacks=[*callbacks]
        )

        doc_chain = load_qa_with_sources_chain(
            llm=llm,
            combine_prompt=prompts.QUESTION_COMBINE_PROMPT,
            reduce_llm=streaming_llm,
            chain_type="map_reduce",
        )

        qa = ConversationalRetrievalChain(
            retriever=self.retriever,
            combine_docs_chain=doc_chain,
            question_generator=LLMChain(
                llm=llm, prompt=prompts.CONDENSE_QUESTION_PROMPT,
            ),
            return_generated_question=True,
        )

        routes = {
            classifier.DOMAIN_SPECIFIC_QUESTION: qa,
        }

        return ClassifyRouterChain(
            classifier=self.classify,
            destination_chains=routes,
            default_chain=LLMChain(
                llm=streaming_llm,
                prompt=prompts.CONVERSATION_PROMPT,
                output_key="answer"
            )
        )

    async def ask_stream(
        self,
        question: str,
    ) -> AsyncIterable[str]:
        callback = AsyncIteratorCallbackHandler()
        qa = self._load_router([callback])

        async def wrap_done(fn: Awaitable, event: asyncio.Event) -> Result:
            try:
                result = await fn
                return result
            except Exception as e:
                raise e
            finally:
                event.set()

        inputs = {
            "input": question,
            "chat_history": self.chat_history,
        }
        task = asyncio.create_task(wrap_done(
            qa.acall(inputs),
            callback.done,
        ))

        async for token in callback.aiter():
            data = json.dumps({"token": token})
            yield f"data: {data}\n\n"

        try:
            await task
            result = task.result()
            print(result)
            self.chat_history.append((question, result["answer"]))

            data = "event: close\n"
            data += "data: Connection closed by the server\n\n"

            yield data
        except Exception as e:
            print(f"Error: {e}")
            data = "event: error\n"
            data += "data: Sorry but the server encountered an error. "
            data += "Please, try again later\n\n"

            yield data
