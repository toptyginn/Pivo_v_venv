from document_cache_app.models import now_iso_time

fake_users_db = {
    1: {"id": 1, "username": "john_doe", "role": "user", "password": "password123"},
    2: {"id": 2, "username": "jane_smith", "role": "admin", "password": "admin123"},
    3: {"id": 3, "username": "bob_wilson", "role": "user", "password": "password456"}
}

fake_documents_db = {
    1: {"id": 1, "title": "Project Report", "content": "Project details...", "category": "reports", "is_public": False, "created_by": 1, "created_at": "2025-06-01T10:00:00", "last_modified": "2025-06-01T11:00:00"},
    2: {"id": 2, "title": "Team Guidelines", "content": "Guidelines for team...", "category": "guidelines", "is_public": True, "created_by": 2, "created_at": "2025-06-01T09:00:00", "last_modified": "2025-06-01T10:00:00"},
    3: {"id": 3, "title": "Urgent Update", "content": "Important update...", "category": "urgent", "is_public": False, "created_by": 1, "created_at": "2025-06-01T12:00:00", "last_modified": "2025-06-01T12:00:00"}
}

fake_permissions_db = {
    1: [{"user_id": 1, "permission_level": "write"}, {"user_id": 2, "permission_level": "read"}],
    2: [{"user_id": 2, "permission_level": "write"}, {"user_id": 3, "permission_level": "read"}],
    3: [{"user_id": 1, "permission_level": "write"}]
}

next_doc_id=4

def get_user(user_id: int):
    if type(user_id) is not int or user_id <= 0:
        return None
    return fake_users_db.get(user_id)

def get_document(doc_id: int):
    if type(doc_id) is not int or doc_id <= 0:
        return None
    return fake_documents_db.get(doc_id)

def get_documents(user_id: int):
    if type(user_id) is not int or user_id <= 0:
        return None
    docs = []
    for doc in fake_documents_db.values():
        if doc["created_by"] == user_id:
            docs.append(doc)
            continue
        perms = fake_permissions_db.get(doc["id"], [])
        for p in perms:
            if p["user_id"] == user_id:
                docs.append(doc)
                break
        if doc["is_public"] and doc not in docs:
            docs.append(doc)

    return docs

def get_shared_documents(user_id: int):
    if type(user_id) is not int or user_id <= 0:
        return []

    shared_docs = []
    for doc in fake_documents_db.values():
        if doc["is_public"]:
            shared_docs.append(doc)

    return shared_docs

def get_permissions(user_id: int):
    if type(user_id) is not int or user_id <= 0:
        return None
    return fake_permissions_db.get(user_id)

def create_document(title: str, content: str, category: str, is_public : bool, user_id: int):
    global next_doc_id

    if type(title) is not str or title.strip() == "":
        return None
    if type(content) is not str:
        return None
    if type(category) is not str or category.strip() == "":
        return None
    if type(is_public) is not bool:
        return None
    if get_user(user_id) is None:
        return None

    row={
        "id": next_doc_id,
        "title": title,
        "content": content,
        "category": category,
        "is_public": is_public,
        "created_by": user_id,
        "created_at": now_iso_time(),
        "last_modified": now_iso_time()
    }

    fake_documents_db[next_doc_id] = row
    fake_permissions_db[next_doc_id] = [{"user_id": user_id, "permission_level": "write"}]
    next_doc_id += 1
    return row

def update_document(doc_id: int, title: str or None, content: str or None, category: str or None, is_public: bool or None):
    if type(doc_id) is not int or doc_id <= 0:
        return None
    row = fake_documents_db.get(doc_id)
    if not row:
        return None

    if title is not None:
        row["title"] = title
    if content is not None:
        row["content"] = content
    if category is not None:
        row["category"] = category
    if is_public is not None:
        row["is_public"] = is_public

    row["last_modified"] = now_iso_time()

    return row

def add_permission(doc_id: int, user_id: int, permission_level: str):
    fake_permissions_db.setdefault(doc_id, []).append(
        {"user_id": user_id, "permission_level": permission_level}
    )

def remove_permission(doc_id: int, user_id: int):
    perms = fake_permissions_db.get(doc_id, [])
    fake_permissions_db[doc_id] = [p for p in perms if p["user_id"] != user_id]
