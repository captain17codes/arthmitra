from enum import Enum


class OrgType(str, Enum):
    NRLM = "nrlm"
    CSC = "csc"
    NGO = "ngo"
    SCA = "sca"
    OTHER = "other"
    INDIVIDUAL = "individual"  # one per self-registered person; isolates their data


class UserRole(str, Enum):
    AGENT = "agent"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"
    CITIZEN = "citizen"  # the entrepreneur using the app for themselves


class CoordSource(str, Enum):
    OSM = "osm"
    MANUAL = "manual"
    OTHER = "other"


class SectorType(str, Enum):
    RURAL = "rural"
    URBAN = "urban"


class BusinessSector(str, Enum):
    MANUFACTURING = "manufacturing"
    SERVICE = "service"
    TRADING = "trading"
    AGRI_ALLIED = "agri_allied"


class BenchmarkConfidence(str, Enum):
    OFFICIAL = "official"
    SECONDARY = "secondary"
    ESTIMATE = "estimate"


class SchemeStatus(str, Enum):
    VERIFIED = "verified"
    CONFLICT = "conflict"
    UNVERIFIED = "unverified"
    RETIRED = "retired"


class TriState(str, Enum):
    YES = "yes"
    NO = "no"
    UNKNOWN = "unknown"


class ConsentMethod(str, Enum):
    VOICE = "voice"
    TAP = "tap"


class CaseStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    DPR_GENERATED = "dpr_generated"
    APPLIED = "applied"
    SANCTIONED = "sanctioned"
    REJECTED = "rejected"
    DISBURSED = "disbursed"
    CLOSED = "closed"


class InputSource(str, Enum):
    AGENT = "agent"
    DEFAULT = "default"
    VOICE = "voice"


class SocialCategory(str, Enum):
    SC = "SC"
    ST = "ST"
    OBC = "OBC"
    VJNT = "VJNT"
    SBC = "SBC"
    GENERAL = "General"


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
