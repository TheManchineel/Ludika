<template>
    <div class="review-page">
        <div class="review-content">
            <h1 class="review-title">
                Review Game
            </h1>

            <div class="placeholder-message">
                <div class="placeholder-content">
                    <svg class="placeholder-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                        xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z">
                        </path>
                    </svg>
                    <h2>Review Feature Coming Soon</h2>
                    <p>This page will allow you to review and rate games.</p>
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
// Get the game ID from the route
const route = useRoute()
const gameId = route.params.id as string

// Set up page metadata
useHead({
    title: `Review Game ${gameId} - Ludika`
})
</script>

<style scoped>
.review-page {
    padding: 2rem;
    max-width: 800px;
    margin: 0 auto;
}

.review-content {
    padding: 0 1rem;
}

.review-title {
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
    background-color: #f9fafb;
    border-radius: 1rem;
    border: 2px dashed #d1d5db;
}

.placeholder-icon {
    width: 4rem;
    height: 4rem;
    margin: 0 auto 1.5rem;
    color: #10b981;
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
    background-color: #e5e7eb;
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