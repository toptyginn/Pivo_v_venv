from httpx import AsyncClient
from fastapi import FastAPI, Request, HTTPException
from parso.cache import clear_cache

app = FastAPI()
redis = createClient()

@app.get("/documents")
async def documents(request: Request):
    try:
        user_id =  request.headers["X-User-ID"]
    except:
        raise HTTPException(status_code=404)

    try:






@app.get("/documents/{doc_id}")
async def documents(request: Request, doc_id: int):
    try:
        user_id =  request.headers["X-User-ID"]



@app.get("/documents/shared")
async def documents_shared():


@app.post("/documents")
async def documents_shared():




@app.put("/documents/{doc_id}")
async def documents_shared(doc_id: int):



@app.post("/documents/{doc_id}/share")
async def documents_share(doc_id: int):



@app.delete("/documents/{doc_id}/share")
async def documents_share(doc_id: int):



@app.post("/auth/login")
async def documents_share():



@app.post("/admin/cache/clear")
async def clear_cache():



