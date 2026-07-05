from rbac.permissions import permissions

def has_permission(role, permission):
    allowed_permissions = permissions.get(role, [])

    if "*" in allowed_permissions:
        return True

    return permission in allowed_permissions