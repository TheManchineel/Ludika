<template>
    <div v-if="userReview || (reviews && reviews.length > 0)" class="reviews-section">
        <h2 class="reviews-title">Reviews</h2>
        <div class="reviews-list">
            <!-- My Review Card -->
            <ReviewCard v-if="userReview" :review="userReview" :is-my-review="true" :game-id="props.gameId" />

            <!-- Other Reviews -->
            <ReviewCard v-for="review in reviews" :key="`${review.reviewer_id}-${review.created_at}`" :review="review"
                :is-my-review="false" :game-id="props.gameId" @delete-review="handleDeleteOtherReview" />
        </div>
    </div>

    <div v-else class="no-reviews">
        <div class="no-reviews-content">
            <font-awesome-icon icon="comments" class="no-reviews-icon" />
            <p>No reviews yet for this game</p>
            <p class="no-reviews-subtitle">Be the first to share your thoughts!</p>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { GameReview } from '../../types/game'
import ReviewCard from './ReviewCard.vue'
import { useGames } from '~/composables/useGames'

interface Props {
    reviews: readonly GameReview[] | undefined
    userReview: GameReview | null | undefined
    gameId: string | number
}

interface Emits {
    (e: 'refresh'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { deleteOtherUserReview } = useGames()

const handleDeleteOtherReview = async (userId: string) => {
    try {
        await deleteOtherUserReview(props.gameId, userId)
        emit('refresh')
    } catch (error) {
        console.error('Failed to delete review:', error)
    }
}
</script>

<style scoped>
.reviews-section {
    margin-top: 3rem;
}

.reviews-title {
    font-size: 1.875rem;
    font-weight: 700;
    color: #374151;
    margin-bottom: 1.5rem;
    text-align: center;
}

.reviews-list {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.no-reviews {
    margin-top: 3rem;
    text-align: center;
}

.no-reviews-content {
    padding: 3rem;
    background-color: #f9fafb;
    border-radius: 1rem;
    border: 2px dashed #d1d5db;
}

.no-reviews-icon {
    font-size: 3rem;
    color: #9ca3af;
    margin-bottom: 1rem;
}

.no-reviews-content p {
    color: #6b7280;
    font-size: 1.125rem;
    margin-bottom: 0.5rem;
}

.no-reviews-subtitle {
    font-size: 0.875rem !important;
    color: #9ca3af !important;
}
</style>