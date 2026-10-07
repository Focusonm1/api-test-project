def auth_headers(token):
    if token is None:
        return {}
    return {"Authorization": f"Bearer {token}"}