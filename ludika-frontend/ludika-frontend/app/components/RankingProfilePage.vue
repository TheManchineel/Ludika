<script setup lang="ts">
import RankingProfileForm from '~/components/RankingProfileForm.vue'

interface Props {
    mode: 'create' | 'edit'
    profileId?: string
}

const props = defineProps<Props>()

const title = computed(() => (props.mode === 'edit' ? 'Edit Ranking Profile' : 'Create Ranking Profile'))
const subtitle = computed(() =>
    props.mode === 'edit'
        ? 'Modify your ranking profile to better reflect your preferences for game evaluation.'
        : 'Define a custom profile to rank games based on criteria that matter most to you.'
)
const breadcrumbLast = computed(() => (props.mode === 'edit' ? 'Edit Profile' : 'New Profile'))
const breadcrumbTo = computed(() => (props.mode === 'edit' ? `/rank-games/profiles/${props.profileId}` : '/rank-games/profiles/new'))
const titleIcon = computed(() => (props.mode === 'edit' ? 'edit' : 'plus'))
</script>

<template>
    <div class="ranking-profile-page">
        <!-- Page Header -->
        <div class="page-header">
            <div class="container">
                <div class="header-content">
                    <div class="breadcrumb-container">
                        <VaBreadcrumbs>
                            <VaBreadcrumbsItem to="/rank-games">Rank Games</VaBreadcrumbsItem>
                            <VaBreadcrumbsItem :to="breadcrumbTo">{{ breadcrumbLast }}</VaBreadcrumbsItem>
                        </VaBreadcrumbs>
                    </div>

                    <h1 class="page-title">
                        <font-awesome-icon :icon="titleIcon" class="title-icon" />
                        {{ title }}
                    </h1>
                    <p class="page-subtitle">{{ subtitle }}</p>
                </div>
            </div>
        </div>

        <!-- Form Section -->
        <div class="form-section">
            <div class="container">
                <RankingProfileForm :mode="props.mode" :profile-id="props.profileId" />
            </div>
        </div>
    </div>

</template>

<style scoped>
.ranking-profile-page {
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
