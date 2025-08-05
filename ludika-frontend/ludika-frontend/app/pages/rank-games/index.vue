<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'
import GameLibrary from '~/components/GameLibrary.vue'

definePageMeta({
    layout: 'default'
})

interface RankingProfile {
    id: number
    name: string
    is_global: boolean
    user_id: string
    weights: Array<{
        weight: number
        criterion_id: number
    }>
}

const { authenticatedFetch, isPrivileged, user } = useAuth()

// State
const profiles = ref<RankingProfile[]>([])
const selectedProfileId = ref<number | null>(null)
const profilesLoading = ref(false)
const profilesError = ref<string | null>(null)

// Computed properties
const selectedProfile = computed(() => {
    return profiles.value.find(p => p.id === selectedProfileId.value) || null
})

const globalProfiles = computed(() => {
    return profiles.value.filter(p => p.is_global)
})

const nonGlobalProfiles = computed(() => {
    return profiles.value.filter(p => !p.is_global)
})

const dropdownOptions = computed(() => {
    const options: Array<{ text: string, value: number }> = []

    // Add global profiles
    globalProfiles.value.forEach(profile => {
        options.push({ text: `${profile.name} (Global)`, value: profile.id })
    })

    // Add non-global profiles
    nonGlobalProfiles.value.forEach(profile => {
        options.push({ text: `${profile.name} (Personal)`, value: profile.id })
    })

    return options
})

const canEditSelectedProfile = computed(() => {
    const profile = selectedProfile.value
    if (!profile) return false

    // Can edit if profile is not global OR user is privileged
    return !profile.is_global || isPrivileged()
})

const rankedGamesEndpoint = computed(() => {
    return selectedProfileId.value ? `/api/v1/games/ranked/${selectedProfileId.value}` : ''
})

// Methods
const fetchProfiles = async () => {
    profilesLoading.value = true
    profilesError.value = null

    try {
        const response = await authenticatedFetch<RankingProfile[]>('/api/v1/reviews/profiles')
        profiles.value = response

        // Auto-select first profile if available
        if (profiles.value.length > 0 && !selectedProfileId.value) {
            const firstProfile = profiles.value[0]
            if (firstProfile) {
                selectedProfileId.value = firstProfile.id
            }
        }
    } catch (error) {
        console.error('Error fetching ranking profiles:', error)
        profilesError.value = 'Failed to load ranking profiles'
    } finally {
        profilesLoading.value = false
    }
}

const handleProfileChange = (profileId: number) => {
    selectedProfileId.value = profileId
}

const editProfile = () => {
    if (selectedProfileId.value) {
        navigateTo(`/rank-games/profiles/${selectedProfileId.value}`)
    }
}

const createNewProfile = () => {
    navigateTo('/rank-games/profiles/new')
}

// Lifecycle
onMounted(() => {
    fetchProfiles()
})
</script>

