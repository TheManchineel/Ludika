<template>
    <div class="add-rating-card">
        <div v-if="!showDropdown" class="add-rating-placeholder" @click.stop="openDropdown">
            <div class="placeholder-content">
                <font-awesome-icon icon="plus" class="plus-icon" />
                <span class="placeholder-text">Add Rating Criterion</span>
            </div>
        </div>

        <div v-else class="dropdown-content">
            <div class="dropdown-header">
                <h3 class="dropdown-title">Select a Criterion</h3>
                <button @click="showDropdown = false" class="close-button" type="button">
                    <font-awesome-icon icon="times" />
                </button>
            </div>

            <div class="criteria-list">
                <button v-for="criterion in availableCriteria" :key="criterion.id" @click="selectCriterion(criterion)"
                    class="criterion-option" type="button">
                    <div class="criterion-info">
                        <div class="criterion-name">{{ criterion.name }}</div>
                        <div class="criterion-description">{{ criterion.description }}</div>
                    </div>
                </button>

                <div v-if="availableCriteria.length === 0" class="no-criteria">
                    <font-awesome-icon icon="check-circle" class="check-icon" />
                    <span>All criteria have been added</span>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { ReviewCriterion } from '../../types/game'

interface Props {
    availableCriteria: ReviewCriterion[]
}

interface Emits {
    (e: 'select', criterion: ReviewCriterion): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

const showDropdown = ref(false)

const openDropdown = () => {
    showDropdown.value = true
}

const selectCriterion = (criterion: ReviewCriterion) => {
    emit('select', criterion)
    showDropdown.value = false
}

// Close dropdown when clicking outside
const handleClickOutside = (event: Event) => {
    if (!showDropdown.value) return
    const target = event.target as Element
    if (!target.closest('.add-rating-card')) {
        showDropdown.value = false
    }
}

onMounted(() => {
    document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.add-rating-card {
    position: relative;
}

.add-rating-placeholder {
    background: #f9fafb;
    border: 2px dashed #d1d5db;
    border-radius: 0.75rem;
    padding: 2rem;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
    text-align: center;
}

.add-rating-placeholder:hover {
    border-color: #10b981;
    background: #f0fdf4;
}

.placeholder-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
}

.plus-icon {
    font-size: 2rem;
    color: #10b981;
}

.placeholder-text {
    font-size: 1.125rem;
    font-weight: 600;
    color: #374151;
}

.dropdown-content {
    background: white;
    border: 2px solid #e5e7eb;
    border-radius: 0.75rem;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    z-index: 10;
    max-height: 400px;
    overflow: hidden;
}

.dropdown-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #e5e7eb;
    background: #f9fafb;
}

.dropdown-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: #374151;
    margin: 0;
}

.close-button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    background-color: #6b7280;
    color: white;
    border: none;
    border-radius: 0.375rem;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
}

.close-button:hover {
    background-color: #4b5563;
}

.criteria-list {
    max-height: 300px;
    overflow-y: auto;
    padding: 0.5rem;
}

.criterion-option {
    width: 100%;
    padding: 1rem;
    background: none;
    border: none;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
    text-align: left;
}

.criterion-option:hover {
    background: #f3f4f6;
}

.criterion-info {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.criterion-name {
    font-size: 1rem;
    font-weight: 600;
    color: #374151;
}

.criterion-description {
    font-size: 0.875rem;
    color: #6b7280;
    line-height: 1.4;
}

.no-criteria {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
    padding: 2rem;
    color: #6b7280;
    text-align: center;
}

.check-icon {
    font-size: 2rem;
    color: #10b981;
}

@media (max-width: 768px) {
    .dropdown-content {
        position: fixed;
        top: 50%;
        left: 1rem;
        right: 1rem;
        transform: translateY(-50%);
        max-height: 80vh;
    }
}
</style>