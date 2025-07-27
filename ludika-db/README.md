# ludika-db

Schema and database configuration for Ludika.

Ludika uses PostgreSQL as its RDBMS.

## Database Schema

### Custom Types

| Type | Values | Description |
|------|--------|-------------|
| `user_role` | `'user'`, `'content_moderator'`, `'platform_administrator'` | User permission levels |
| `game_status` | `'draft'`, `'submitted'`, `'approved'`, `'rejected'` | Game submission workflow states |

### Tables

#### Users
User accounts (plural because `user` is reserved in PostgreSQL)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `uuid` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique user identifier |
| `visible_name` | TEXT | NOT NULL, CHECK (visible_name <> '') | Display name for the user |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE | User's email address |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| `last_login` | TIMESTAMP | DEFAULT NULL | Last login timestamp |
| `user_role` | user_role | DEFAULT 'user' | User's permission level |
| `enabled` | BOOLEAN | NOT NULL, DEFAULT TRUE | Whether the account is active |
| `password_hash` | TEXT | NULL | Hashed password for authentication |

#### Game
Games proposed by users

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY, NOT NULL | Unique game identifier |
| `name` | TEXT | NOT NULL, CHECK (name <> '') | Game title |
| `description` | TEXT | NULL | Game description |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Game creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |
| `url` | TEXT | NOT NULL | Game URL/link |
| `proposing_user` | UUID | REFERENCES Users(uuid) ON DELETE SET NULL | User who proposed the game |
| `status` | game_status | NOT NULL, DEFAULT 'draft' | Current workflow status |
| `approved_by` | UUID | REFERENCES Users(uuid) ON DELETE SET NULL | Moderator who approved the game |

#### GameImage
Images associated with games

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `game_id` | INTEGER | PRIMARY KEY, REFERENCES Game(id) ON DELETE CASCADE | Associated game |
| `position` | INTEGER | PRIMARY KEY, NOT NULL, CHECK (position >= 0) | Display order of the image |
| `image` | TEXT | NOT NULL | Image data/URL |

#### Tag
Tags that can be assigned to games

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Unique tag identifier |
| `name` | TEXT | NOT NULL | Tag name |
| `icon` | TEXT | DEFAULT NULL | Icon associated with the tag |

#### GameTag
Many-to-many relationship between games and tags

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `game_id` | INTEGER | PRIMARY KEY, REFERENCES Game(id) ON DELETE CASCADE | Associated game |
| `tag_id` | INTEGER | PRIMARY KEY, REFERENCES Tag(id) ON DELETE CASCADE | Associated tag |

#### ReviewCriterion
Criteria used for game reviews

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Unique criterion identifier |
| `name` | TEXT | NOT NULL, UNIQUE | Criterion name (e.g., "Ease of use", "Fun factor") |
| `description` | TEXT | NULL | Criterion description |

#### Review
Reviews submitted by users for games

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `game_id` | INTEGER | PRIMARY KEY, REFERENCES Game(id) ON DELETE CASCADE | Reviewed game |
| `reviewer_id` | UUID | PRIMARY KEY, REFERENCES Users(uuid) ON DELETE CASCADE | User who wrote the review |
| `review_text` | TEXT | NULL | Written review content |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Review creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

#### ReviewRating
Individual criterion ratings within a review

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `game_id` | INTEGER | PRIMARY KEY, REFERENCES Game(id) ON DELETE CASCADE | Associated game |
| `reviewer_id` | UUID | PRIMARY KEY, REFERENCES Users(uuid) ON DELETE CASCADE | User who provided the rating |
| `criterion_id` | INTEGER | PRIMARY KEY, REFERENCES ReviewCriterion(id) ON DELETE CASCADE | Rated criterion |
| `score` | INTEGER | NOT NULL, CHECK (score >= 1 AND score <= 5) | Rating score (1-5 scale) |

#### CriterionWeightProfile
Weight profiles for Multi-Criteria Decision Analysis (MCDA)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Unique profile identifier |
| `user_id` | UUID | REFERENCES Users(uuid) ON DELETE CASCADE | User who owns the profile (NULL for global profiles) |
| `name` | TEXT | NOT NULL | Profile name |
| `is_global` | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether this is a global profile |

#### CriterionWeight
Weights for each criterion in a weight profile

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `profile_id` | INTEGER | PRIMARY KEY, REFERENCES CriterionWeightProfile(id) ON DELETE CASCADE | Associated weight profile |
| `criterion_id` | INTEGER | PRIMARY KEY, REFERENCES ReviewCriterion(id) ON DELETE CASCADE | Associated criterion |
| `weight` | FLOAT | CHECK (weight >= 0) | Weight value for the criterion |

## Relationships

- **Users** → **Game**: One user can propose many games (proposing_user)
- **Users** → **Game**: One user can approve many games (approved_by)
- **Game** → **GameImage**: One game can have many images
- **Game** ↔ **Tag**: Many-to-many relationship through GameTag
- **Users** → **Review**: One user can review many games
- **Game** → **Review**: One game can have many reviews
- **Review** → **ReviewRating**: One review can have many criterion ratings
- **Users** → **CriterionWeightProfile**: One user can have many weight profiles
- **CriterionWeightProfile** → **CriterionWeight**: One profile can have many criterion weights

