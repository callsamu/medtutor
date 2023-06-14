import asyncio
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware


from ai import AI
from searcher import DocumentSearcher


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

searcher = DocumentSearcher()
ai = AI(searcher.as_retriever())


@app.get("/document")
async def document(query: str):
    return searcher.search(query)


@app.get("/debug/stream")
async def debug():
    async def counter():
        i = 0
        while True:
            i += 1
            await asyncio.sleep(0.01)
            data = json.dumps({"token": f" {i} "})
            yield f"data: {data}\n\n"

    return StreamingResponse(counter(), media_type="text/event-stream")


@app.get("/ask")
async def ask(question: str):
    return StreamingResponse(
        ai.ask(question),
        media_type="text/event-stream"
    )


@app.get("/ask/stream")
async def root(question: str):
    return StreamingResponse(
        ai.ask_stream(question),
        media_type="text/event-stream"
    )
