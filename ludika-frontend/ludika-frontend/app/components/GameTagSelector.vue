<template>
    <div class="game-tag-selector">
        <!-- Selected tags with remove functionality -->
        <div class="selected-tags">
            <VaChip v-for="tag in selectedTagsData" :key="tag.id" :color="'primary'" :size="size"
                class="game-tag removable-tag" @click="removeTag(tag.id)">
                <div class="tag-content">
                    <font-awesome-icon v-if="tag.icon" :icon="tag.icon" class="tag-icon" />
                    <span class="tag-name">{{ tag.name }}</span>
                    <font-awesome-icon icon="times" class="remove-icon" />
                </div>
            </VaChip>

            <!-- Add Tag button -->
            <VaDropdown v-model="dropdownOpen" :disabled="availableTags.length === 0" prevent-overflow stateful>
                <template #anchor>
                    <VaChip :color="'success'" :size="size" class="add-tag-chip" :disabled="availableTags.length === 0">
                        <div class="tag-content">
                            <font-awesome-icon icon="plus" class="tag-icon" />
                            <span class="tag-name">Add Tag</span>
                        </div>
                    </VaChip>
                </template>

                <VaDropdownContent class="tag-dropdown">
                    <div class="tag-search">
                        <VaInput v-model="searchQuery" placeholder="Search tags..." :clearable="true"
                            class="search-input">
                            <template #prependInner>
                                <font-awesome-icon icon="search" />
                            </template>
                        </VaInput>
                    </div>
                    <div class="tag-list">
                        <div v-for="tag in filteredAvailableTags" :key="tag.id" class="tag-option" @click="addTag(tag)">
                            <font-awesome-icon v-if="tag.icon" :icon="tag.icon" class="option-icon" />
                            <span class="option-name">{{ tag.name }}</span>
                        </div>
                        <div v-if="filteredAvailableTags.length === 0" class="no-tags">
                            No available tags
                        </div>
                    </div>
                </VaDropdownContent>
            </VaDropdown>
        </div>

        <!-- Loading and error states -->
        <div v-if="tagsLoading" class="loading-state">
            <VaProgressCircle indeterminate size="small" />
            <span>Loading tags...</span>
        </div>
        <div v-if="tagsError" class="error-state">
            <font-awesome-icon icon="exclamation-triangle" class="text-danger" />
            <span>{{ tagsError }}</span>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { TagPublic } from '~~/types/game'

interface Props {
    selectedTags: readonly number[]
    availableTagsData: readonly TagPublic[]
    size?: 'small' | 'medium' | 'large'
    tagsLoading?: boolean
    tagsError?: string | null
}

interface Emits {
    (e: 'update:selectedTags', tags: number[]): void
}

const props = withDefaults(defineProps<Props>(), {
    size: 'small',
    tagsLoading: false,
    tagsError: null
})

const emit = defineEmits<Emits>()

const dropdownOpen = ref(false)
const searchQuery = ref('')

// Get tag objects for selected tag IDs
const selectedTagsData = computed(() => {
    return props.availableTagsData.filter(tag => props.selectedTags.includes(tag.id))
})

// Get tags that aren't already selected
const availableTags = computed(() => {
    return props.availableTagsData.filter(tag => !props.selectedTags.includes(tag.id))
})

// Filter available tags based on search query
const filteredAvailableTags = computed(() => {
    if (!searchQuery.value.trim()) {
        return availableTags.value
    }

    const query = searchQuery.value.toLowerCase()
    return availableTags.value.filter(tag =>
        tag.name.toLowerCase().includes(query)
    )
})

const addTag = (tag: TagPublic) => {
    const newTags = [...props.selectedTags, tag.id]
    emit('update:selectedTags', newTags)
    dropdownOpen.value = false
    searchQuery.value = ''
}

const removeTag = (tagId: number) => {
    const newTags = props.selectedTags.filter(id => id !== tagId)
    emit('update:selectedTags', newTags)
}
</script>

<style scoped>
.game-tag-selector {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.selected-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: flex-start;
}

.game-tag {
    font-size: 0.75rem;
    min-height: 2rem;
    display: flex;
    align-items: center;
}

.removable-tag {
    cursor: pointer;
    transition: all 0.2s ease;
}

.removable-tag:hover {
    transform: scale(0.95);
}

.removable-tag:hover .remove-icon {
    opacity: 1;
}

.add-tag-chip {
    cursor: pointer;
    border: 2px dashed;
    background-color: transparent !important;
    min-height: 2rem;
    display: flex;
    align-items: center;
}

.add-tag-chip:hover {
    transform: scale(1.05);
}

.tag-content {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    position: relative;
}

.tag-icon {
    font-size: 0.875rem;
}

.remove-icon {
    font-size: 0.75rem;
    opacity: 0;
    transition: opacity 0.2s ease;
    position: absolute;
    right: 0;
    background-color: inherit;
    border-radius: 50%;
}

.removable-tag .tag-name {
    transition: opacity 0.2s ease;
}

.removable-tag:hover .tag-name {
    opacity: 0.7;
}

.tag-name {
    line-height: 1;
}

.tag-dropdown {
    min-width: 250px;
    max-width: 300px;
}

.tag-search {
    padding: 0.5rem;
    border-bottom: 1px solid #e5e7eb;
}

.search-input {
    margin: 0;
}

.tag-list {
    max-height: 200px;
    overflow-y: auto;
}

.tag-option {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem;
    cursor: pointer;
    transition: background-color 0.2s ease;
}

.tag-option:hover {
    background-color: #f3f4f6;
}

.option-icon {
    font-size: 1rem;
    color: #6b7280;
}

.option-name {
    font-size: 0.875rem;
}

.no-tags {
    padding: 1rem;
    text-align: center;
    color: #6b7280;
    font-style: italic;
}

.loading-state,
.error-state {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    color: #6b7280;
}

.error-state {
    color: #dc2626;
}
</style>