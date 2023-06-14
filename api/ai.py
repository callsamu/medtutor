import asyncio
import json
from typing import AsyncIterable, Awaitable

from prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains.llm import LLMChain
from langchain.schema import BaseRetriever
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains.question_answering.map_reduce_prompt import COMBINE_PROMPT

Result = dict[str, str]


class AI:
    chat_history = []

    def __init__(self, retriever: BaseRetriever):
        self.retriever = retriever

    def _load_conversation_chain(
        self,
        callbacks: list[BaseCallbackHandler] = []
    ) -> ConversationalRetrievalChain:
        llm = ChatOpenAI(
            client=None,
            verbose=True,
            temperature=0.5,
        )

        question_generator = LLMChain(
            llm=llm,
            prompt=CONDENSE_QUESTION_PROMPT,
            verbose=True,
        )

        streaming_llm = ChatOpenAI(
            client=None,
            temperature=0.5,
            streaming=True,
            callbacks=[*callbacks],
        )

        doc_chain = load_qa_with_sources_chain(
            llm=llm,
            combine_prompt=COMBINE_PROMPT,
            reduce_llm=streaming_llm,
            chain_type="map_reduce",
        )

        return ConversationalRetrievalChain(
            retriever=self.retriever,
            combine_docs_chain=doc_chain,
            question_generator=question_generator,
            return_generated_question=True,
            return_source_documents=True,
        )

    async def ask(self, question: str) -> AsyncIterable[str]:
        qa = self._load_conversation_chain()
        result = qa({
            "question": question,
            "chat_history": self.chat_history,
        })
        answer = result["answer"]
        self.chat_history.append((question, answer))

        data = json.dumps({"token": answer})
        yield f"data: {data}\n\n"

    async def ask_stream(
        self,
        question: str,
    ) -> AsyncIterable[str]:
        callback = AsyncIteratorCallbackHandler()
        qa = self._load_conversation_chain([callback])

        async def wrap_done(fn: Awaitable, event: asyncio.Event) -> Result:
            try:
                result = await fn
                return result
            except Exception as e:
                print(f"Error: {e}")
                raise e
            finally:
                event.set()

        inputs = {
            "question": question,
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
