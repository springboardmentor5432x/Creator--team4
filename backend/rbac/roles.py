from enum import Enum
class Role(str,Enum):
    CREATOR="Creator"
    AGENCY="Agency"
    MARKETING_TEAM="Marketing Team"
    ADMINISTRATOR="Administrator"