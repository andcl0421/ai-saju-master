from .user import User, PushSubscription
from .saju import SajuProfile, Gender
from .fortune import DailyFortune, FortunePhrase
from .log import FortuneLog
from app.db.database import Base
# Alembic이나 외부에서 참조할 때 편리하도록 모든 모델을 리스트업합니다.
__all__ = [
    "Base",
    "User",
    "PushSubscription",
    "SajuProfile",
    "Gender",
    "DailyFortune",
    "FortunePhrase",
    "FortuneLog",
]