<template>
    <div class="game-form-editor">
        <VaCard class="form-card">
            <VaCardContent>
                <div class="form-header">
                    <h2 class="form-title">
                        {{ isEditing ? 'Edit Game' : 'Create New Game' }}
                    </h2>
                    <p v-if="isEditing && gameData" class="game-id">
                        Game ID: {{ gameData.id }}
                    </p>
                </div>

                <VaForm ref="formRef" @submit.prevent="handleSubmit">
                    <div class="form-grid">
                        <!-- Game Name -->
                        <VaInput v-model="formData.name" label="Game Name" placeholder="Enter the name of the game"
                            :rules="[(v: string) => !!v || 'Game name is required']" required class="form-field" />

                        <!-- Game URL -->
                        <VaInput v-model="formData.url" label="Game URL" placeholder="https://example.com/game" :rules="[
                            (v: string) => !!v || 'Game URL is required',
                            (v: string) => isValidUrl(v) || 'Please enter a valid URL'
                        ]" required class="form-field" />

                        <!-- Game Description -->
                        <div class="form-field description-field">
                            <VaTextarea v-model="formData.description" label="Description"
                                placeholder="Describe the game..."
                                :rules="[(v: string) => !!v || 'Description is required']" required :min-rows="4"
                                :max-rows="8" autosize />
                        </div>

                        <!-- Tags Section -->
                        <div class="form-field tags-field">
                            <label class="va-input-label">Tags</label>
                            <p class="field-description">
                                Select tags that describe this game. Click on selected tags to remove them.
                            </p>
                            <GameTagSelector v-model:selected-tags="formData.tags" :available-tags-data="tags"
                                :tags-loading="tagsLoading" :tags-error="tagsError" size="medium" />
                        </div>

                        <!-- Images Section (only in edit mode) -->
                        <div v-if="isEditing && currentGameData" class="form-field images-field">
                            <GameImageManager :game-data="currentGameData" @images-updated="handleImagesUpdated" />
                        </div>
                    </div>

                    <!-- Form Actions -->
                    <div class="form-actions">
                        <div class="form-actions-left">
                            <VaButton v-if="isEditing && gameData" color="danger" @click="confirmDelete"
                                :disabled="updateLoading">
                                Delete Game
                            </VaButton>
                        </div>

                        <div class="form-actions-right">
                            <VaButton preset="secondary" @click="handleCancel" :disabled="updateLoading">
                                Cancel
                            </VaButton>

                            <VaButton type="submit" :loading="updateLoading" :disabled="!isFormValid">
                                {{ isEditing ? 'Save Changes' : 'Create Game' }}
                            </VaButton>
                        </div>
                    </div>
                </VaForm>

                <!-- Error Display -->
            </VaCardContent>
            <VaAlert v-if="updateError" color="danger" class="form-error" closeable @close="clearError">
                {{ updateError }}
            </VaAlert>
        </VaCard>

        <!-- Delete Confirmation Modal -->
        <ConfirmationModal v-model="showDeleteModal" title="Confirm Game Deletion"
            :message="`Are you sure you want to delete the game ${gameData?.name}?`"
            warning-message="This action cannot be undone." confirm-text="Delete Game" confirm-color="danger"
            :loading="updateLoading" @confirm="handleDelete" @cancel="showDeleteModal = false" />
    </div>
</template>

<script setup lang="ts">
import type { GamePublic, GameCreate, GameUpdate } from '~~/types/game'
import { useGames } from '~/composables/useGames'
import GameTagSelector from './GameTagSelector.vue'
import GameImageManager from './GameImageManager.vue'
import ConfirmationModal from './ConfirmationModal.vue'

interface Props {
    gameData?: GamePublic | null
    isEditing?: boolean
}

interface Emits {
    (e: 'success', game: GamePublic): void
    (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
    gameData: null,
    isEditing: false
})

const emit = defineEmits<Emits>()

const {
    tags,
    tagsLoading,
    tagsError,
    updateLoading,
    updateError,
    fetchTags,
    updateGame,
    createGame,
    deleteGame
} = useGames()

const formRef = ref()

// Form data
const formData = reactive({
    name: '',
    description: '',
    url: '',
    tags: [] as number[]
})

// Current game data for image management (updates independently of form data)
const currentGameData = ref<GamePublic | null>(null)

// Delete confirmation modal state
const showDeleteModal = ref(false)

// Initialize form data
const initializeFormData = () => {
    if (props.isEditing && props.gameData) {
        formData.name = props.gameData.name
        formData.description = props.gameData.description
        formData.url = props.gameData.url
        formData.tags = props.gameData.tags.map(tag => tag.id)
        currentGameData.value = props.gameData
    } else {
        // Reset for create mode
        formData.name = ''
        formData.description = ''
        formData.url = ''
        formData.tags = []
        currentGameData.value = null
    }
}

