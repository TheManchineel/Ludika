import type { GamePublic, GameUpdate, GameCreate, TagPublic, GameReview, ReviewCriterion } from '../../types/game'
import { useAuth } from './useAuth'

export const useGames = () => {
  const games = ref<GamePublic[]>([])
  const game = ref<GamePublic | null>(null)
  const userReview = ref<GameReview | null>(null)
  const reviewCriteria = ref<ReviewCriterion[]>([])
  const tags = ref<TagPublic[]>([])
  const totalCount = ref(0)
  const supportsServerPagination = ref(false)
  const currentPage = ref(0)
  const itemsPerPage = ref(50)
  const loading = ref(false)
  const gameLoading = ref(false)
  const userReviewLoading = ref(false)
  const reviewCriteriaLoading = ref(false)
  const tagsLoading = ref(false)
  const updateLoading = ref(false)
  const error = ref<string | null>(null)
  const gameError = ref<string | null>(null)
  const userReviewError = ref<string | null>(null)
  const reviewCriteriaError = ref<string | null>(null)
  const tagsError = ref<string | null>(null)
  const updateError = ref<string | null>(null)

  const { authenticatedFetch, withSSRCheck } = useAuth()

  // Note: unified fetching is implemented via _fetchGamesFromEndpoint below.

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

      // Keep itemsPerPage in sync with the passed limit so totalPages computes correctly
      if (typeof limit === 'number' && limit > 0 && itemsPerPage.value !== limit) {
        itemsPerPage.value = limit
      }

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
      // Treat presence of X-Total-Count as indicator of server-side pagination support
      if (totalCountHeader) {
        totalCount.value = parseInt(totalCountHeader)
        supportsServerPagination.value = true
      } else {
        totalCount.value = data.length
        supportsServerPagination.value = false
      }
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

  // Default games fetcher uses the unified endpoint-based implementation
  const fetchGames = withSSRCheck(async (searchQuery?: string, selectedTags?: number[], page?: number, limit?: number) => {
    return _fetchGamesFromEndpoint('/api/v1/games/', searchQuery, selectedTags, page, limit)
  })

  const _fetchGameById = async (id: string | number) => {
    gameLoading.value = true
    gameError.value = null

    try {
      const response = await authenticatedFetch<GamePublic>(`/api/v1/games/${id}/with-reviews`)
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

  const _fetchUserReview = async (gameId: string | number) => {
    userReviewLoading.value = true
    userReviewError.value = null

    try {
      const response = await authenticatedFetch<GameReview>(`/api/v1/reviews/${gameId}/my-review`)
      userReview.value = response
    } catch (err: any) {
      // If it's a 404, that means the user doesn't have a review yet
      if (err.response?.status === 404 || err.status === 404) {
        userReview.value = null
        userReviewError.value = null
      } else {
        userReviewError.value = 'Failed to fetch user review'
        console.error('Error fetching user review:', err)
      }
    } finally {
      userReviewLoading.value = false
    }
  }

  // SSR-safe version
  const fetchUserReview = withSSRCheck(_fetchUserReview)

  const _fetchReviewCriteria = async () => {
    reviewCriteriaLoading.value = true
    reviewCriteriaError.value = null

    try {
      const response = await authenticatedFetch<ReviewCriterion[]>('/api/v1/reviews/criteria')
      reviewCriteria.value = response
    } catch (err) {
      reviewCriteriaError.value = 'Failed to fetch review criteria'
      console.error('Error fetching review criteria:', err)
    } finally {
      reviewCriteriaLoading.value = false
    }
  }

  // SSR-safe version
  const fetchReviewCriteria = withSSRCheck(_fetchReviewCriteria)

  const _submitReview = async (gameId: string | number, reviewData: { review_text: string; ratings: { score: number; criterion_id: number }[] }): Promise<GameReview> => {
    updateLoading.value = true
    updateError.value = null

    try {
      const response = await authenticatedFetch<GameReview>(`/api/v1/reviews/${gameId}/my-review`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(reviewData)
      })

      // Update the local user review state
      userReview.value = response

      return response
    } catch (err) {
      updateError.value = 'Failed to submit review'
      console.error('Error submitting review:', err)
      throw err
    } finally {
      updateLoading.value = false
    }
  }

  // SSR-safe version
  const submitReview = withSSRCheck(_submitReview)

  const _deleteReview = async (gameId: string | number): Promise<void> => {
    updateLoading.value = true
    updateError.value = null

    try {
      await authenticatedFetch(`/api/v1/reviews/${gameId}/my-review`, {
        method: 'DELETE'
      })

      // Clear the local user review state
      userReview.value = null
    } catch (err) {
      updateError.value = 'Failed to delete review'
      console.error('Error deleting review:', err)
      throw err
    } finally {
      updateLoading.value = false
    }
  }

  // SSR-safe version
  const deleteReview = withSSRCheck(_deleteReview)

  const _deleteOtherUserReview = async (gameId: string | number, userId: string): Promise<void> => {
    updateLoading.value = true
    updateError.value = null

    try {
      await authenticatedFetch(`/api/v1/reviews/${gameId}/${userId}`, {
        method: 'DELETE'
      })

      // Reload the game data to refresh reviews
      if (game.value) {
        await _fetchGameById(gameId)
      }
    } catch (err) {
      updateError.value = 'Failed to delete review'
      console.error('Error deleting other user review:', err)
      throw err
    } finally {
      updateLoading.value = false
    }
  }

  // SSR-safe version
  const deleteOtherUserReview = withSSRCheck(_deleteOtherUserReview)

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
    userReview: readonly(userReview),
    reviewCriteria: readonly(reviewCriteria),
    tags: readonly(tags),
    totalCount: readonly(totalCount),
    supportsServerPagination: readonly(supportsServerPagination),
    currentPage: readonly(currentPage),
    itemsPerPage: readonly(itemsPerPage),
    totalPages,
    hasNextPage,
    hasPreviousPage,
    loading: readonly(loading),
    gameLoading: readonly(gameLoading),
    userReviewLoading: readonly(userReviewLoading),
    reviewCriteriaLoading: readonly(reviewCriteriaLoading),
    tagsLoading: readonly(tagsLoading),
    updateLoading: readonly(updateLoading),
    error: readonly(error),
    gameError: readonly(gameError),
    userReviewError: readonly(userReviewError),
    reviewCriteriaError: readonly(reviewCriteriaError),
    tagsError: readonly(tagsError),
    updateError: readonly(updateError),
    fetchGames,
    fetchGamesFromEndpoint,
    fetchGameById,
    fetchUserReview,
    fetchReviewCriteria,
    submitReview,
    deleteReview,
    deleteOtherUserReview,
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