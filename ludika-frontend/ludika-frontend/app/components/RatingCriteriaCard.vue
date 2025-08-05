<template>
    <div class="criteria-card">
        <div class="criteria-header">
            <div class="criteria-info">
                <h3 class="criteria-name">{{ criterion.name }}</h3>
                <p class="criteria-description">{{ criterion.description }}</p>
            </div>
            <button @click="$emit('remove')" class="remove-button" type="button">
                <font-awesome-icon icon="times" />
            </button>
        </div>

        <div class="rating-section">
            <div class="rating-label">Your Rating:</div>
            <div class="star-rating">
                <button v-for="star in 5" :key="star" @click="updateRating(star)"
                    :class="['star-button', { 'active': star <= modelValue }]" type="button">
                    <font-awesome-icon :icon="'fas fa-star'" />
                </button>
                <span class="rating-text">{{ modelValue }}/5</span>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { ReviewCriterion } from '../../types/game'

interface Props {
    criterion: ReviewCriterion
    modelValue: number
}

interface Emits {
    (e: 'update:modelValue', value: number): void
    (e: 'remove'): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

const updateRating = (rating: number) => {
    emit('update:modelValue', rating)
}
</script>

<style scoped>
.criteria-card {
    background: white;
    border: 2px solid #e5e7eb;
    border-radius: 0.75rem;
    padding: 1.5rem;
    transition: all 0.2s ease-in-out;
    position: relative;
}

.criteria-card:hover {
    border-color: #d1d5db;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.criteria-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.criteria-info {
    flex: 1;
    margin-right: 1rem;
}

.criteria-name {
    font-size: 1.125rem;
    font-weight: 600;
    color: #374151;
    margin: 0 0 0.5rem 0;
}

.criteria-description {
    font-size: 0.875rem;
    color: #6b7280;
    line-height: 1.4;
    margin: 0;
}

.remove-button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    background-color: #ef4444;
    color: white;
    border: none;
    border-radius: 0.375rem;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
    flex-shrink: 0;
}

.remove-button:hover {
    background-color: #dc2626;
    transform: scale(1.05);
}

.rating-section {
    padding-top: 1rem;
    border-top: 1px solid #e5e7eb;
}

.rating-label {
    font-size: 0.875rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 0.75rem;
}

.star-rating {
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.star-button {
    background: none;
    border: none;
    padding: 0.25rem;
    cursor: pointer;
    color: #d1d5db;
    transition: all 0.2s ease-in-out;
    font-size: 1.25rem;
}

.star-button:hover {
    transform: scale(1.1);
}

.star-button.active {
    color: #fbbf24;
}

.rating-text {
    margin-left: 0.5rem;
    font-size: 0.875rem;
    font-weight: 600;
    color: #6b7280;
}

@media (max-width: 768px) {
    .criteria-header {
        flex-direction: column;
        gap: 1rem;
    }

    .criteria-info {
        margin-right: 0;
    }

    .remove-button {
        align-self: flex-end;
    }
}
</style>