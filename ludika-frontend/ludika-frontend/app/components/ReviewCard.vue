<template>
    <div :class="['review-item', { 'my-review-item': isMyReview }]">
        <div class="review-header">
            <VaAvatar :color="getAvatarColor(review.author.visible_name)" size="large" class="review-avatar">
                {{ getInitials(review.author.visible_name) }}
            </VaAvatar>
            <div class="review-author-info">
                <div class="author-name">
                    {{ review.author.visible_name }}
                    <span v-if="isMyReview" class="my-review-badge">(My Review)</span>
                </div>
                <div class="author-role">{{ formatRole(review.author.user_role) }}</div>
                <div class="review-date">{{ formatDate(review.created_at) }}</div>
            </div>
            <NuxtLink v-if="isMyReview" :to="`${gameId}/review`" class="edit-review-button">
                <font-awesome-icon icon="pencil-alt" />
            </NuxtLink>
            <button v-else-if="isPrivileged() && gameId" @click="showDeleteModal = true" class="delete-review-button"
                title="Delete this review">
                <font-awesome-icon icon="trash" />
            </button>
        </div>

        <div class="review-content">
            <p class="review-text">{{ review.review_text }}</p>

            <div v-if="review.ratings && review.ratings.length > 0" class="review-ratings">
                <div v-for="rating in review.ratings" :key="rating.criterion.id" class="rating-item">
                    <div class="rating-criterion">
                        <div class="criterion-name">{{ rating.criterion.name }}</div>
                        <div class="criterion-description">{{ rating.criterion.description }}</div>
                    </div>
                    <div class="rating-stars">
                        <font-awesome-icon v-for="star in 5" :key="star" :icon="'fas fa-star'" :class="{
                            'star-filled': star <= rating.score,
                            'star-empty': star > rating.score
                        }" />
                        <span class="rating-score">({{ rating.score }}/5)</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <ConfirmationModal v-model="showDeleteModal" title="Delete Review"
        :message="`Are you sure you want to delete ${review.author.visible_name}'s review? This action cannot be undone.`"
        confirm-text="Delete" confirm-color="danger" @confirm="handleDeleteReview" @cancel="showDeleteModal = false" />
</template>

<script setup lang="ts">
import type { GameReview } from '../../types/game'
import { useAuth } from '~/composables/useAuth'
import ConfirmationModal from './ConfirmationModal.vue'

interface Props {
    review: GameReview
    isMyReview?: boolean
    gameId?: string | number
}

interface Emits {
    (e: 'deleteReview', userId: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { isPrivileged } = useAuth()
const showDeleteModal = ref(false)

const getInitials = (name: string): string => {
    return name
        .split(' ')
        .map(word => word.charAt(0).toUpperCase())
        .slice(0, 2)
        .join('')
}

const getAvatarColor = (name: string): string => {
    // Generate a consistent color based on the name
    const colors = ['primary', 'secondary', 'success', 'info', 'warning', 'danger'] as const
    const index = name.length % colors.length
    return colors[index]
}

const formatRole = (role: string): string => {
    return role.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    })
}

const handleDeleteReview = () => {
    emit('deleteReview', props.review.reviewer_id as string)
    showDeleteModal.value = false
}
</script>

<style scoped>
.review-item {
    background: white;
    border-radius: 1rem;
    padding: 1.5rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    border: 1px solid #e5e7eb;
    position: relative;
}

.review-header {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 1rem;
}

.review-avatar {
    flex-shrink: 0;
}

.review-author-info {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.author-name {
    font-size: 1.125rem;
    font-weight: 600;
    color: #374151;
}

.author-role {
    font-size: 0.875rem;
    color: #6b7280;
    font-weight: 500;
}

.review-date {
    font-size: 0.75rem;
    color: #9ca3af;
}

.review-content {
    margin-left: 0;
}

.review-text {
    font-size: 1rem;
    color: #4b5563;
    line-height: 1.6;
    margin-bottom: 1rem;
}

.review-ratings {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.rating-item {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 1rem;
    background-color: #f9fafb;
    border-radius: 0.5rem;
    border: 1px solid #e5e7eb;
}

.rating-criterion {
    flex: 1;
    margin-right: 1rem;
}

.criterion-name {
    font-weight: 600;
    color: #374151;
    margin-bottom: 0.25rem;
}

.criterion-description {
    font-size: 0.875rem;
    color: #6b7280;
    line-height: 1.4;
}

.rating-stars {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    flex-shrink: 0;
}

.star-filled {
    color: #fbbf24;
}

.star-empty {
    color: #d1d5db;
}

.rating-score {
    font-size: 0.875rem;
    font-weight: 600;
    color: #6b7280;
    margin-left: 0.5rem;
}

/* My Review Styles */
.my-review-item {
    background: #f0fdf4;
    border: 2px solid #22c55e;
}

.my-review-badge {
    font-size: 0.875rem;
    font-weight: 600;
    color: #16a34a;
}

.edit-review-button,
.delete-review-button {
    position: absolute;
    top: 1rem;
    right: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2.5rem;
    height: 2.5rem;
    border: none;
    border-radius: 0.5rem;
    transition: all 0.2s ease-in-out;
    text-decoration: none;
    cursor: pointer;
    box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
}

.edit-review-button {
    background-color: #22c55e;
    color: white;
}

.delete-review-button {
    background: rgba(239, 68, 68, 0.1);
    color: #dc2626;
    border: 2px solid #dc2626;
}

.edit-review-button:hover {
    background-color: #16a34a;
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.delete-review-button:hover {
    background-color: #dc2626;
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
    .rating-item {
        flex-direction: column;
        gap: 0.75rem;
    }

    .rating-criterion {
        margin-right: 0;
    }

    .rating-stars {
        justify-content: flex-start;
    }
}
</style>