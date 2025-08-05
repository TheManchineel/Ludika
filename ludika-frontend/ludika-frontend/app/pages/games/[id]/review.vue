<template>
    <div class="review-page">
        <div class="review-content">
            <h1 class="review-title">
                {{ isEditing ? 'Edit Review' : 'Review Game' }}
            </h1>

            <!-- Loading State -->
            <div v-if="userReviewLoading || reviewCriteriaLoading" class="loading-state">
                <VaProgressCircle indeterminate color="primary" />
                <div class="loading-text">Loading review data...</div>
            </div>

            <!-- Error State -->
            <div v-else-if="userReviewError || reviewCriteriaError" class="error-state">
                <div class="error-text">Failed to load review data. Please try again.</div>
            </div>

            <!-- Review Form -->
            <form v-else @submit.prevent="handleSubmit" class="review-form">
                <!-- Review Text Section -->
                <div class="form-section">
                    <label for="reviewText" class="form-label">
                        <font-awesome-icon icon="comment" class="label-icon" />
                        Your Review
                    </label>
                    <textarea id="reviewText" v-model="reviewText" placeholder="Share your thoughts about this game..."
                        class="review-textarea" rows="6" required></textarea>
                </div>

                <!-- Ratings Section -->
                <div class="form-section">
                    <div class="section-header">
                        <div class="section-label">
                            <font-awesome-icon icon="star" class="label-icon" />
                            Rating Criteria
                        </div>
                        <div class="section-subtitle">Rate different aspects of the game</div>
                    </div>

                    <div class="ratings-grid">
                        <!-- Existing Rating Cards -->
                        <RatingCriteriaCard v-for="rating in selectedRatings" :key="rating.criterion.id"
                            :criterion="rating.criterion" v-model="rating.score"
                            @remove="removeCriterion(rating.criterion.id)" />

                        <!-- Add Rating Card -->
                        <AddRatingCard :available-criteria="availableCriteria" @select="addCriterion" />
                    </div>
                </div>

                <!-- Action Buttons -->
                <div class="form-actions">
                    <div class="left-actions">
                        <VaButton v-if="isEditing" preset="plain" color="danger" @click="showDeleteModal = true"
                            :disabled="updateLoading">
                            <font-awesome-icon icon="trash" class="action-icon" />
                            Delete Review
                        </VaButton>
                    </div>
                    <div class="right-actions">
                        <VaButton preset="secondary" @click="$router.push(`/games/${gameId}`)"
                            :disabled="updateLoading">
                            Cancel
                        </VaButton>
                        <VaButton type="submit" :loading="updateLoading" :disabled="!reviewText.trim()">
                            {{ isEditing ? 'Update Review' : 'Submit Review' }}
                        </VaButton>
                    </div>
                </div>
            </form>

            <!-- Delete Confirmation Modal -->
            <ConfirmationModal v-model="showDeleteModal" title="Delete Review"
                message="Are you sure you want to delete this review? This action cannot be undone."
                confirm-text="Delete" confirm-color="danger" :loading="updateLoading" @confirm="handleDeleteReview"
                @cancel="showDeleteModal = false" />
        </div>
    </div>
</template>

<script setup lang="ts">
import type { ReviewCriterion } from '../../../types/game'
import { useGames } from '~/composables/useGames'
import RatingCriteriaCard from '~/components/RatingCriteriaCard.vue'
import AddRatingCard from '~/components/AddRatingCard.vue'
import ConfirmationModal from '~/components/ConfirmationModal.vue'

// Get the game ID from the route
const route = useRoute()
const router = useRouter()
const gameId = route.params.id as string

// Set up page metadata
useHead({
    title: `Review Game ${gameId} - Ludika`
})

const {
    userReview,
    userReviewLoading,
    userReviewError,
    reviewCriteria,
    reviewCriteriaLoading,
    reviewCriteriaError,
    updateLoading,
    updateError,
    fetchUserReview,
    fetchReviewCriteria,
    submitReview,
    deleteReview
} = useGames()

