import type { GamePublic } from '../../types/game'
import { useAuth } from './useAuth'

export const useGames = () => {
  const games = ref<GamePublic[]>([])
  const game = ref<GamePublic | null>(null)
  const loading = ref(false)
  const gameLoading = ref(false)
  const error = ref<string | null>(null)
  const gameError = ref<string | null>(null)

  const { authenticatedFetch } = useAuth()

  const fetchGames = async (searchQuery?: string) => {
    loading.value = true
    error.value = null

    try {
      let url = '/api/v1/games/'
      if (searchQuery && searchQuery.trim()) {
        url += `?search=${encodeURIComponent(searchQuery.trim())}`
      }

      const response = await authenticatedFetch<GamePublic[]>(url)
      games.value = response
    } catch (err) {
      error.value = 'Failed to fetch games'
      console.error('Error fetching games:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchGameById = async (id: string | number) => {
    gameLoading.value = true
    gameError.value = null

    try {
      const response = await authenticatedFetch<GamePublic>(`/api/v1/games/${id}`)
      game.value = response
    } catch (err) {
      gameError.value = 'Failed to fetch game'
      console.error('Error fetching game:', err)
    } finally {
      gameLoading.value = false
    }
  }

  return {
    games: readonly(games),
    game: readonly(game),
    loading: readonly(loading),
    gameLoading: readonly(gameLoading),
    error: readonly(error),
    gameError: readonly(gameError),
    fetchGames,
    fetchGameById
  }
} 