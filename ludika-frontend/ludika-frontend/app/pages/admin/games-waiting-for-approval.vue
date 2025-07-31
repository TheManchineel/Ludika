<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'

definePageMeta({
    layout: 'default'
})

const { isAdmin, isContentModerator } = useAuth()

// Redirect if not privileged user
onMounted(() => {
    if (!isAdmin() && !isContentModerator()) {
        navigateTo('/')
    }
})
</script>

<template>
    <div>
        <!-- Breadcrumb navigation -->
        <div class="breadcrumb-container">
            <VaBreadcrumbs>
                <VaBreadcrumbsItem to="/admin">Admin</VaBreadcrumbsItem>
                <VaBreadcrumbsItem to="/admin/games-waiting-for-approval">Games Waiting for Approval</VaBreadcrumbsItem>
            </VaBreadcrumbs>
        </div>

        <!-- Reuse GameLibrary component with custom settings -->
        <GameLibrary :searchable="true" :tagFilterable="false" title="Games Waiting for Approval"
            subtitle="Review and approve games submitted by users." api-endpoint="/api/v1/games/waiting-for-approval"
            :show-hero="true" />
    </div>
</template>

<style scoped>
.breadcrumb-container {
    max-width: var(--container-max-width);
    margin: 0 auto;
    padding: 1rem var(--container-padding);
    background-color: #f8f9fa;
}
</style>