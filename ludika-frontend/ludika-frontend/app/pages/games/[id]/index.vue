<template>
    <div class="game-page">
        <!-- Loading State -->
        <div v-if="gameLoading" class="loading-state">
            <VaProgressCircle indeterminate color="primary" />
            <div class="loading-text">Loading game details...</div>
        </div>

        <div v-else-if="gameError" class="error-state">
            <div class="error-text">{{ gameError }}</div>
        </div>

        <div v-else-if="game" class="game-content">
            <div class="title-section">
                <h1 class="game-title">
                    {{ game.name }}
                </h1>
                <div class="title-actions">
                    <GameStatusBadge :status="game.status" />
                    <NuxtLink v-if="canEditGame(game)" :to="`/games/${game.id}/edit`" class="edit-button">
                        <svg class="edit-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                            xmlns="http://www.w3.org/2000/svg">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z">
                            </path>
                        </svg>
                    </NuxtLink>
                </div>
            </div>

            <div class="action-buttons-section">
                <a v-if="game.url" :href="game.url" target="_blank" rel="noopener noreferrer" class="visit-button">
                    <svg class="visit-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                        xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                    </svg>
                    Visit Game
                </a>
                <NuxtLink :to="`${game.id}/review`" class="review-button">
                    <svg class="review-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                        xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z">
                        </path>
                    </svg>
                    Review Game
                </NuxtLink>

                <!-- Status Action Buttons -->
                <button v-if="canSubmitGame" @click="showSubmitModal = true" class="submit-button">
                    <font-awesome-icon icon="paper-plane" class="action-icon" />
                    Submit Game
                </button>

                <button v-if="canApproveGame" @click="showApproveModal = true" class="approve-button">
                    <font-awesome-icon icon="check-circle" class="action-icon" />
                    Approve Game
                </button>

                <button v-if="canRejectGame" @click="showRejectModal = true" class="reject-button">
                    <font-awesome-icon icon="times-circle" class="action-icon" />
                    Reject Game
                </button>
            </div>

            <div class="game-description">
                {{ game.description }}
            </div>

            <div v-if="game.tags && game.tags.length > 0" class="game-tags-section">
                <GameTags :tags="game.tags" size="medium" class="game-detail-tags" />
            </div>

            <div v-if="game.images && game.images.length > 0" class="images-section">
                <h2 class="images-title">Images</h2>
                <VaCarousel v-model="currentSlide" :items="sortedImages" class="game-carousel" height="400px"
                    autoscroll>
                    <template #default="{ item }">
                        <div class="carousel-slide">
                            <img :src="`/static/${item.image}`" :alt="`${game.name} screenshot ${item.position}`"
                                class="carousel-image" />
                        </div>
                    </template>
                </VaCarousel>
            </div>

            <div v-else class="no-images">
                <div class="no-images-content">
                    <p>No images available for this game</p>
                </div>
            </div>
        </div>

        <div v-else-if="!gameLoading && !game && isClient" class="not-found-state">
            <div class="not-found-text">Game not found</div>
        </div>

        <!-- Confirmation Modals -->
        <ConfirmationModal v-model="showSubmitModal" title="Submit Game for Review"
            message="Are you sure you want to submit this game for review?"
            warning-message="Once submitted, you won't be able to make further changes to the game."
            confirm-text="Submit" confirm-color="primary" :loading="updateLoading" @confirm="handleSubmitGame"
            @cancel="showSubmitModal = false" />

        <ConfirmationModal v-model="showApproveModal" title="Approve Game"
            message="Are you sure you want to approve this game? It will be published and visible to all users."
            confirm-text="Approve" confirm-color="success" :loading="updateLoading" @confirm="handleApproveGame"
            @cancel="showApproveModal = false" />

        <ConfirmationModal v-model="showRejectModal" title="Reject Game"
            message="Are you sure you want to reject this game? The submitter will be notified." confirm-text="Reject"
            confirm-color="danger" :loading="updateLoading" @confirm="handleRejectGame"
            @cancel="showRejectModal = false" />
    </div>
</template>

<script setup lang="ts">
import { useGames } from '~/composables/useGames'
import { useAuth } from '~/composables/useAuth'
import ConfirmationModal from '~/components/ConfirmationModal.vue'
import GameStatusBadge from '~/components/GameStatusBadge.vue'

// Get the game ID from the route
const route = useRoute()
const gameId = route.params.id as string

// Set up page metadata
useHead({
    title: 'Game Details - Ludika'
})

const { game, gameLoading, gameError, updateLoading, fetchGameById, updateGameStatus } = useGames()
const { canEditGame, isPrivileged, user } = useAuth()

const currentSlide = ref(0)
const isClient = computed(() => import.meta.client)

// Modal states
const showSubmitModal = ref(false)
const showApproveModal = ref(false)
const showRejectModal = ref(false)

const sortedImages = computed(() => {
    if (!game.value?.images) return []
    return [...game.value.images].sort((a, b) => a.position - b.position)
})

