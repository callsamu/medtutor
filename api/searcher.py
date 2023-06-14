from os import environ

import qdrant_client

from langchain.vectorstores import Qdrant
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document, BaseRetriever


class DocumentSearcher:
    qdrant: Qdrant
    doc_number = 1

    def __init__(self):
        client = qdrant_client.QdrantClient(
            api_key=environ.get("QDRANT_API_KEY"),
            url=environ.get("QDRANT_HOST"),
            prefer_grpc=True,
        )
        embeddings = OpenAIEmbeddings(client=None)
        self.qdrant = Qdrant(
            client=client,
            collection_name="MedTexts",
            embeddings=embeddings
        )

    def as_retriever(self) -> BaseRetriever:
        return self.qdrant.as_retriever(
            search_kwargs={"k": self.doc_number}
        )

    def search(self, query: str) -> list[Document]:
        return self.qdrant.similarity_search(query, self.doc_number)
