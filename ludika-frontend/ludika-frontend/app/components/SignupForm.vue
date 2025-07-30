<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'

interface Props {
    showLogin?: boolean
}

const props = withDefaults(defineProps<Props>(), {
    showLogin: false
})

const emit = defineEmits<{
    signupSuccess: []
    switchToLogin: []
}>()

const { signup, isLoading } = useAuth()

const form = reactive({
    email: '',
    visible_name: '',
    password: ''
})

const errors = reactive({
    email: '',
    visible_name: '',
    password: '',
    general: ''
})

const validateForm = (): boolean => {
    // Reset errors
    errors.email = ''
    errors.visible_name = ''
    errors.password = ''
    errors.general = ''

    let isValid = true

    if (!form.email.trim()) {
        errors.email = 'Email is required'
        isValid = false
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
        errors.email = 'Please enter a valid email address'
        isValid = false
    }

    if (!form.visible_name.trim()) {
        errors.visible_name = 'Display name is required'
        isValid = false
    } else if (form.visible_name.trim().length < 2) {
        errors.visible_name = 'Display name must be at least 2 characters'
        isValid = false
    }

    if (!form.password.trim()) {
        errors.password = 'Password is required'
        isValid = false
    } else if (form.password.trim().length < 6) {
        errors.password = 'Password must be at least 6 characters'
        isValid = false
    }

    return isValid
}

const handleSignup = async () => {
    if (!validateForm()) return

    try {
        await signup({
            email: form.email,
            visible_name: form.visible_name,
            password: form.password
        })

        // Reset form
        form.email = ''
        form.visible_name = ''
        form.password = ''

        emit('signupSuccess')
    } catch (error: any) {
        errors.general = error?.data?.detail || 'Signup failed. Please try again.'
    }
}

const handleKeydown = (event: KeyboardEvent) => {
    if (event.key === 'Enter') {
        handleSignup()
    }
}
</script>

<template>
    <VaCard class="signup-form">
        <VaCardContent>
            <div class="form-header">
                <h2 class="form-title">Sign Up</h2>
                <p class="form-subtitle">Create your Ludika account</p>
            </div>

            <VaForm @submit.prevent="handleSignup">
                <div class="form-fields">
                    <VaInput v-model="form.email" label="Email" type="email" :error="!!errors.email"
                        :error-messages="errors.email" :disabled="isLoading" @keydown="handleKeydown" clearable />

                    <VaInput v-model="form.visible_name" label="Display Name" type="text" :error="!!errors.visible_name"
                        :error-messages="errors.visible_name" :disabled="isLoading" @keydown="handleKeydown"
                        clearable />

                    <VaInput v-model="form.password" label="Password" type="password" :error="!!errors.password"
                        :error-messages="errors.password" :disabled="isLoading" @keydown="handleKeydown" clearable />
                </div>

                <VaAlert v-if="errors.general" color="danger" :model-value="true" closeable class="error-alert"
                    @input="errors.general = ''">
                    {{ errors.general }}
                </VaAlert>

                <div class="form-actions">
                    <VaButton type="submit" :loading="isLoading" :disabled="isLoading" class="signup-button"
                        @click="handleSignup">
                        Sign Up
                    </VaButton>

                    <div v-if="showLogin" class="login-link">
                        <p>
                            Already have an account?
                            <VaButton preset="plain" @click="$emit('switchToLogin')">
                                Sign in
                            </VaButton>
                        </p>
                    </div>
                </div>
            </VaForm>
        </VaCardContent>
    </VaCard>
</template>

<style scoped>
.signup-form {
    max-width: 400px;
    margin: 0 auto;
    width: 100%;
}

.signup-form :deep(.va-card__content) {
    padding: 2rem !important;
    margin: 0 !important;
    width: 100% !important;
    box-sizing: border-box !important;
}

.signup-form :deep(.va-form) {
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

.signup-button {
    width: 100%;
}

.login-link {
    text-align: center;
}

.login-link p {
    margin: 0;
    color: #666;
}
</style>