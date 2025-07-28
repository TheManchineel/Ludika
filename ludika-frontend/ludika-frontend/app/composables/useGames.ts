import type { GamePublic } from '../../types/game'

export const useGames = () => {
  const games = ref<GamePublic[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchGames = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await $fetch<GamePublic[]>('/api/v1/games/')
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