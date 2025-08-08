<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'
import RankingProfilePage from '~/components/RankingProfilePage.vue'

definePageMeta({
    layout: 'default',
})

const { isAuthenticated } = useAuth()

// Redirect if not authenticated
watch(
    isAuthenticated,
    (authenticated) => {
        if (!authenticated) {
            navigateTo('/login')
        }
    },
    { immediate: true },
)
</script>

<template>
    <RankingProfilePage mode="create" />

</template>