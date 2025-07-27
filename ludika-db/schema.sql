-- PostgreSQL schema file

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
        -- User roles
        CREATE TYPE user_role AS ENUM ('user', 'content_moderator', 'platform_administrator');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'game_status') THEN
        -- Game statuses
        CREATE TYPE game_status AS ENUM ('draft', 'submitted', 'approved', 'rejected');
    END IF;
END $$;

-- User accounts (plural because `user` is reserved in PostgreSQL)
CREATE TABLE IF NOT EXISTS Users (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visible_name TEXT NOT NULL CHECK (visible_name <> ''),
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login TIMESTAMP DEFAULT NULL,
    user_role user_role DEFAULT 'user',
    enabled BOOLEAN DEFAULT TRUE NOT NULL,
    password_hash TEXT
);

-- Games proposed by users
CREATE TABLE IF NOT EXISTS Game (
    id SERIAL PRIMARY KEY NOT NULL,
    name TEXT NOT NULL CHECK (name <> ''),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    url TEXT NOT NULL,
    proposing_user UUID REFERENCES Users(uuid) ON DELETE SET NULL,
    status game_status DEFAULT 'draft' NOT NULL,
    approved_by UUID REFERENCES Users(uuid) ON DELETE SET NULL
);

-- Images of a game
CREATE TABLE IF NOT EXISTS GameImage (
    game_id INTEGER REFERENCES Game(id) ON DELETE CASCADE,
    position INTEGER NOT NULL CHECK (position >= 0),
    image TEXT NOT NULL,
    PRIMARY KEY (game_id, position)
);

-- Tags that can be assigned to games
CREATE TABLE IF NOT EXISTS Tag (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    icon TEXT DEFAULT NULL
);

-- Tags assigned to each game
CREATE TABLE IF NOT EXISTS GameTag (
    game_id INTEGER REFERENCES Game(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES Tag(id) ON DELETE CASCADE,
    PRIMARY KEY (game_id, tag_id)
);

-- Criteria used for reviews (e.g. "Ease of use", "Fun factor", "Learning", etc.)
CREATE TABLE IF NOT EXISTS ReviewCriterion (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- Review of a game by a user, with ratings for each criterion
CREATE TABLE IF NOT EXISTS Review (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES Game(id) ON DELETE CASCADE,
    reviewer_id UUID REFERENCES Users(uuid) ON DELETE CASCADE,
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (game_id, reviewer_id)
);

-- Ratings for each criterion in a review
CREATE TABLE IF NOT EXISTS ReviewRating (
    review_id INTEGER REFERENCES Review(id) ON DELETE CASCADE,
    criterion_id INTEGER REFERENCES ReviewCriterion(id) ON DELETE CASCADE,
    score INTEGER CHECK (score >= 1 AND score <= 5),
    PRIMARY KEY (review_id, criterion_id)
);

-- Weight profile defined by a user (or admin if global), to be used for MCDA (Multi-Criteria Decision Analysis)
CREATE TABLE IF NOT EXISTS CriterionWeightProfile (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES Users(uuid) ON DELETE CASCADE,
    name TEXT NOT NULL,
    is_global BOOLEAN NOT NULL DEFAULT FALSE
);

-- Weights for each criterion in a weight profile
CREATE TABLE IF NOT EXISTS CriterionWeight (
    profile_id INTEGER REFERENCES CriterionWeightProfile(id) ON DELETE CASCADE,
    criterion_id INTEGER REFERENCES ReviewCriterion(id) ON DELETE CASCADE,
    weight FLOAT CHECK (weight >= 0),
    PRIMARY KEY (profile_id, criterion_id)
);