<template>
    <div class="rank-games-page">
        <!-- Page Header -->
        <div class="page-header">
            <div class="container">
                <h1 class="page-title">
                    <font-awesome-icon icon="chart-line" class="title-icon" />
                    Rank Games
                </h1>
                <p class="page-subtitle">
                    View games ranked by different <a
                        href="https://en.wikipedia.org/wiki/Multiple-criteria_decision_analysis"
                        class="title-link">MCDA</a> profiles, or
                    create your own. Find the best title for your requirements.
                </p>
            </div>
        </div>

        <!-- Profile Selection Section -->
        <div class="profile-section">
            <div class="container">
                <div class="profile-controls">
                    <div class="profile-selector">
                        <label class="selector-label">Ranking Profile:</label>
                        <div class="selector-group">
                            <VaSelect v-model="selectedProfileId" :options="dropdownOptions" :loading="profilesLoading"
                                :disabled="profilesLoading || profilesError !== null"
                                placeholder="Select a ranking profile..." class="profile-dropdown" value-by="value"
                                text-by="text" @update:model-value="handleProfileChange" />

                            <VaButton v-if="canEditSelectedProfile" @click="editProfile" preset="secondary"
                                class="edit-button" :disabled="!selectedProfile">
                                <font-awesome-icon icon="edit" class="button-icon" />
                                <span class="button-text">Edit Profile</span>
                            </VaButton>

                            <VaButton @click="createNewProfile" preset="primary" class="create-button">
                                <font-awesome-icon icon="plus" class="button-icon" />
                                <span class="button-text">New Profile</span>
                            </VaButton>
                        </div>
                    </div>

                    <!-- Error state -->
                    <div v-if="profilesError" class="error-container">
                        <VaAlert color="danger" :title="profilesError" />
                    </div>

                    <!-- Selected profile info -->
                    <div v-if="selectedProfile" class="selected-profile-info">
                        <div class="profile-info-card">
                            <div class="profile-header">
                                <h3 class="profile-name">{{ selectedProfile.name }}</h3>
                                <VaChip :color="selectedProfile.is_global ? 'primary' : 'secondary'" size="small">
                                    {{ selectedProfile.is_global ? 'Global' : 'Personal' }}
                                </VaChip>
                            </div>
                            <p class="profile-description">
                                This profile ranks games based on
                                {{ selectedProfile.weights.length }}
                                criteria with custom weightings.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Games Library Section -->
        <div v-if="selectedProfileId" class="games-section">
            <GameLibrary :key="selectedProfileId" :searchable="false" :tagFilterable="false" :showHero="false"
                :apiEndpoint="rankedGamesEndpoint" title="Ranked Games"
                subtitle="Games ranked according to your selected profile" />
        </div>

        <!-- Empty state -->
        <div v-else-if="!profilesLoading && profiles.length === 0" class="empty-state">
            <div class="container">
                <div class="empty-content">
                    <font-awesome-icon icon="chart-line" class="empty-icon" />
                    <h2>No Ranking Profiles Available</h2>
                    <p>Create your first ranking profile to start ranking games according to your preferences.</p>
                    <VaButton @click="createNewProfile" preset="primary" class="create-empty-button">
                        <font-awesome-icon icon="plus" class="button-icon" />
                        Create Your First Profile
                    </VaButton>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.rank-games-page {
    min-height: 100vh;
    background-color: #f8f9fa;
}

.page-header {
    background: linear-gradient(135deg, #9423e0 0%, #4f1377 100%);
    padding: 3rem 0;
    color: white;
}

.container {
    max-width: var(--container-max-width);
    margin: 0 auto;
    padding: 0 var(--container-padding);
}

.page-title {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.title-icon {
    font-size: 2.5rem;
}

.page-subtitle {
    font-size: 1.2rem;
    opacity: 0.9;
    margin: 0;
    max-width: 600px;
}

.profile-section {
    padding: 2rem 0;
    background: white;
    border-bottom: 1px solid #e5e7eb;
}

.profile-controls {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.profile-selector {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.selector-label {
    font-size: 1.1rem;
    font-weight: 600;
    color: #374151;
}

.selector-group {
    display: flex;
    gap: 1rem;
    align-items: center;
    flex-wrap: wrap;
}

.profile-dropdown {
    min-width: 300px;
    flex: 1;
}

.edit-button,
.create-button {
    flex-shrink: 0;
    white-space: nowrap;
}

.button-icon {
    margin-right: 0.5rem;
}

.button-text {
    display: none;
}

.error-container {
    margin-top: 1rem;
}

.selected-profile-info {
    margin-top: 1rem;
}

.profile-info-card {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 0.75rem;
    padding: 1.5rem;
}

.profile-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.75rem;
}

.profile-name {
    font-size: 1.25rem;
    font-weight: 600;
    color: #374151;
    margin: 0;
}

.profile-description {
    color: #6b7280;
    margin: 0;
    line-height: 1.5;
}

.games-section {
    background: #f8f9fa;
}

.empty-state {
    padding: 4rem 0;
    text-align: center;
}

.empty-content {
    max-width: 500px;
    margin: 0 auto;
}

.empty-icon {
    font-size: 4rem;
    color: #9ca3af;
    margin-bottom: 1.5rem;
}

.empty-content h2 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 1rem;
}

.empty-content p {
    color: #6b7280;
    margin-bottom: 2rem;
    line-height: 1.6;
}

.create-empty-button {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

/* Responsive design */
@media (min-width: 640px) {
    .button-text {
        display: inline;
    }

    .selector-group {
        flex-wrap: nowrap;
    }
}

@media (min-width: 768px) {
    .profile-selector {
        flex-direction: row;
        align-items: center;
        gap: 1.5rem;
    }

    .selector-label {
        white-space: nowrap;
        margin-bottom: 0;
    }

    .selector-group {
        flex: 1;
    }
}

.title-link {
    color: white;
    text-decoration: underline;
}
</style>
