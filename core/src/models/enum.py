import enum


class AccessLevelEnum(enum.Enum):
    director = "director"
    manager = "manager"
    admin = "admin"

    @property
    def level(self) -> int:
        mapping = {
            AccessLevelEnum.manager: 1,
            AccessLevelEnum.director: 2,
            AccessLevelEnum.admin: 3,
        }
        return mapping[self]


class EducationalProgramPartnerEnum(enum.Enum):
    OO = "OO"
    Industry = "Industry"
    Science = "Science"
    Other = "Other"


class EducationalProgramLanguageTypeEnum(enum.Enum):
    RUSSIAN = "RUSSIAN"
    ENGLISH = "ENGLISH"
    PARTIALLY_ENGLISH = "PARTIALLY_ENGLISH"


class NetworkFormEnum(enum.Enum):
    NO = "NO"
    FEFU_BASIC = "FEFU_BASIC"
    FEFU_PARTICIPANT = "FEFU_PARTICIPANT"
    UNKNOWN = "UNKNOWN"


class EducationalFormEnum(enum.Enum):
    OFFLINE = "OFFLINE"
    ONLINE = "ONLINE"
    BOTH = "BOTH"


class EducationalstandardEnum(enum.Enum):
    FGOS_VO_3_PLUS = "ФГОС ВО (3++)"
    OS_VO_DVFU = "ОС ВО ДВФУ"


class DeleteBehaviorEnum(enum.Enum):
    RESTRICT = "RESTRICT"
    CASCADE = "CASCADE"
    SET_NULL = "SET NULL"
