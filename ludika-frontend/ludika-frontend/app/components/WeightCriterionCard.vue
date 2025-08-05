<template>
    <div class="weight-card">
        <div class="weight-header">
            <div class="criterion-info">
                <h3 class="criterion-name">{{ criterion.name }}</h3>
                <p class="criterion-description">{{ criterion.description }}</p>
            </div>
            <button @click="$emit('remove')" class="remove-button" type="button">
                <font-awesome-icon icon="times" />
            </button>
        </div>

        <div class="weight-section">
            <div class="weight-label">Weight:</div>
            <div class="weight-controls">
                <VaSlider v-model="sliderValue" :min="0" :max="1" :step="0.01" class="weight-slider" color="primary" />
                <VaInput v-model="inputValue" class="weight-input" placeholder="0.00"
                    @update:model-value="handleInputChange" @blur="handleInputBlur" />
            </div>
            <div class="weight-display">{{ formattedWeight }}</div>
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

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Separate refs for slider and input to avoid validation conflicts
const sliderValue = computed({
    get: () => props.modelValue,
    set: (value: number) => {
        const clampedValue = Math.max(0, Math.min(1, value))
        emit('update:modelValue', clampedValue)
    }
})

const inputValue = ref(props.modelValue.toFixed(2))

const formattedWeight = computed(() => {
    return props.modelValue.toFixed(2)
})

// Watch for external changes to modelValue
watch(() => props.modelValue, (newValue) => {
    inputValue.value = newValue.toFixed(2)
})

const handleInputChange = (value: string) => {
    // Just update the local input value, don't emit yet
    inputValue.value = value
}

const handleInputBlur = () => {
    const numericValue = parseFloat(inputValue.value)
    if (!isNaN(numericValue)) {
        const clampedValue = Math.max(0, Math.min(1, numericValue))
        emit('update:modelValue', clampedValue)
    } else {
        // Reset to current value if invalid
        inputValue.value = props.modelValue.toFixed(2)
    }
}
</script>

<style scoped>
.weight-card {
    background: white;
    border: 2px solid #e5e7eb;
    border-radius: 0.75rem;
    padding: 1.5rem;
    transition: all 0.2s ease-in-out;
    position: relative;
}

.weight-card:hover {
    border-color: #d1d5db;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.weight-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.criterion-info {
    flex: 1;
    margin-right: 1rem;
}

.criterion-name {
    font-size: 1.125rem;
    font-weight: 600;
    color: #374151;
    margin: 0 0 0.5rem 0;
}

.criterion-description {
    font-size: 0.875rem;
    color: #6b7280;
    margin: 0;
    line-height: 1.4;
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

.weight-section {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.weight-label {
    font-size: 0.875rem;
    font-weight: 600;
    color: #374151;
}

.weight-controls {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.weight-slider {
    flex: 1;
}

.weight-input {
    width: 80px;
    flex-shrink: 0;
}

.weight-display {
    font-size: 0.875rem;
    color: var(--va-primary);
    font-weight: 600;
    text-align: center;
    padding: 0.25rem 0.5rem;
    background: rgba(148, 35, 224, 0.1);
    border-radius: 0.25rem;
}

@media (max-width: 640px) {
    .weight-controls {
        flex-direction: column;
        align-items: stretch;
        gap: 0.5rem;
    }

    .weight-input {
        width: 100%;
    }
}
</style>