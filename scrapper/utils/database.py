#!/usr/bin/env python

import sys
import sqlite3
import logging
from typing import Iterable

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("DB")
logger.setLevel(logging.INFO)

connection = sqlite3.connect('database.db')
cursor = connection.cursor()


def commit():
    connection.commit()


def insert_references_as_citations(references: list[str]):
    query = """
        INSERT INTO papers (citation) VALUES (?)
    """
    data = [(ref, ) for ref in references]
    cursor.executemany(query, data)
    connection.commit()


def read_doiless_citations() -> Iterable[str]:
    query = """
        SELECT citation FROM papers
        WHERE doi IS NULL
    """

    for citation in cursor.execute(query):
        yield citation


def read_downloaded_citations() -> Iterable[str]:
    query = """
        SELECT citation FROM papers
        WHERE doi IS NOT NULL
        AND is_downloaded = 1
    """

    for citation in cursor.execute(query):
        yield citation


def add_doi_to_citation(doi: str, citation: str, was_downloaded: bool = False):
    query = """
        UPDATE papers
        SET doi = ?, is_downloaded = ?
        WHERE citation = ?
    """

    downloaded_flag = 1 if was_downloaded else 0
    cursor.execute(query, (doi, downloaded_flag, citation))



def create_table_if_not_exists():
    logger.info("Creating SQL table...")

    query = """
        CREATE TABLE IF NOT EXISTS papers (
            citation TEXT UNIQUE,
            doi TEXT UNIQUE DEFAULT NULL,
            is_downloaded INTEGER DEFAULT 0,
            was_embedded INTEGER DEFAULT 0
        )
    """

    cursor.execute(query)