// Form state
const reviewText = ref('')
const selectedRatings = ref<{ criterion: ReviewCriterion; score: number }[]>([])
const showDeleteModal = ref(false)

// Computed properties
const isEditing = computed(() => !!userReview.value)

const availableCriteria = computed(() => {
    const usedCriteriaIds = selectedRatings.value.map(r => r.criterion.id)
    return reviewCriteria.value.filter(criterion => !usedCriteriaIds.includes(criterion.id))
})

// Methods
const addCriterion = (criterion: ReviewCriterion) => {
    selectedRatings.value.push({
        criterion,
        score: 5 // Default to 5 stars
    })
}

const removeCriterion = (criterionId: number) => {
    const index = selectedRatings.value.findIndex(r => r.criterion.id === criterionId)
    if (index !== -1) {
        selectedRatings.value.splice(index, 1)
    }
}

const populateForm = () => {
    if (userReview.value) {
        reviewText.value = userReview.value.review_text

        // Populate ratings
        selectedRatings.value = userReview.value.ratings.map(rating => ({
            criterion: rating.criterion,
            score: rating.score
        }))
    }
}

const handleSubmit = async () => {
    try {
        const reviewData = {
            review_text: reviewText.value.trim(),
            ratings: selectedRatings.value.map(rating => ({
                score: rating.score,
                criterion_id: rating.criterion.id
            }))
        }

        await submitReview(gameId, reviewData)

        // Navigate back to game page
        router.push(`/games/${gameId}`)
    } catch (error) {
        console.error('Failed to submit review:', error)
    }
}

const handleDeleteReview = async () => {
    try {
        await deleteReview(gameId)
        showDeleteModal.value = false

        // Navigate back to game page
        router.push(`/games/${gameId}`)
    } catch (error) {
        console.error('Failed to delete review:', error)
        showDeleteModal.value = false
    }
}

// Initialize data
onMounted(async () => {
    // Fetch review criteria and user's existing review
    await Promise.all([
        fetchReviewCriteria(),
        fetchUserReview(gameId)
    ])

    // Populate form if editing existing review
    populateForm()
})

// Watch for changes in userReview to handle async loading
watch(userReview, () => {
    populateForm()
}, { immediate: true })
</script>

<style scoped>
.review-page {
    padding: 2rem;
    max-width: 1000px;
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

.loading-state,
.error-state {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 300px;
    gap: 1rem;
}

.loading-text,
.error-text {
    font-size: 1.125rem;
    color: #6b7280;
}

.review-form {
    max-width: 800px;
    margin: 0 auto;
}

.form-section {
    margin-bottom: 2rem;
}

.form-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.125rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 0.75rem;
}

.label-icon {
    color: #10b981;
}

.review-textarea {
    width: 100%;
    padding: 1rem;
    border: 2px solid #e5e7eb;
    border-radius: 0.5rem;
    font-size: 1rem;
    line-height: 1.6;
    resize: vertical;
    transition: border-color 0.2s ease-in-out;
}

.review-textarea:focus {
    outline: none;
    border-color: #10b981;
}

.section-header {
    margin-bottom: 1.5rem;
}

.section-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.125rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 0.25rem;
}

.section-subtitle {
    font-size: 0.875rem;
    color: #6b7280;
}

.ratings-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
}

.form-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 2rem;
    border-top: 1px solid #e5e7eb;
}

.left-actions {
    display: flex;
}

.right-actions {
    display: flex;
    gap: 1rem;
}

.action-icon {
    margin-right: 0.5rem;
}

@media (max-width: 768px) {
    .review-page {
        padding: 1rem;
    }

    .review-title {
        font-size: 2rem;
    }

    .ratings-grid {
        grid-template-columns: 1fr;
    }

    .form-actions {
        flex-direction: column;
        gap: 1rem;
    }

    .right-actions {
        flex-direction: column-reverse;
        width: 100%;
    }

    .left-actions {
        order: 2;
    }

    .right-actions {
        order: 1;
    }
}
</style>