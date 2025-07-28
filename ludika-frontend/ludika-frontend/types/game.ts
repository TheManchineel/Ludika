export interface TagPublic {
  id: number
  name: string
  icon: string | null
}

export interface GameImage {
  position: number
  image: string
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
} 