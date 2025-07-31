<template>
    <div class="game-image-manager">
        <h3 class="section-title">Game Images</h3>
        <p class="section-description">
            Manage the images for this game. Hover over an image to delete or replace it.
        </p>

        <!-- Images Grid -->
        <div class="images-grid">
            <!-- Existing Images -->
            <div v-for="image in sortedImages" :key="image.position" class="image-thumbnail-container"
                @mouseenter="hoveredImage = image.position" @mouseleave="hoveredImage = null">
                <div class="image-thumbnail">
                    <img :src="`/static/${image.image}`" :alt="`Game image ${image.position}`" class="thumbnail-img"
                        :class="{ 'blurred': hoveredImage === image.position }" />

                    <!-- Overlay buttons on hover -->
                    <div v-if="hoveredImage === image.position" class="image-overlay">
                        <VaButton preset="secondary" color="danger" size="small" @click="deleteImage(image.position)"
                            :loading="updateLoading" class="overlay-button">
                            <VaIcon name="delete" />
                        </VaButton>

                        <VaButton preset="secondary" color="primary" size="small"
                            @click="triggerReplaceImage(image.position)" :loading="updateLoading"
                            class="overlay-button">
                            <VaIcon name="swap_horiz" />
                        </VaButton>
                    </div>
                </div>

                <div class="image-position">Position {{ image.position }}</div>
            </div>

            <!-- Add Image Button -->
            <div class="add-image-container">
                <VaButton preset="secondary" color="success" size="large" @click="triggerAddImage"
                    :loading="updateLoading" class="add-image-button">
                    <VaIcon name="add" class="add-icon" />
                    Add Image
                </VaButton>
            </div>
        </div>

        <!-- Hidden file inputs -->
        <input ref="addFileInput" type="file" accept="image/*" @change="handleAddImage" style="display: none" />

        <input ref="replaceFileInput" type="file" accept="image/*" @change="handleReplaceImage" style="display: none" />

        <!-- Error Display -->
        <VaAlert v-if="updateError" color="danger" class="error-alert" closeable @close="clearError">
            {{ updateError }}
        </VaAlert>

        <!-- Success Toast -->
        <VaAlert v-if="successMessage" color="success" class="success-alert" closeable @close="successMessage = ''">
            {{ successMessage }}
        </VaAlert>

        <!-- Delete Image Confirmation Modal -->
        <ConfirmationModal v-model="showDeleteModal" title="Delete Image"
            message="Are you sure you want to delete this image?" confirm-text="Delete" confirm-color="danger"
            :loading="updateLoading" @confirm="handleDeleteImage"
            @cancel="() => { showDeleteModal = false; imageToDelete = null }" />
    </div>
</template>

<script setup lang="ts">
import type { GamePublic, GameImage } from '~~/types/game'
import { useGames } from '~/composables/useGames'
import { useAuth } from '~/composables/useAuth'
import ConfirmationModal from './ConfirmationModal.vue'

interface Props {
    gameData: GamePublic
}