// Computed properties for button visibility
const canSubmitGame = computed(() => {
    return game.value?.status === 'draft' &&
        user.value?.uuid === game.value?.proposing_user
})

const canApproveGame = computed(() => {
    return isPrivileged() &&
        game.value &&
        (game.value.status === 'draft' || game.value.status === 'submitted')
})

const canRejectGame = computed(() => {
    return isPrivileged() &&
        game.value &&
        (game.value.status === 'draft' || game.value.status === 'submitted')
})

// Status update handlers
const handleSubmitGame = async () => {
    if (!game.value?.id) return

    try {
        await updateGameStatus(game.value.id, 'submitted')
        showSubmitModal.value = false
        // Refresh the page to show updated status
        await refreshPage()
    } catch (error) {
        console.error('Failed to submit game:', error)
        showSubmitModal.value = false
    }
}

const handleApproveGame = async () => {
    if (!game.value?.id) return

    try {
        await updateGameStatus(game.value.id, 'approved')
        showApproveModal.value = false
        await refreshPage()
    } catch (error) {
        console.error('Failed to approve game:', error)
        showApproveModal.value = false
    }
}

const handleRejectGame = async () => {
    if (!game.value?.id) return

    try {
        await updateGameStatus(game.value.id, 'rejected')
        showRejectModal.value = false
        await refreshPage()
    } catch (error) {
        console.error('Failed to reject game:', error)
        showRejectModal.value = false
    }
}

const refreshPage = async () => {
    if (gameId) {
        await fetchGameById(gameId)
    }
}

onMounted(() => {
    if (gameId) {
        fetchGameById(gameId)
    }
})

watch(() => route.params.id, (newId) => {
    if (newId) {
        fetchGameById(newId as string)
    }
})

watch(game, (newGame) => {
    if (newGame) {
        useHead({
            title: `${newGame.name} - Ludika`
        })
    }
})
</script>

<style scoped>
.game-page {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

.loading-state {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 400px;
    gap: 1rem;
}

.error-state,
.not-found-state {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 400px;
}

.loading-text,
.error-text,
.not-found-text {
    font-size: 1.125rem;
    padding: 0.75rem 1.5rem;
    color: #6b7280;
}

.game-content {
    padding: 0 1rem;
}

.title-section {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
}

.game-title {
    font-size: 3rem;
    font-weight: 700;
    color: #374151;
    margin: 0;
    text-align: center;
}

.title-actions {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.edit-button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 3rem;
    height: 3rem;
    background-color: #f59e0b;
    color: white;
    text-decoration: none;
    border-radius: 0.5rem;
    transition: all 0.2s ease-in-out;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.edit-button:hover {
    background-color: #d97706;
    transform: translateY(-1px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.edit-icon {
    width: 1.5rem;
    height: 1.5rem;
}

.action-buttons-section {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}

.visit-button {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    background-color: #3b82f6;
    color: white;
    text-decoration: none;
    border-radius: 0.5rem;
    font-weight: 600;
    transition: all 0.2s ease-in-out;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.visit-button:hover {
    background-color: #2563eb;
    transform: translateY(-1px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.visit-icon {
    width: 1.25rem;
    height: 1.25rem;
}

.review-button {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    background-color: #10b981;
    color: white;
    text-decoration: none;
    border-radius: 0.5rem;
    font-weight: 600;
    transition: all 0.2s ease-in-out;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.review-button:hover {
    background-color: #059669;
    transform: translateY(-1px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.review-icon {
    width: 1.25rem;
    height: 1.25rem;
}

/* Status Action Buttons */
.submit-button,
.approve-button,
.reject-button {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    color: white;
    text-decoration: none;
    border: none;
    border-radius: 0.5rem;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.submit-button {
    background-color: #3b82f6;
}

.submit-button:hover {
    background-color: #2563eb;
    transform: translateY(-1px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.approve-button {
    background-color: #10b981;
}

.approve-button:hover {
    background-color: #059669;
    transform: translateY(-1px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.reject-button {
    background-color: #ef4444;
}

.reject-button:hover {
    background-color: #dc2626;
    transform: translateY(-1px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.action-icon {
    width: 1.25rem;
    height: 1.25rem;
}

.game-description {
    font-size: 1.125rem;
    color: #6b7280;
    margin-bottom: 2rem;
    text-align: center;
    max-width: 600px;
    margin: 0 auto 2rem;
}

.game-tags-section {
    margin-bottom: 2rem;
}

.game-detail-tags {
    justify-content: center;
}

.images-section {
    margin-bottom: 2rem;
}

.images-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 1rem;
}

.game-carousel {
    border-radius: 0.5rem;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.carousel-slide {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 400px;
    background-color: #f3f4f6;
}

.carousel-image {
    max-height: 100%;
    max-width: 100%;
    object-fit: contain;
    border-radius: 0.5rem;
}

.no-images {
    text-align: center;
    color: #9ca3af;
    margin-bottom: 2rem;
}

.no-images-content {
    padding: 3rem;
    background-color: #f3f4f6;
    border-radius: 0.5rem;
}
</style>