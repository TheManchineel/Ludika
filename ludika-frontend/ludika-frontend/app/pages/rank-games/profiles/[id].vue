<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'
import RankingProfilePage from '~/components/RankingProfilePage.vue'

definePageMeta({
    layout: 'default',
})

const route = useRoute()
const { isAuthenticated } = useAuth()

const profileId = route.params.id as string

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
    <RankingProfilePage mode="edit" :profile-id="profileId" />

</template>