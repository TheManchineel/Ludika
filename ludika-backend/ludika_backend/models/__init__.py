from . import games, users, review

from .games import Game, GamePublic, GameWithReviews, Tag
from .users import User, UserPublic
from .review import Review, ReviewPublic, ReviewCriterion, CriterionWeightProfile

# Rebuild models to resolve forward references (Python is a *****)
Game.model_rebuild()
GamePublic.model_rebuild()
GameWithReviews.model_rebuild()
Tag.model_rebuild()

User.model_rebuild()
UserPublic.model_rebuild()

Review.model_rebuild()
ReviewPublic.model_rebuild()
ReviewCriterion.model_rebuild()
CriterionWeightProfile.model_rebuild()