interface Emits {
    (e: 'imagesUpdated', game: GamePublic): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const {
    addGameImage,
    replaceGameImage,
    deleteGameImage,
    fetchGameById,
    updateLoading,
    updateError
} = useGames()

const { authenticatedFetch } = useAuth()

const hoveredImage = ref<number | null>(null)
const replacingPosition = ref<number | null>(null)
const successMessage = ref('')
const showDeleteModal = ref(false)
const imageToDelete = ref<number | null>(null)

const addFileInput = ref<HTMLInputElement>()
const replaceFileInput = ref<HTMLInputElement>()

// Computed properties
const sortedImages = computed(() => {
    return [...props.gameData.images].sort((a, b) => a.position - b.position)
})

// Methods
const triggerAddImage = () => {
    if (addFileInput.value) {
        addFileInput.value.click()
    }
}

const triggerReplaceImage = (position: number) => {
    replacingPosition.value = position
    if (replaceFileInput.value) {
        replaceFileInput.value.click()
    }
}

const handleAddImage = async (event: Event) => {
    const target = event.target as HTMLInputElement
    const file = target.files?.[0]

    if (!file) return

    try {
        await addGameImage(props.gameData.id, file)

        // Clear the input
        target.value = ''

        // Refresh game data
        await refreshGameData()

        successMessage.value = 'Image added successfully!'
        setTimeout(() => { successMessage.value = '' }, 3000)
    } catch (error) {
        console.error('Error adding image:', error)
    }
}

const handleReplaceImage = async (event: Event) => {
    const target = event.target as HTMLInputElement
    const file = target.files?.[0]

    if (!file || replacingPosition.value === null) return

    try {
        await replaceGameImage(props.gameData.id, replacingPosition.value, file)

        // Clear the input and position
        target.value = ''
        replacingPosition.value = null

        // Refresh game data
        await refreshGameData()

        successMessage.value = 'Image replaced successfully!'
        setTimeout(() => { successMessage.value = '' }, 3000)
    } catch (error) {
        console.error('Error replacing image:', error)
    }
}

const deleteImage = (position: number) => {
    imageToDelete.value = position
    showDeleteModal.value = true
}

const handleDeleteImage = async () => {
    if (imageToDelete.value === null || imageToDelete.value === undefined) {
        return
    }

    try {
        await deleteGameImage(props.gameData.id, imageToDelete.value)

        // Refresh game data
        await refreshGameData()

        successMessage.value = 'Image deleted successfully!'
        setTimeout(() => { successMessage.value = '' }, 3000)

        showDeleteModal.value = false
        imageToDelete.value = null
    } catch (error) {
        console.error('Error deleting image:', error)
        showDeleteModal.value = false
        imageToDelete.value = null
    }
}

const refreshGameData = async () => {
    try {
        // Fetch the updated game data using the authenticated fetch
        const updatedGame = await authenticatedFetch<GamePublic>(`/api/v1/games/${props.gameData.id}`)
        emit('imagesUpdated', updatedGame)
    } catch (error) {
        console.error('Error refreshing game data:', error)
    }
}

const clearError = () => {
    // Error clearing is handled by the composable automatically
}
</script>

<style scoped>
.game-image-manager {
    margin-top: 2rem;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 0.5rem;
}

.section-description {
    font-size: 0.875rem;
    color: #6b7280;
    margin-bottom: 1.5rem;
}

.images-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 1rem;
}

.image-thumbnail-container {
    position: relative;
    cursor: pointer;
}

.image-thumbnail {
    position: relative;
    width: 100%;
    height: 150px;
    border-radius: 0.5rem;
    overflow: hidden;
    background-color: #f5f5f5;
    display: flex;
    align-items: center;
    justify-content: center;
}

.thumbnail-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: filter 0.3s ease;
}

.thumbnail-img.blurred {
    filter: blur(2px) brightness(0.7);
}

.image-overlay {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    display: flex;
    gap: 0.5rem;
    z-index: 10;
}

.overlay-button {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.image-position {
    text-align: center;
    font-size: 0.75rem;
    color: #6b7280;
    margin-top: 0.5rem;
}

.add-image-container {
    display: flex;
    align-items: center;
    justify-content: center;
}

.add-image-button {
    width: 100%;
    height: 150px;
    border: 2px dashed #d1d5db;
    border-radius: 0.5rem;
    background-color: #f9fafb;
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}

.add-image-button:hover {
    border-color: #059669;
    background-color: #f0fdf4;
}

.add-icon {
    font-size: 1.5rem;
}

.error-alert,
.success-alert {
    margin-top: 1rem;
}

@media (max-width: 640px) {
    .images-grid {
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 1rem;
    }

    .image-thumbnail {
        height: 120px;
    }

    .add-image-button {
        height: 120px;
    }
}
</style>