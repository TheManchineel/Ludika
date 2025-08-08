from . import games, users, review

from .games import Game, GamePublic, GameWithReviews, Tag
from .users import User, UserPublic
from .review import Review, ReviewPublic, ReviewCriterion, CriterionWeightProfile

# Rebuild models to resolve forward references (Python is a *****)
all_models = (
    Game,
    GamePublic,
    GameWithReviews,
    Tag,
    User,
    UserPublic,
    Review,
    ReviewPublic,
    ReviewCriterion,
    CriterionWeightProfile
)

for model in all_models:
    model.model_rebuild()