// Validation
const isValidUrl = (url: string): boolean => {
    try {
        new URL(url)
        return true
    } catch {
        return false
    }
}

const isFormValid = computed(() => {
    return formData.name.trim() !== '' &&
        formData.description.trim() !== '' &&
        formData.url.trim() !== '' &&
        isValidUrl(formData.url)
})

// Form submission
const handleSubmit = async () => {
    if (!formRef.value.validate()) {
        return
    }

    try {
        let result: GamePublic

        if (props.isEditing && props.gameData) {
            // Create update payload with only changed fields
            const updatePayload: GameUpdate = {}

            if (formData.name !== props.gameData.name) {
                updatePayload.name = formData.name
            }
            if (formData.description !== props.gameData.description) {
                updatePayload.description = formData.description
            }
            if (formData.url !== props.gameData.url) {
                updatePayload.url = formData.url
            }

            // Always include tags since they might have changed
            const currentTagIds = props.gameData.tags.map(tag => tag.id).sort()
            const newTagIds = [...formData.tags].sort()
            if (JSON.stringify(currentTagIds) !== JSON.stringify(newTagIds)) {
                updatePayload.tags = formData.tags
            }

            // Only submit if there are changes
            if (Object.keys(updatePayload).length === 0) {
                // No changes, just emit success with current data
                emit('success', props.gameData)
                return
            }

            result = await updateGame(props.gameData.id, updatePayload)
        } else {
            // Create new game
            const createPayload: GameCreate = {
                name: formData.name,
                description: formData.description,
                url: formData.url,
                tags: formData.tags
            }

            result = await createGame(createPayload)
        }

        emit('success', result)
    } catch (error) {
        console.error('Form submission error:', error)
        // Error is handled by the composable and displayed via updateError
    }
}

const handleCancel = () => {
    emit('cancel')
}

const handleImagesUpdated = (updatedGame: GamePublic) => {
    // Update the current game data with the latest version
    // This keeps the image section updated without affecting the form data
    currentGameData.value = updatedGame
}

const clearError = () => {
    // The updateError is managed by the composable, so we would need to clear it
    // For now, we can reset form if needed, but the error will clear on next action
}

const confirmDelete = () => {
    showDeleteModal.value = true
}

const handleDelete = async () => {
    console.log("handleDelete", props.gameData)
    if (!props.gameData?.id) return

    try {
        await deleteGame(props.gameData.id)
        showDeleteModal.value = false
        // Redirect to homepage on successful deletion
        await navigateTo('/')
    } catch (error) {
        console.error('Delete error:', error)
        showDeleteModal.value = false
        // Error is handled by the composable and displayed via updateError
    }
}

// Watch for gameData changes to reinitialize form
watch(() => props.gameData, () => {
    initializeFormData()
}, { immediate: true })

watch(() => props.isEditing, () => {
    initializeFormData()
})

// Fetch tags when component mounts
onMounted(async () => {
    await fetchTags()
})
</script>

<style scoped>
.game-form-editor {
    max-width: 800px;
    margin: 0 auto;
    padding: 1rem;
}

.form-card {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.form-header {
    margin-bottom: 2rem;
    text-align: center;
}

.form-title {
    font-size: 2rem;
    font-weight: 700;
    color: #374151;
    margin-bottom: 0.5rem;
}

.game-id {
    font-family: monospace;
    background-color: #f3f4f6;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    display: inline-block;
    color: #6b7280;
    font-size: 0.875rem;
}

.form-grid {
    display: grid;
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.form-field {
    width: 100%;
}

.description-field {
    grid-column: 1 / -1;
}

.tags-field {
    grid-column: 1 / -1;
}

.images-field {
    grid-column: 1 / -1;
}

.field-description {
    font-size: 0.875rem;
    color: #6b7280;
    margin-bottom: 0.75rem;
    margin-top: 0.25rem;
}

.va-input-label {
    display: block;
    font-size: 0.875rem;
    font-weight: 500;
    color: #374151;
    margin-bottom: 0.25rem;
}

.form-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 2rem;
}

.form-actions-left {
    display: flex;
}

.form-actions-right {
    display: flex;
    gap: 1rem;
}

.form-error {
    margin-top: 1rem;
}

@media (min-width: 640px) {
    .form-grid {
        grid-template-columns: 1fr 1fr;
    }

    .form-field:first-child {
        grid-column: 1 / -1;
    }
}
</style>