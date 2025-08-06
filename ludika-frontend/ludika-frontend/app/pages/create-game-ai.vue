<script setup lang="ts">
definePageMeta({
  layout: 'default'
})

// Form data
const formData = reactive({
  url: ''
})

// State management
const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// Form reference
const formRef = ref()

// Get authenticated fetch from useAuth
const { authenticatedFetch } = useAuth()

// URL validation
const isValidUrl = (url: string): boolean => {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

// Form validation
const isFormValid = computed(() => {
  return formData.url.trim() !== '' && isValidUrl(formData.url)
})

// Clear messages
const clearError = () => {
  errorMessage.value = ''
}

const clearSuccess = () => {
  successMessage.value = ''
}

// Handle form submission
const handleSubmit = async () => {
  if (!formRef.value.validate()) {
    return
  }

  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response = await authenticatedFetch<{ success: boolean; game_id?: string; message?: string }>('/api/v1/ai/add-game-from-url', {
      method: 'POST',
      query: {
        url: formData.url
      }
    })

    if (response.success) {
      // Navigate to the created game
      await navigateTo(`/games/${response.game_id}`)
    } else {
      // Show error message
      errorMessage.value = response.message || 'Failed to create game from URL'
    }
  } catch (error: any) {
    console.error('Error creating game:', error)
    errorMessage.value = error.data?.message || 'An unexpected error occurred. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="ai-game-form-container">
    <div class="container">
      <div class="form-wrapper">
        <VaCard class="form-card">
          <VaCardContent>
            <div class="form-header">
              <h2 class="form-title">
                <font-awesome-icon icon="magic" class="title-icon" />
                Create Game with AI
              </h2>
              <p class="form-description">
                Enter a game URL and let our AI analyze it to automatically create a game entry for you.
              </p>
            </div>

            <!-- Loading State -->
            <div v-if="isLoading" class="loading-container">
              <VaSpinner size="large" />
              <p class="loading-text">
                ✨ Processing your request... ✨
              </p>
            </div>

            <!-- Form -->
            <VaForm v-else ref="formRef" @submit.prevent="handleSubmit">
              <div class="form-content">
                <VaInput v-model="formData.url" label="Game URL" placeholder="https://example.com/game" :rules="[
                  (v: string) => !!v || 'Game URL is required',
                  (v: string) => isValidUrl(v) || 'Please enter a valid URL'
                ]" required class="form-field" :disabled="isLoading" />

                <div class="form-actions">
                  <VaButton type="submit" :loading="isLoading" :disabled="!isFormValid || isLoading"
                    class="submit-button">
                    <font-awesome-icon icon="magic" class="button-icon" />
                    Generate!
                  </VaButton>
                </div>
              </div>
            </VaForm>

            <!-- Error Display -->
            <VaAlert v-if="errorMessage" color="danger" class="form-error" closeable @close="clearError">
              {{ errorMessage }}
            </VaAlert>

            <!-- Success Display -->
            <VaAlert v-if="successMessage" color="success" class="form-success" closeable @close="clearSuccess">
              {{ successMessage }}
            </VaAlert>
          </VaCardContent>
        </VaCard>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ai-game-form-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 0;
}

.container {
  max-width: 600px;
  margin: 0 auto;
  padding: 0 1rem;
}

.form-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
}

.form-card {
  width: 100%;
  max-width: 500px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
}

.form-header {
  text-align: center;
  margin-bottom: 2rem;
}

.form-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--va-primary);
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.title-icon {
  color: var(--va-primary);
}

.form-description {
  color: var(--va-text-secondary);
  font-size: 1rem;
  line-height: 1.5;
  margin: 0;
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-field {
  width: 100%;
}

.form-actions {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
}

.submit-button {
  min-width: 150px;
  height: 48px;
  font-size: 1.1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, var(--va-primary) 0%, var(--va-primary-dark) 100%);
  border: none;
  transition: all 0.3s ease;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.button-icon {
  font-size: 1rem;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 0;
  gap: 1.5rem;
}

.loading-text {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--va-primary);
  text-align: center;
  margin: 0;
}

.form-error {
  margin-top: 1rem;
}

.form-success {
  margin-top: 1rem;
}

/* Responsive design */
@media (max-width: 768px) {
  .ai-game-form-container {
    padding: 1rem 0;
  }

  .container {
    padding: 0 0.5rem;
  }

  .form-title {
    font-size: 1.5rem;
  }

  .form-description {
    font-size: 0.9rem;
  }

  .submit-button {
    min-width: 120px;
    height: 44px;
    font-size: 1rem;
  }
}
</style>