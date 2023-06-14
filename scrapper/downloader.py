#!/usr/bin/env python
import logging
import asyncio
import sys

import aiohttp
import aiofiles
from aiohttp import ClientSession
from bs4 import BeautifulSoup, Tag

import utils.database as db


logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("Scrapper")
logger.setLevel(logging.INFO)

pubmed_url = "https://pubmed.ncbi.nlm.nih.gov/"
scihub_url = "https://sci-hub.st/"


def paper_path(paper: str) -> str:
    return f"./papers/{paper.strip()}pdf"


def extract_download_link(scihub_page: str) -> str:
    soup = BeautifulSoup(scihub_page, "html.parser")
    buttons_div = soup.find("div", id="buttons")

    if not isinstance(buttons_div, Tag):
        raise Exception("Could not find paper")

    button = buttons_div.find("button")

    if not isinstance(button, Tag):
        raise Exception("Could not find paper")

    js = button.attrs["onclick"]

    [_, link] = js.split("=", 1)
    link = link.strip("'")
    logger.info(f"LINK: {link}")

    if link.startswith("//"):
        link = link.replace("//", "https://")
        link = link.replace("?download=true", "")
    elif link.startswith("/"):
        link = scihub_url + link

    return link


async def fetch_doi(paper: str, session: ClientSession) -> str:
    logger.info(f"FETCHING PAPER DOI: {paper}")
    response = await session.get(pubmed_url, params={"term": paper})

    soup = BeautifulSoup(await response.text(), "html.parser")
    doi_anchor = soup.find("a", class_="id-link")

    if not isinstance(doi_anchor, Tag):
        raise Exception(f"Could not find DOI in page for paper '{paper}'")

    return doi_anchor.text.strip()


async def fetch_scihub_page(doi: str, session: ClientSession) -> str:
    logger.info(f"FETCHING SCIHUB PAGE: {doi}")
    body = {"request": doi}
    response = await session.post(scihub_url, data=body)
    return await response.text()


async def fetch_paper(paper: str, session: ClientSession):
    try:
        doi = await fetch_doi(paper, session)
        scihub_page = await fetch_scihub_page(doi, session)

        link = extract_download_link(scihub_page)

        logger.info(f"DOWNLOADING FROM: {link}")
        response = await session.get(link)

        path = paper_path(paper)
        logger.info(f"DOWNLOADED TO: {path}")

        async with aiofiles.open(path, "wb") as f:
            await f.write(await response.read())

        db.add_doi_to_citation(doi, paper, was_downloaded=True)
        db.commit()

    except aiohttp.ClientError as e:
        error = "iohttp exception for paper %s [%s]: %s"
        status = getattr(e, "status", None),
        message = getattr(e, "message", None)

        logger.error(error, paper, status, message)
    except Exception as e:
        raise e


async def worker(session: ClientSession, queue: asyncio.Queue):
    while True:
        paper = await queue.get()
        try:
            await fetch_paper(paper, session)
        except Exception as e:
            logger.error(e)
        finally:
            queue.task_done()


async def main():
    references = []

    for ref in db.read_doiless_citations():
        [destructured] = ref
        references.append(destructured)

    async with ClientSession() as session:
        q = asyncio.Queue()

        workers = [
            asyncio.create_task(worker(session, q))
            for _ in range(10)
        ]

        for reference in references:
            q.put_nowait(reference.strip())

        await q.join()
        for w in workers:
            w.cancel()


if __name__ == "__main__":
    asyncio.run(main())
