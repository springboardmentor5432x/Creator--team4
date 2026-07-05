from rbac.roles import Role
from rbac.authorization import has_permission

print("===== RBAC TEST =====")

tests = [
    (Role.CREATOR, "view_dashboard"),
    (Role.CREATOR, "manage_users"),
    (Role.AGENCY, "manage_creators"),
    (Role.MARKETING_TEAM, "view_reports"),
    (Role.ADMINISTRATOR, "manage_users")
]

for role, permission in tests:
    if has_permission(role, permission):
        print(f"{role} -> {permission} : Access Granted")
    else:
        print(f"{role} -> {permission} : Access Denied")