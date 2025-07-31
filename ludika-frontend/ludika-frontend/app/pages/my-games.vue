<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'

// Set up auth
const { isAuthenticated } = useAuth()

// Redirect if not authenticated
watch(isAuthenticated, (authenticated) => {
    if (!authenticated) {
        navigateTo('/login')
    }
}, { immediate: true })
</script>

<template>
    <div>
        <GameLibrary title="My Games" subtitle="Manage your created games" apiEndpoint="/api/v1/games/my-games"
            :showHero="true" :searchable="true" :tagFilterable="false" />
    </div>
</template>