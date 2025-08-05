<script setup lang="ts">
import { useUsers } from '~/composables/useUsers'
import { useAuth } from '~/composables/useAuth'

definePageMeta({
    layout: 'default'
})

const { user, userLoading, userError, fetchCurrentUser } = useUsers()
const { isAuthenticated } = useAuth()

// Redirect if not authenticated
watch(isAuthenticated, (authenticated) => {
    if (!authenticated) {
        navigateTo('/login')
    }
}, { immediate: true })

onMounted(() => {
    if (isAuthenticated.value) {
        fetchCurrentUser()
    }
})
</script>

<template>
    <UserProfile :user="user" :loading="userLoading" :error="userError" :show-back-button="false" />
</template>