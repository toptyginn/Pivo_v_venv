from document_cache_app.database import fake_permissions_db, remove_permission, add_permission

class PermissionsManager:
    def __init__(self):
        self.user_permissions = fake_permissions_db

    async def set_permission(self, user_id=None, permission=None, document_id=None) -> dict[int, dict[list]]:
        if user_id is None or permission is None:
            raise ValueError("user_id and permission must be provided")
        if document_id is None:
            document_id  = max(self.user_permissions.keys(), default=1)+1
        try:
            add_permission(document_id, user_id, permission)
            self.user_permissions[document_id] = fake_permissions_db[document_id]
        except ValueError:
            raise KeyError("Failed to set permission for the given user and document ID")
        return self.user_permissions

    async def revoke_permission(self, user_id, permission, document_id) -> dict[int, dict[list]]:
        if document_id in self.user_permissions:
            try:
                remove_permission(document_id, user_id)
                self.user_permissions[document_id] = fake_permissions_db[document_id]
            except ValueError:
                raise KeyError("Permission not found for the given user and document ID")
        else:
            raise KeyError("Document ID not found in permissions database")
        return self.user_permissions
        

    async def has_permission(self, user_id, permission, document_id) -> bool:
        return self.user_permissions.get(document_id) == {"user_id": user_id, "permission_level": permission}

    async def list_permissions(self, user_id) -> list[dict[int, str]]:
        res = []
        for doc_id, perm in self.user_permissions.items():
            if perm["user_id"] == user_id:
                res.append({doc_id: perm["permission_level"]})
        return res