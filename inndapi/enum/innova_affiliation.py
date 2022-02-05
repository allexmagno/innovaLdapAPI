from enum import Enum


class InnovaAffiliationTypeEnum(Enum):
    STAFF = 'staff'
    MEMBER = 'member'
    PARTNER = 'partner'


class InnovaAffiliationSubTypeEnum(Enum):
    POSITION = 'position'
    EMPLOYEE = 'employee'
    SCHOLARSHIP = 'scholarship'
    OTHER = 'other'
    COMPANY = 'company'
    COMPANY_AFFILIATED = 'company_affiliated'
    STARTUP = 'startup'
    STARTUP_AFFILIATED = 'startup_affiliated'
    ENTREPRENEUR = 'entrepreneur'
    EDU = 'edu'
    GOV = 'gov'
    COM = 'com'
    STAKEHOLDERS = 'stakeholders'
