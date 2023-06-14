#!/usr/bin/env python

from sys import argv
from os.path import join
from tiktoken import encoding_for_model
from langchain.document_loaders import PyMuPDFLoader

import utils.database as db

encoding = encoding_for_model("text-embedding-ada-002")


def load_pdf(citation: str, path: str) -> int:
    tokens = 0

    loader = PyMuPDFLoader(path)
    documents = loader.load_and_split()

    for doc in documents:
        doc.metadata["source"] = citation
        encoded_doc = encoding.encode(doc.page_content)
        tokens += len(encoded_doc)

    return tokens


def main():
    tokens = 0

    dirpath = "./papers/" if len(argv) < 2 else argv[1]

    for [citation] in db.read_downloaded_citations():
        path = join(dirpath, citation)
        path = path.removesuffix(".") + ".pdf"
        print(path)
        tokens += load_pdf(citation, path)

    print(tokens * (0.0004 / 1000) * 5)


if __name__ == "__main__":
    main()
