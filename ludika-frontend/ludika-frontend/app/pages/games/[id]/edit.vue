<template>
    <div class="edit-game-page">
        <div class="edit-game-content">
            <!-- Loading state -->
            <div v-if="gameLoading" class="loading-state">
                <VaProgressCircle indeterminate />
                <p>Loading game data...</p>
            </div>

            <!-- Error state -->
            <div v-else-if="gameError" class="error-state">
                <VaAlert color="danger" class="error-alert">
                    {{ gameError }}
                </VaAlert>
                <div class="back-button-section">
                    <VaButton preset="secondary" @click="navigateTo(`/games/${gameId}`)">
                        <VaIcon name="arrow_back" class="back-icon" />
                        Back to Game
                    </VaButton>
                </div>
            </div>

            <!-- Game form -->
            <GameFormEditor v-else-if="game" :game-data="game" :is-editing="true" @success="handleSuccess"
                @cancel="handleCancel" />
        </div>
    </div>
</template>

<script setup lang="ts">
import type { GamePublic } from '~~/types/game'
import { useAuth } from '~/composables/useAuth'
import { useGames } from '~/composables/useGames'
import GameFormEditor from '~/components/GameFormEditor.vue'

// Get the game ID from the route
const route = useRoute()
const gameId = route.params.id as string

// Set up auth and game data
const { canEditGame, isAuthenticated } = useAuth()
const { game, gameLoading, gameError, fetchGameById } = useGames()

// Set up page metadata
useHead({
    title: `Edit Game ${gameId} - Ludika`
})

// Form event handlers
const handleSuccess = (updatedGame: GamePublic) => {
    // Navigate to the game's view page using the returned game ID
    // This handles both edit (same ID) and create (new ID) scenarios
    navigateTo(`/games/${updatedGame.id}`)
}

const handleCancel = () => {
    // Navigate back to the game's view page
    navigateTo(`/games/${gameId}`)
}

// Fetch the game data to check permissions
onMounted(async () => {
    if (gameId) {
        await fetchGameById(gameId)

        // Check if user can edit this game
        if (game.value && !canEditGame(game.value)) {
            throw createError({
                statusCode: 403,
                statusMessage: 'You do not have permission to edit this game.'
            })
        }
    }
})

// Redirect if not authenticated
watch(isAuthenticated, (authenticated) => {
    if (!authenticated && !gameLoading.value) {
        navigateTo('/login')
    }
})
</script>

<style scoped>
.edit-game-page {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
    min-height: calc(100vh - 4rem);
}

.edit-game-content {
    padding: 0 1rem;
}

.loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 2rem;
    text-align: center;
    gap: 1rem;
}

.loading-state p {
    color: #6b7280;
    font-size: 1.125rem;
}

.error-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2rem;
    padding: 2rem;
}

.error-alert {
    max-width: 500px;
    width: 100%;
}

.back-button-section {
    display: flex;
    justify-content: center;
}

.back-icon {
    margin-right: 0.5rem;
}

@media (max-width: 768px) {
    .edit-game-page {
        padding: 1rem;
    }

    .edit-game-content {
        padding: 0;
    }
}
</style>