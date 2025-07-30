<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'

definePageMeta({
    layout: 'default'
})

const { isAuthenticated } = useAuth()

// Redirect if already authenticated
watch(isAuthenticated, (authenticated) => {
    if (authenticated) {
        navigateTo('/')
    }
}, { immediate: true })

const handleSignupSuccess = () => {
    navigateTo('/')
    console.log('Signup successful')
    console.log(isAuthenticated.value)
}
</script>

<template>
    <div class="signup-page">
        <div class="signup-container">
            <SignupForm :show-login="true" @signup-success="handleSignupSuccess"
                @switch-to-login="navigateTo('/login')" />
        </div>
    </div>
</template>

<style scoped>
.signup-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    padding: 2rem;
}

.signup-container {
    width: 100%;
    max-width: 400px;
}
</style>