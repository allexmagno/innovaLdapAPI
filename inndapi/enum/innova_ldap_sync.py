from enum import Enum


class InnovaLdapSyncEnum(Enum):
    PENDING = 'pending'
    VALID = 'valid'
    REJECTED = 'rejected'
    SYNC = 'sync'
    FAILED = 'failed'
    UPDATE = 'update'

    CHILD = 'child'
