<template>
    <div class="game-page">
        <!-- Loading State -->
        <div v-if="gameLoading" class="loading-state">
            <div class="loading-text">Loading game details...</div>
        </div>

        <div v-else-if="gameError" class="error-state">
            <div class="error-text">{{ gameError }}</div>
        </div>

        <div v-else-if="game" class="game-content">
            <h1 class="game-title">
                {{ game.name }}
            </h1>

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

        <div v-else class="not-found-state">
            <div class="not-found-text">Game not found</div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useGames } from '~/composables/useGames'

// Get the game ID from the route
const route = useRoute()
const gameId = route.params.id as string

// Set up page metadata
useHead({
    title: 'Game Details - Ludika'
})

const { game, gameLoading, gameError, fetchGameById } = useGames()

const currentSlide = ref(0)

const sortedImages = computed(() => {
    if (!game.value?.images) return []
    return [...game.value.images].sort((a, b) => a.position - b.position)
})

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
    /* Equivalent to py-8 */
    max-width: 1200px;
    /* Equivalent to max-w-4xl */
    margin: 0 auto;
    /* Equivalent to mx-auto */
}

.loading-state,
.error-state,
.not-found-state {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 400px;
    /* Equivalent to min-h-[400px] */
}

.loading-text,
.error-text,
.not-found-text {
    font-size: 1.125rem;
    /* Equivalent to text-lg */
    padding: 0.75rem 1.5rem;
    /* Equivalent to px-4 */
    color: #6b7280;
    /* Equivalent to text-gray-500 */
}

.game-content {
    padding: 0 1rem;
    /* Equivalent to px-4 */
}

.game-title {
    font-size: 3rem;
    /* Equivalent to text-4xl */
    font-weight: 700;
    /* Equivalent to font-bold */
    color: #374151;
    /* Equivalent to text-gray-800 */
    margin-bottom: 1rem;
    /* Equivalent to mb-4 */
    text-align: center;
    /* Equivalent to text-center */
}

.game-description {
    font-size: 1.125rem;
    /* Equivalent to text-lg */
    color: #6b7280;
    /* Equivalent to text-gray-600 */
    margin-bottom: 2rem;
    /* Equivalent to mb-8 */
    text-align: center;
    /* Equivalent to text-center */
    max-width: 600px;
    /* Equivalent to max-w-2xl */
    margin: 0 auto 2rem;
    /* Equivalent to mx-auto mb-8 */
}

.game-tags-section {
    margin-bottom: 2rem;
    /* Equivalent to mb-8 */
}

.game-detail-tags {
    justify-content: center;
    /* Equivalent to justify-center */
}

.images-section {
    margin-bottom: 2rem;
    /* Equivalent to mb-8 */
}

.images-title {
    font-size: 1.5rem;
    /* Equivalent to text-2xl */
    font-weight: 600;
    /* Equivalent to font-semibold */
    color: #374151;
    /* Equivalent to text-gray-800 */
    margin-bottom: 1rem;
    /* Equivalent to mb-4 */
}

.game-carousel {
    border-radius: 0.5rem;
    /* Equivalent to rounded-lg */
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    /* Equivalent to shadow-lg */
}

.carousel-slide {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 400px;
    /* Equivalent to height="400px" */
    background-color: #f3f4f6;
    /* Equivalent to bg-gray-100 */
}

.carousel-image {
    max-height: 100%;
    /* Equivalent to max-h-full */
    max-width: 100%;
    /* Equivalent to max-w-full */
    object-fit: contain;
    /* Equivalent to object-contain */
    border-radius: 0.5rem;
    /* Equivalent to rounded-lg */
}

.no-images {
    text-align: center;
    /* Equivalent to text-center */
    color: #9ca3af;
    /* Equivalent to text-gray-500 */
    margin-bottom: 2rem;
    /* Equivalent to mb-8 */
}

.no-images-content {
    padding: 3rem;
    /* Equivalent to p-12 */
    background-color: #f3f4f6;
    /* Equivalent to bg-gray-100 */
    border-radius: 0.5rem;
    /* Equivalent to rounded-lg */
}
</style>