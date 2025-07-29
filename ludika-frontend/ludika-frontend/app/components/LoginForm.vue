<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'

interface Props {
  showSignup?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showSignup: false
})

const emit = defineEmits<{
  loginSuccess: []
  switchToSignup: []
}>()

const { login, isLoading } = useAuth()

const form = reactive({
  username: '',
  password: ''
})

const errors = reactive({
  username: '',
  password: '',
  general: ''
})

const validateForm = (): boolean => {
  // Reset errors
  errors.username = ''
  errors.password = ''
  errors.general = ''

  let isValid = true

  if (!form.username.trim()) {
    errors.username = 'Email is required'
    isValid = false
  }

  if (!form.password.trim()) {
    errors.password = 'Password is required'
    isValid = false
  }

  return isValid
}

const handleLogin = async () => {
  if (!validateForm()) return

  try {
    await login({
      username: form.username,
      password: form.password
    })

    // Reset form
    form.username = ''
    form.password = ''

    emit('loginSuccess')
  } catch (error: any) {
    errors.general = error?.data?.detail || 'Login failed. Please check your credentials.'
  }
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter') {
    handleLogin()
  }
}
</script>

<template>
  <VaCard class="login-form">
    <VaCardContent>
      <div class="form-header">
        <h2 class="form-title">Sign In</h2>
        <p class="form-subtitle">Enter your credentials to access Ludika</p>
      </div>

      <VaForm @submit.prevent="handleLogin">
        <div class="form-fields">
          <VaInput v-model="form.username" label="Email" type="email" :error="!!errors.username"
            :error-messages="errors.username" :disabled="isLoading" @keydown="handleKeydown" clearable />

          <VaInput v-model="form.password" label="Password" type="password" :error="!!errors.password"
            :error-messages="errors.password" :disabled="isLoading" @keydown="handleKeydown" clearable />
        </div>

        <VaAlert v-if="errors.general" color="danger" :model-value="true" closeable class="error-alert"
          @input="errors.general = ''">
          {{ errors.general }}
        </VaAlert>

        <div class="form-actions">
          <VaButton type="submit" :loading="isLoading" :disabled="isLoading" class="login-button" @click="handleLogin">
            Sign In
          </VaButton>

          <div v-if="showSignup" class="signup-link">
            <p>
              Don't have an account?
              <VaButton preset="plain" @click="$emit('switchToSignup')">
                Sign up
              </VaButton>
            </p>
          </div>
        </div>
      </VaForm>
    </VaCardContent>
  </VaCard>
</template>

<style scoped>
.login-form {
  max-width: 400px;
  margin: 0 auto;
  width: 100%;
}

.login-form :deep(.va-card__content) {
  padding: 2rem !important;
  margin: 0 !important;
  width: 100% !important;
  box-sizing: border-box !important;
}

.login-form :deep(.va-form) {
  width: 100% !important;
  margin: 0 !important;
  padding: 0 !important;
}

.form-header {
  text-align: center;
  margin-bottom: 2rem;
}

.form-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #333;
}

.form-subtitle {
  color: #666;
  margin: 0;
}

.form-fields {
  display: grid !important;
  grid-template-columns: 1fr !important;
  gap: 1.5rem !important;
  margin: 0 0 2rem 0 !important;
  padding: 10 !important;
  width: 100% !important;
}

/* FIXME: fugly hack to fix the input fields not being centered */
.form-fields :deep(*) {
  padding: 5 !important;
  box-sizing: border-box !important;
}


.error-alert {
  margin-top: 0.5rem;
}

.form-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.login-button {
  width: 100%;
}

.signup-link {
  text-align: center;
}

.signup-link p {
  margin: 0;
  color: #666;
}
</style>