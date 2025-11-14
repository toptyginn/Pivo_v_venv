from fastapi import FastAPI, Request, HTTPException
import document_cache_app.cache_manager as cache_manager
import document_cache_app.database as database

app = FastAPI()


@app.get("/documents")
async def documents(request: Request):
    try:
        user_id = int(request.headers["X-User-ID"])
    except:
        raise HTTPException(status_code=404)
    try:
        cache = await cache_manager.get_user_documents(user_id)
        if cache:
            return cache

    result = await database.get_documents()
    cache_manager.set_user_documents(user_id, result)

    if not result:
        raise HTTPException(status_code=404)
    else:
        return result









@app.get("/documents/{doc_id}")
async def document(request: Request, doc_id: int):
    try:
        user_id = int(request.headers["X-User-ID"])
    except:
        raise HTTPException(status_code=404)
    try:
        cache = await cache_manager.get_document_by_user(user_id, doc_id)
        if cache:
            return cache

    result = await database.get_document(doc_id)
    cache_manager.set_document_by_user(user_id, doc_id, result)

    if not result:
        raise HTTPException(status_code=404)
    else:
        return result


@app.get("/documents/shared")
async def documents_shared(request: Request):
    try:
        user_id = int(request.headers["X-User-ID"])
    except:
        raise HTTPException(status_code=404)
    try:
        cache = await cache_manager.get_shared_documents()
        if cache:
            return cache

    result = await database.get_shared_documents()
    cache_manager.set_shared_documents(result)

    if not result:
        raise HTTPException(status_code=404)
    else:
        return result


@app.post("/documents")
async def documents_shared(request: Request, documents: List[dict]):
    try:
        user_id = int(request.headers["X-User-ID"])
    except:
        raise HTTPException(status_code=404)

    for document in documents:
        database.create_document(document)



@app.put("/documents/{doc_id}")
async def documents_shared(request: Request, doc_id: int):
    try:
        user_id = int(request.headers["X-User-ID"])
    except:
        raise HTTPException(status_code=404)

    result = database.update_document(doc_id, title=request.body["title"], content=request.body["content"], category=request.body["category"], is_public=request.body["is_public"])
    if not result:
        raise HTTPException(status_code=404)



@app.post("/documents/{doc_id}/share")
async def documents_share(doc_id: int):
    try:



@app.delete("/documents/{doc_id}/share")
async def documents_share(doc_id: int):



@app.post("/auth/login")
async def documents_share():



@app.post("/admin/cache/clear")
async def clear_cache():



