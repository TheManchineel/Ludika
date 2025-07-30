<template>
    <div class="edit-game-page">
        <div class="edit-game-content">
            <h1 class="edit-title">
                Edit Game
            </h1>

            <div class="placeholder-message">
                <div class="placeholder-content">
                    <svg class="placeholder-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                        xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z">
                        </path>
                    </svg>
                    <h2>Game Editor Coming Soon</h2>
                    <p>This page will allow you to edit game details, add images, and manage tags.</p>
                    <p class="game-id">Game ID: {{ gameId }}</p>

                    <div class="back-button-section">
                        <NuxtLink :to="`/games/${gameId}`" class="back-button">
                            <svg class="back-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                                xmlns="http://www.w3.org/2000/svg">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
                            </svg>
                            Back to Game
                        </NuxtLink>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'
import { useGames } from '~/composables/useGames'

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
    max-width: 1000px;
    margin: 0 auto;
}

.edit-game-content {
    padding: 0 1rem;
}

.edit-title {
    font-size: 3rem;
    font-weight: 700;
    color: #374151;
    margin-bottom: 2rem;
    text-align: center;
}

.placeholder-message {
    text-align: center;
    color: #6b7280;
    margin-bottom: 2rem;
}

.placeholder-content {
    padding: 3rem;
    background-color: #fef3c7;
    border-radius: 1rem;
    border: 2px dashed #f59e0b;
}

.placeholder-icon {
    width: 4rem;
    height: 4rem;
    margin: 0 auto 1.5rem;
    color: #f59e0b;
}

.placeholder-content h2 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 1rem;
}

.placeholder-content p {
    font-size: 1.125rem;
    margin-bottom: 0.5rem;
}

.game-id {
    font-family: monospace;
    background-color: #f3f4f6;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    display: inline-block;
    margin-top: 1rem !important;
    color: #374151 !important;
}

.back-button-section {
    margin-top: 2rem;
}

.back-button {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    background-color: #6b7280;
    color: white;
    text-decoration: none;
    border-radius: 0.5rem;
    font-weight: 600;
    transition: all 0.2s ease-in-out;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.back-button:hover {
    background-color: #4b5563;
    transform: translateY(-1px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.back-icon {
    width: 1.25rem;
    height: 1.25rem;
}
</style>