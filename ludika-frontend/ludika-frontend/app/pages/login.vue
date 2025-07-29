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

const handleLoginSuccess = () => {
  navigateTo('/')
  console.log('Login successful')
  console.log(isAuthenticated.value)
}
</script>

<template>
  <div class="login-page">
    <div class="login-container">
      <LoginForm :show-signup="true" @login-success="handleLoginSuccess" @switch-to-signup="navigateTo('/signup')" />
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem;
}

.login-container {
  width: 100%;
  max-width: 400px;
}
</style>