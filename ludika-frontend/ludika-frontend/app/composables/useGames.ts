import type { GamePublic } from '../../types/game'
import { useAuth } from './useAuth'

export const useGames = () => {
  const games = ref<GamePublic[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const { authenticatedFetch } = useAuth()

  const fetchGames = async (searchQuery?: string) => {
    loading.value = true
    error.value = null

    try {
      // Build the URL with search query if provided
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

  return {
    games: readonly(games),
    loading: readonly(loading),
    error: readonly(error),
    fetchGames
  }
} 