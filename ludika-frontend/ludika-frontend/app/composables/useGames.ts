import type { GamePublic, GameUpdate, GameCreate, TagPublic } from '../../types/game'
import { useAuth } from './useAuth'

export const useGames = () => {
  const games = ref<GamePublic[]>([])
  const game = ref<GamePublic | null>(null)
  const tags = ref<TagPublic[]>([])
  const totalCount = ref(0)
  const currentPage = ref(0)
  const itemsPerPage = ref(50)
  const loading = ref(false)
  const gameLoading = ref(false)
  const tagsLoading = ref(false)
  const updateLoading = ref(false)
  const error = ref<string | null>(null)
  const gameError = ref<string | null>(null)
  const tagsError = ref<string | null>(null)
  const updateError = ref<string | null>(null)

  const { authenticatedFetch, withSSRCheck } = useAuth()

  const _fetchGames = async (searchQuery?: string, selectedTags?: number[], page?: number, limit?: number) => {
    loading.value = true
    error.value = null

    try {
      const params = new URLSearchParams()

      if (searchQuery && searchQuery.trim()) {
        params.append('search', searchQuery.trim())
      }

      if (selectedTags && selectedTags.length > 0) {
        params.append('tags', selectedTags.join(','))
      }

      params.append('page', String(page ?? currentPage.value))
      params.append('limit', String(limit ?? itemsPerPage.value))

      const url = `/api/v1/games/?${params.toString()}`

      // Get token from auth state instead of cookie
      const { token } = useAuth()

      // Use native fetch to get headers
      const baseURL = useRuntimeConfig().public.apiBase || ''
      const response = await fetch(`${baseURL}${url}`, {
        headers: {
          'Authorization': `Bearer ${token.value || ''}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json() as GamePublic[]
      const totalCountHeader = response.headers.get('X-Total-Count')

      games.value = data
      totalCount.value = totalCountHeader ? parseInt(totalCountHeader) : data.length
      if (page !== undefined) currentPage.value = page
    } catch (err) {
      error.value = 'Failed to fetch games'
      console.error('Error fetching games:', err)
    } finally {
      loading.value = false
    }
  }

  // SSR-safe version
  const fetchGames = withSSRCheck(_fetchGames)

  const _fetchGamesFromEndpoint = async (endpoint: string, searchQuery?: string, selectedTags?: number[], page?: number, limit?: number) => {
    loading.value = true
    error.value = null

    try {
      const url = new URL(endpoint, window.location.origin)

      if (searchQuery && searchQuery.trim()) {
        url.searchParams.append('search', searchQuery.trim())
      }

      if (selectedTags && selectedTags.length > 0) {
        url.searchParams.append('tags', selectedTags.join(','))
      }

      url.searchParams.append('page', String(page ?? currentPage.value))
      url.searchParams.append('limit', String(limit ?? itemsPerPage.value))

      // Get token from auth state instead of cookie
      const { token } = useAuth()

      // Use native fetch to get headers
      const baseURL = useRuntimeConfig().public.apiBase || ''
      const response = await fetch(`${baseURL}${url.pathname}${url.search}`, {
        headers: {
          'Authorization': `Bearer ${token.value || ''}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json() as GamePublic[]
      const totalCountHeader = response.headers.get('X-Total-Count')

      games.value = data
      totalCount.value = totalCountHeader ? parseInt(totalCountHeader) : data.length
      if (page !== undefined) currentPage.value = page
    } catch (err) {
      error.value = 'Failed to fetch games'
      console.error('Error fetching games:', err)
    } finally {
      loading.value = false
    }
  }

  // SSR-safe version
  const fetchGamesFromEndpoint = withSSRCheck(_fetchGamesFromEndpoint)

  const _fetchGameById = async (id: string | number) => {
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

  // SSR-safe version
  const fetchGameById = withSSRCheck(_fetchGameById)

  const _fetchTags = async () => {
    tagsLoading.value = true
    tagsError.value = null

    try {
      const response = await authenticatedFetch<TagPublic[]>('/api/v1/tags/')
      tags.value = response
    } catch (err) {
      tagsError.value = 'Failed to fetch tags'
      console.error('Error fetching tags:', err)
    } finally {
      tagsLoading.value = false
    }
  }

  // SSR-safe version
  const fetchTags = withSSRCheck(_fetchTags)

  const _updateGame = async (id: string | number, gameData: GameUpdate): Promise<GamePublic> => {
    updateLoading.value = true
    updateError.value = null

    try {
      const response = await authenticatedFetch<GamePublic>(`/api/v1/games/${id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(gameData)
      })

      // Update the local game state if this is the current game
      if (game.value && game.value.id === Number(id)) {
        game.value = response
      }

      return response
    } catch (err) {
      updateError.value = 'Failed to update game'
      console.error('Error updating game:', err)
      throw err
    } finally {
      updateLoading.value = false
    }
  }

  // SSR-safe version
  const updateGame = withSSRCheck(_updateGame)

  const _createGame = async (gameData: GameCreate): Promise<GamePublic> => {
    updateLoading.value = true
    updateError.value = null

    try {
      const response = await authenticatedFetch<GamePublic>('/api/v1/games/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(gameData)
      })

      return response
    } catch (err) {
      updateError.value = 'Failed to create game'
      console.error('Error creating game:', err)
      throw err
    } finally {
      updateLoading.value = false
    }
  }

  // SSR-safe version
  const createGame = withSSRCheck(_createGame)

  // Image management functions
  const _addGameImage = async (gameId: string | number, file: File): Promise<{ status: string; filename: string }> => {
    updateLoading.value = true
    updateError.value = null

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await authenticatedFetch<{ status: string; filename: string }>(`/api/v1/games/${gameId}/images`, {
        method: 'POST',
        body: formData
      })

      return response
    } catch (err) {
      updateError.value = 'Failed to add image'
      console.error('Error adding image:', err)
      throw err
    } finally {
      updateLoading.value = false
    }
  }

  const _replaceGameImage = async (gameId: string | number, position: number, file: File): Promise<{ status: string; filename: string }> => {
    updateLoading.value = true
    updateError.value = null

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await authenticatedFetch<{ status: string; filename: string }>(`/api/v1/games/${gameId}/images/${position}`, {
        method: 'PUT',
        body: formData
      })

      return response
    } catch (err) {
      updateError.value = 'Failed to replace image'
      console.error('Error replacing image:', err)
      throw err
    } finally {
      updateLoading.value = false
    }
  }

  const _deleteGameImage = async (gameId: string | number, position: number): Promise<{ status: string; deleted: boolean }> => {
    updateLoading.value = true
    updateError.value = null

    try {
      const response = await authenticatedFetch<{ status: string; deleted: boolean }>(`/api/v1/games/${gameId}/images/${position}`, {
        method: 'DELETE'
      })

      return response
    } catch (err) {
      updateError.value = 'Failed to delete image'
      console.error('Error deleting image:', err)
      throw err
    } finally {
      updateLoading.value = false
    }
  }

  const _deleteGame = async (gameId: string | number): Promise<void> => {
    updateLoading.value = true
    updateError.value = null

    try {
      await authenticatedFetch(`/api/v1/games/${gameId}`, {
        method: 'DELETE'
      })
    } catch (err) {
      updateError.value = 'Failed to delete game'
      console.error('Error deleting game:', err)
      throw err
    } finally {
      updateLoading.value = false
    }
  }

  const _updateGameStatus = async (gameId: string | number, status: string): Promise<GamePublic> => {
    updateLoading.value = true
    updateError.value = null

    try {
      const response = await authenticatedFetch<GamePublic>(`/api/v1/games/${gameId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status })
      })

      // Update the local game state if this is the current game
      if (game.value && game.value.id === Number(gameId)) {
        game.value = response
      }

      return response
    } catch (err) {
      updateError.value = `Failed to update game status to ${status}`
      console.error('Error updating game status:', err)
      throw err
    } finally {
      updateLoading.value = false
    }
  }

  // SSR-safe versions
  const addGameImage = withSSRCheck(_addGameImage)
  const replaceGameImage = withSSRCheck(_replaceGameImage)
  const deleteGameImage = withSSRCheck(_deleteGameImage)
  const deleteGame = withSSRCheck(_deleteGame)
  const updateGameStatus = withSSRCheck(_updateGameStatus)

  // Computed values for pagination
  const totalPages = computed(() => Math.ceil(totalCount.value / itemsPerPage.value))
  const hasNextPage = computed(() => currentPage.value < totalPages.value - 1)
  const hasPreviousPage = computed(() => currentPage.value > 0)

  // Utility functions for pagination
  const nextPage = () => {
    if (hasNextPage.value) {
      currentPage.value++
    }
  }

  const previousPage = () => {
    if (hasPreviousPage.value) {
      currentPage.value--
    }
  }

  const goToPage = (page: number) => {
    if (page >= 0 && page < totalPages.value) {
      currentPage.value = page
    }
  }

  const clearPagination = () => {
    currentPage.value = 0
    totalCount.value = 0
  }

  return {
    games: readonly(games),
    game: readonly(game),
    tags: readonly(tags),
    totalCount: readonly(totalCount),
    currentPage: readonly(currentPage),
    itemsPerPage: readonly(itemsPerPage),
    totalPages,
    hasNextPage,
    hasPreviousPage,
    loading: readonly(loading),
    gameLoading: readonly(gameLoading),
    tagsLoading: readonly(tagsLoading),
    updateLoading: readonly(updateLoading),
    error: readonly(error),
    gameError: readonly(gameError),
    tagsError: readonly(tagsError),
    updateError: readonly(updateError),
    fetchGames,
    fetchGamesFromEndpoint,
    fetchGameById,
    fetchTags,
    updateGame,
    createGame,
    addGameImage,
    replaceGameImage,
    deleteGameImage,
    deleteGame,
    updateGameStatus,
    nextPage,
    previousPage,
    goToPage,
    clearPagination
  }
} 