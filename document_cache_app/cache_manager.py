from redis import exceptions
import redis.asyncio as redis
import json
from typing import Optional, Any, List
from dotenv import load_dotenv
import os

load_dotenv()

class CacheManager:
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

    USER_DOCS_TTL = 5 * 60
    SHARED_DOCS_TTL = 2 * 60
    SINGLE_DOC_TTL = 10 * 60
    PERMISSIONS_TTL = 15 * 60

    def __init__(self):
        try:
            self.redis_client = redis.Redis(host=self.REDIS_HOST, port=self.REDIS_PORT, decode_responses=True)
        except exceptions.ConnectionError:
            self.redis_client = None


    @staticmethod
    def _get_user_docs_key(user_id: int) -> str:
        return f"user:{user_id}:documents"

    @staticmethod
    def _get_shared_docs_key() -> str:
        return "shared:documents"

    @staticmethod
    def _get_single_doc_key(user_id: int, doc_id: int) -> str:
        return f"user:{user_id}:document:{doc_id}"

    @staticmethod
    def _get_permissions_key(doc_id: int) -> str:
        return f"document:{doc_id}:permissions"

    async def get_cache(self, key: str) -> Optional[Any]:
        if not self.redis_client:
            return None
        
        try:
            cached_data = await self.redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except exceptions.RedisError as e:
            return None
        except json.JSONDecodeError as e:
            await self.invalidate_cache(key)
            return None

    async def set_cache(self, key: str, value: Any, ttl: int):
        if not self.redis_client:
            return
        
        try:
            serialized_data = json.dumps(value)
            await self.redis_client.setex(key, ttl, serialized_data)
        except exceptions.RedisError as e:
            pass
        except TypeError as e:
            pass

    async def invalidate_cache(self, key: str):
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.delete(key)
        except exceptions.RedisError as e:
            pass

    async def invalidate_cache_pattern(self, pattern: str) -> List[str]:
        if not self.redis_client:
            return []

        invalidated_keys = []
        try:
            async for key in self.redis_client.scan_iter(match=pattern):
                await self.redis_client.delete(key)
                invalidated_keys.append(key)
            
            return invalidated_keys
        except exceptions.RedisError as e:
            return invalidated_keys

    async def get_user_documents(self, user_id: int) -> Optional[List[dict]]:
        return await self.get_cache(self._get_user_docs_key(user_id))

    async def set_user_documents(self, user_id: int, documents: List[dict]):
        await self.set_cache(self._get_user_docs_key(user_id), documents, self.USER_DOCS_TTL)

    async def invalidate_user_documents(self, user_id: int):
        await self.invalidate_cache(self._get_user_docs_key(user_id))

    async def invalidate_user_documents_for_list(self, user_ids: List[int]):
        if not self.redis_client:
            return
        
        try:
            async with self.redis_client.pipeline() as pipe:
                for user_id in user_ids:
                    key = self._get_user_docs_key(user_id)
                    pipe.delete(key)
                await pipe.execute()
        except exceptions.RedisError as e:
            pass

    async def get_shared_documents(self) -> Optional[List[dict]]:
        return await self.get_cache(self._get_shared_docs_key())

    async def set_shared_documents(self, documents: List[dict]):
        await self.set_cache(self._get_shared_docs_key(), documents, self.SHARED_DOCS_TTL)

    async def invalidate_shared_documents(self):
        await self.invalidate_cache(self._get_shared_docs_key())

    async def get_document_by_user(self, user_id: int, doc_id: int) -> Optional[dict]:
        return await self.get_cache(self._get_single_doc_key(user_id, doc_id))

    async def set_document_by_user(self, user_id: int, doc_id: int, document: dict):
        await self.set_cache(self._get_single_doc_key(user_id, doc_id), document, self.SINGLE_DOC_TTL)

    async def invalidate_document_for_all_users(self, doc_id: int) -> List[str]:
        pattern = self._get_single_doc_key("*", doc_id)
        return await self.invalidate_cache_pattern(pattern)

    async def invalidate_specific_user_document(self, user_id: int, doc_id: int):
        await self.invalidate_cache(self._get_single_doc_key(user_id, doc_id))

    async def get_document_permissions(self, doc_id: int) -> Optional[List[dict]]:
        return await self.get_cache(self._get_permissions_key(doc_id))

    async def set_document_permissions(self, doc_id: int, permissions: List[dict]):
        await self.set_cache(self._get_permissions_key(doc_id), permissions, self.PERMISSIONS_TTL)

    async def invalidate_document_permissions(self, doc_id: int):
        await self.invalidate_cache(self._get_permissions_key(doc_id))

    async def clear_all_cache(self) -> bool:
        if not self.redis_client:
            return False
        
        try:
            await self.redis_client.flushdb()
            return True
        except exceptions.RedisError as e:
            return False

    async def close(self):
        if self.redis_client:
            await self.redis_client.close()

cache = CacheManager()
