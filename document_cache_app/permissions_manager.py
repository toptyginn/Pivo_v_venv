from document_cache_app.database import fake_permissions_db

class PermissionsManager:
    def __init__(self):
        self.user_permissions = fake_permissions_db

    def set_permission(self, user_id=None, permission=None, document_id=None) -> dict[int, dict[list]]:
        if user_id is None or permission is None:
            raise ValueError("user_id and permission must be provided")
        if document_id is None:
            document_id  = max(self.user_permissions.keys(), default=1)+1
        fake_permissions_db.update({document_id: {"user_id": user_id, "permission_level": permission}})
        return self.user_permissions

    def revoke_permission(self, user_id, permission, document_id) -> dict[int, dict[list]]:
        if document_id in fake_permissions_db:
            try:
                fake_permissions_db[document_id].remove({"user_id": user_id, "permission_level": permission})
            except ValueError:
                raise KeyError("Permission not found for the given user and document ID")
        else:
            raise KeyError("Document ID not found in permissions database")
        return self.user_permissions
        

    def has_permission(self, user_id, permission, document_id) -> bool:
        return fake_permissions_db.get(document_id) == {"user_id": user_id, "permission_level": permission}

    def list_permissions(self, user_id) -> list[dict[int, str]]:
        res = []
        for doc_id, perm in fake_permissions_db.items():
            if perm["user_id"] == user_id:
                res.append({doc_id: perm["permission_level"]})
        return res