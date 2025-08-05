<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'
import RankingProfileForm from '~/components/RankingProfileForm.vue'

definePageMeta({
    layout: 'default'
})

const { isAuthenticated } = useAuth()

// Redirect if not authenticated
watch(isAuthenticated, (authenticated) => {
    if (!authenticated) {
        navigateTo('/login')
    }
}, { immediate: true })
</script>

<template>
    <div class="new-profile-page">
        <!-- Page Header -->
        <div class="page-header">
            <div class="container">
                <div class="header-content">
                    <div class="breadcrumb-container">
                        <VaBreadcrumbs>
                            <VaBreadcrumbsItem to="/rank-games">Rank Games</VaBreadcrumbsItem>
                            <VaBreadcrumbsItem to="/rank-games/profiles/new">New Profile</VaBreadcrumbsItem>
                        </VaBreadcrumbs>
                    </div>

                    <h1 class="page-title">
                        <font-awesome-icon icon="plus" class="title-icon" />
                        Create Ranking Profile
                    </h1>
                    <p class="page-subtitle">
                        Define a custom profile to rank games based on criteria that matter most to you.
                    </p>
                </div>
            </div>
        </div>

        <!-- Form Section -->
        <div class="form-section">
            <div class="container">
                <RankingProfileForm mode="create" />
            </div>
        </div>
    </div>
</template>

<style scoped>
.new-profile-page {
    min-height: 100vh;
    background-color: #f8f9fa;
}

.page-header {
    background: linear-gradient(135deg, #9423e0 0%, #4f1377 100%);
    padding: 2rem 0;
    color: white;
}

.container {
    max-width: var(--container-max-width);
    margin: 0 auto;
    padding: 0 var(--container-padding);
}

.header-content {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.breadcrumb-container {
    margin-bottom: 0.5rem;
}

.page-title {
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.title-icon {
    font-size: 2rem;
}

.page-subtitle {
    font-size: 1.1rem;
    opacity: 0.9;
    margin: 0;
    max-width: 600px;
}

.form-section {
    padding: 2rem 0;
    background: white;
}

@media (max-width: 768px) {
    .page-title {
        font-size: 2rem;
    }

    .title-icon {
        font-size: 1.5rem;
    }
}
</style>