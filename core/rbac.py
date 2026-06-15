import enum

from core.db.base import UserRole


class Permission(str, enum.Enum):
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    DATASOURCE_READ = "datasource:read"
    DATASOURCE_WRITE = "datasource:write"
    DATASET_READ = "dataset:read"
    DATASET_WRITE = "dataset:write"
    SCAN_TRIGGER = "scan:trigger"
    SCAN_READ = "scan:read"
    AUDIT_READ = "audit:read"

    CATEGORY_WRITE = "category:write"
    CATEGORY_READ = "category:read"
    CATEGORY_UPDATE = "category:update"
    CATEGORY_DELETE = "category:delete"

    TAG_ASSIGN = "tag:assign"
    TAG_CREATE = "tag:create"
    TAG_READ = "tag:read"
    TAG_DELETE = "tag:delete"



ROLE_PERMISSIONS: dict[UserRole, frozenset[Permission]] = {
    UserRole.VIEWER: frozenset(
        {
            Permission.DATASOURCE_READ,
            Permission.DATASET_READ,
            Permission.AUDIT_READ,
            Permission.TAG_READ,
            Permission.CATEGORY_READ,
            Permission.SCAN_READ
        }
    ),
    UserRole.EDITOR: frozenset(
        {
            Permission.DATASOURCE_READ,
            Permission.DATASOURCE_WRITE,
            Permission.DATASET_READ,
            Permission.DATASET_WRITE,
            Permission.SCAN_TRIGGER,
            Permission.AUDIT_READ,
            Permission.CATEGORY_WRITE,
            Permission.CATEGORY_READ,
            Permission.CATEGORY_UPDATE,
            Permission.CATEGORY_DELETE,
            Permission.TAG_READ,
            Permission.TAG_ASSIGN,
            Permission.TAG_CREATE,
            Permission.TAG_DELETE
        }
    ),
    UserRole.ADMIN: frozenset(Permission),
}


def role_has_permission(role: UserRole, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, frozenset())


def role_at_least(role: UserRole, minimum: UserRole) -> bool:
    hierarchy = {UserRole.VIEWER: 0, UserRole.EDITOR: 1, UserRole.ADMIN: 2}
    return hierarchy.get(role, -1) >= hierarchy.get(minimum, 0)
