export interface TagPublic {
  id: number
  name: string
  icon: string | null
}

export interface GameImage {
  position: number
  image: string
}

export interface ReviewAuthor {
  visible_name: string
  user_role: string
  enabled: boolean
  uuid: string
  created_at: string
  last_login: string | null
}

export interface ReviewCriterion {
  id: number
  name: string
  description: string
}

export interface ReviewRating {
  score: number
  criterion: ReviewCriterion
}

export interface GameReview {
  review_text: string
  game_id: number
  reviewer_id: string
  author: ReviewAuthor
  created_at: string
  updated_at: string
  ratings: readonly ReviewRating[]
}

export interface GamePublic {
  id: number
  name: string
  description: string
  url: string
  created_at: string
  updated_at: string
  tags: readonly TagPublic[]
  images: readonly GameImage[]
  status: string
  proposing_user: string | null
  reviews?: readonly GameReview[]
  total_score?: number
}

export interface GameCreate {
  name: string
  description: string
  url: string
  tags: number[]
}

export interface GameUpdate {
  name?: string
  description?: string
  url?: string
  tags?: number[]
} 