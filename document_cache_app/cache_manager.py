import redis.asyncio as redis
import json
from typing import Optional, Any, List
from dotenv import load_dotenv
import os

load_dotenv()

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)

try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
except redis.exceptions.ConnectionError as e:
    redis_client = None

USER_DOCS_TTL = 5 * 60
SHARED_DOCS_TTL = 2 * 60
SINGLE_DOC_TTL = 10 * 60
PERMISSIONS_TTL = 15 * 60


def _get_user_docs_key(user_id: int) -> str:
    return f"user:{user_id}:documents"

def _get_shared_docs_key() -> str:
    return "shared:documents"

def _get_single_doc_key(user_id: int, doc_id: int) -> str:
    return f"user:{user_id}:document:{doc_id}"

def _get_permissions_key(doc_id: int) -> str:
    return f"document:{doc_id}:permissions"


def get_cache(key: str) -> Optional[Any]:
    if not redis_client:
        return None
        
    try:
        cached_data = redis_client.get(key)
        if cached_data:
            return json.loads(cached_data)
        return None
    except redis.exceptions.RedisError as e:
        return None
    except json.JSONDecodeError as e:
        invalidate_cache(key)
        return None

def set_cache(key: str, value: Any, ttl: int):
    if not redis_client:
        return
        
    try:
        serialized_data = json.dumps(value)
        redis_client.setex(key, ttl, serialized_data)
    except redis.exceptions.RedisError as e:
        pass
    except TypeError as e:
        pass

def invalidate_cache(key: str):
    if not redis_client:
        return
        
    try:
        redis_client.delete(key)
    except redis.exceptions.RedisError as e:
        pass

def invalidate_cache_pattern(pattern: str) -> List[str]:
    if not redis_client:
        return []

    invalidated_keys = []
    try:
        for key in redis_client.scan_iter(match=pattern):
            redis_client.delete(key)
            invalidated_keys.append(key)
            
        return invalidated_keys
    except redis.exceptions.RedisError as e:
        return invalidated_keys

def get_user_documents(user_id: int) -> Optional[List[dict]]:
    return get_cache(_get_user_docs_key(user_id))

def set_user_documents(user_id: int, documents: List[dict]):
    set_cache(_get_user_docs_key(user_id), documents, USER_DOCS_TTL)

def invalidate_user_documents(user_id: int):
    invalidate_cache(_get_user_docs_key(user_id))

def invalidate_user_documents_for_list(user_ids: List[int]):
    if not redis_client:
        return
        
    try:
        pipe = redis_client.pipeline()
        keys_to_delete = []
        for user_id in user_ids:
            key = _get_user_docs_key(user_id)
            keys_to_delete.append(key)
            pipe.delete(key)
        pipe.execute()
    except redis.exceptions.RedisError as e:
        pass

def get_shared_documents() -> Optional[List[dict]]:
    return get_cache(_get_shared_docs_key())

def set_shared_documents(documents: List[dict]):
    set_cache(_get_shared_docs_key(), documents, SHARED_DOCS_TTL)

def invalidate_shared_documents():
    invalidate_cache(_get_shared_docs_key())

def get_document_by_user(user_id: int, doc_id: int) -> Optional[dict]:
    return get_cache(_get_single_doc_key(user_id, doc_id))

def set_document_by_user(user_id: int, doc_id: int, document: dict):
    set_cache(_get_single_doc_key(user_id, doc_id), document, SINGLE_DOC_TTL)

def invalidate_document_for_all_users(doc_id: int) -> List[str]:
    pattern = _get_single_doc_key("*", doc_id)
    return invalidate_cache_pattern(pattern)

def invalidate_specific_user_document(user_id: int, doc_id: int):
    invalidate_cache(_get_single_doc_key(user_id, doc_id))

def get_document_permissions(doc_id: int) -> Optional[List[dict]]:
    return get_cache(_get_permissions_key(doc_id))

def set_document_permissions(doc_id: int, permissions: List[dict]):
    set_cache(_get_permissions_key(doc_id), permissions, PERMISSIONS_TTL)

def invalidate_document_permissions(doc_id: int):
    invalidate_cache(_get_permissions_key(doc_id))

def clear_all_cache() -> bool:
    if not redis_client:
        return False
        
    try:
        redis_client.flushdb()
        return True
    except redis.exceptions.RedisError as e:
        return False