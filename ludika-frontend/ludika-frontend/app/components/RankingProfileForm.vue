<template>
    <div class="ranking-profile-form">
        <!-- Loading State -->
        <div v-if="loading || criteriaLoading" class="loading-state">
            <VaProgressCircle indeterminate color="primary" />
            <div class="loading-text">{{ loading ? 'Loading profile data...' : 'Loading criteria...' }}</div>
        </div>

        <!-- Error State -->
        <div v-else-if="error || criteriaError" class="error-state">
            <VaAlert color="danger" :title="error || criteriaError" />
        </div>

        <!-- Profile Form -->
        <form v-else @submit.prevent="handleSubmit" class="profile-form">
            <!-- Profile Name Section -->
            <div class="form-section">
                <label for="profileName" class="form-label">
                    <font-awesome-icon icon="tag" class="label-icon" />
                    Profile Name
                </label>
                <VaInput id="profileName" v-model="profileName"
                    placeholder="Enter a descriptive name for this ranking profile..." class="profile-name-input"
                    :error="!!nameError" :error-messages="nameError ? [nameError] : []" required />
            </div>

            <!-- Global Toggle Section (Only for privileged users) -->
            <div v-if="isPrivileged()" class="form-section">
                <div class="toggle-section">
                    <div class="toggle-info">
                        <label class="form-label">
                            <font-awesome-icon icon="globe" class="label-icon" />
                            Global Profile
                        </label>
                        <p class="toggle-description">
                            Global profiles are visible to all users and can be used by anyone for ranking games.
                        </p>
                    </div>
                    <VaSwitch v-model="isGlobal" :label="isGlobal ? 'Global' : 'Personal'" class="global-switch" />
                </div>
            </div>

            <!-- Weights Section -->
            <div class="form-section">
                <div class="section-header">
                    <div class="section-label">
                        <font-awesome-icon icon="balance-scale" class="label-icon" />
                        Criterion Weights
                    </div>
                    <div class="section-subtitle">Define how much each criterion matters in your ranking</div>
                </div>

                <div class="weights-grid">
                    <!-- Existing Weight Cards -->
                    <WeightCriterionCard v-for="weight in selectedWeights" :key="weight.criterion.id"
                        :criterion="weight.criterion" v-model="weight.weight"
                        @remove="removeCriterion(weight.criterion.id)" />

                    <!-- Add Weight Card -->
                    <AddWeightCard :available-criteria="availableCriteria" @select="addCriterion" />
                </div>

                <div v-if="weightsError" class="weights-error">
                    <VaAlert color="danger" :title="weightsError" />
                </div>
            </div>

            <div class="form-actions">
                <VaButton @click="navigateTo('/rank-games')" preset="secondary" class="cancel-button">
                    Cancel
                </VaButton>

                <VaButton v-if="isEditMode && profileId" @click="showDeleteModal = true" color="danger"
                    preset="secondary" class="delete-button">
                    <font-awesome-icon icon="trash" class="button-icon" />
                    Delete Profile
                </VaButton>

                <VaButton type="submit" :loading="submitLoading" :disabled="!isFormValid" class="submit-button">
                    <font-awesome-icon :icon="isEditMode ? 'save' : 'plus'" class="button-icon" />
                    {{ isEditMode ? 'Save Changes' : 'Create Profile' }}
                </VaButton>
            </div>
        </form>

        <!-- Delete Confirmation Modal -->
        <ConfirmationModal v-model="showDeleteModal" title="Delete Ranking Profile"
            :message="`Are you sure you want to delete the profile '${profileName}'? This action cannot be undone.`"
            confirm-text="Delete" confirm-color="danger" @confirm="handleDelete" @cancel="showDeleteModal = false" />
    </div>
</template>

<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'
import WeightCriterionCard from './WeightCriterionCard.vue'
import AddWeightCard from './AddWeightCard.vue'
import ConfirmationModal from './ConfirmationModal.vue'
import type { ReviewCriterion } from '../../types/game'

interface Props {
    profileId?: number | string
    mode: 'create' | 'edit'
}

interface ProfileWeight {
    criterion: ReviewCriterion
    weight: number
}

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

const props = defineProps<Props>()
const router = useRouter()
const { authenticatedFetch, isPrivileged } = useAuth()

// State
const loading = ref(false)
const criteriaLoading = ref(false)
const submitLoading = ref(false)
const error = ref<string | null>(null)
const criteriaError = ref<string | null>(null)
const nameError = ref<string | null>(null)
const weightsError = ref<string | null>(null)

const profileName = ref('')
const isGlobal = ref(false)
const selectedWeights = ref<ProfileWeight[]>([])
const criteria = ref<ReviewCriterion[]>([])
const showDeleteModal = ref(false)

// Computed properties
const isEditMode = computed(() => props.mode === 'edit')

const availableCriteria = computed(() => {
    const usedCriteriaIds = selectedWeights.value.map(w => w.criterion.id)
    return criteria.value.filter(criterion => !usedCriteriaIds.includes(criterion.id))
})

const isFormValid = computed(() => {
    return profileName.value.trim().length > 0 && selectedWeights.value.length > 0
})

// Methods
const fetchCriteria = async () => {
    criteriaLoading.value = true
    criteriaError.value = null

    try {
        const response = await authenticatedFetch<ReviewCriterion[]>('/api/v1/reviews/criteria')
        criteria.value = response
    } catch (err) {
        console.error('Error fetching criteria:', err)
        criteriaError.value = 'Failed to load criteria'
    } finally {
        criteriaLoading.value = false
    }
}

const fetchProfile = async () => {
    if (!isEditMode.value || !props.profileId) return

    loading.value = true
    error.value = null

    try {
        const response = await authenticatedFetch<RankingProfile>(`/api/v1/reviews/profiles/${props.profileId}`)

        profileName.value = response.name
        isGlobal.value = response.is_global

        // Map weights to criteria
        selectedWeights.value = response.weights.map(weight => {
            const criterion = criteria.value.find(c => c.id === weight.criterion_id)
            if (!criterion) {
                throw new Error(`Criterion with ID ${weight.criterion_id} not found`)
            }
            return {
                criterion,
                weight: weight.weight
            }
        })
    } catch (err) {
        console.error('Error fetching profile:', err)
        error.value = 'Failed to load profile data'
    } finally {
        loading.value = false
    }
}

const addCriterion = (criterion: ReviewCriterion) => {
    selectedWeights.value.push({
        criterion,
        weight: 0.5 // Default weight
    })
}

const removeCriterion = (criterionId: number) => {
    const index = selectedWeights.value.findIndex(w => w.criterion.id === criterionId)
    if (index !== -1) {
        selectedWeights.value.splice(index, 1)
    }
}

const validateForm = () => {
    nameError.value = null
    weightsError.value = null

    if (profileName.value.trim().length === 0) {
        nameError.value = 'Profile name is required'
        return false
    }

    if (selectedWeights.value.length === 0) {
        weightsError.value = 'At least one criterion weight is required'
        return false
    }

    return true
}

const handleSubmit = async () => {
    if (!validateForm()) return

    submitLoading.value = true
    error.value = null

    try {
        const profileData = {
            name: profileName.value.trim(),
            is_global: isGlobal.value,
            weights: selectedWeights.value.map(weight => ({
                criterion_id: weight.criterion.id,
                weight: weight.weight
            }))
        }

        if (isEditMode.value) {
            await authenticatedFetch(`/api/v1/reviews/profiles/${props.profileId}`, {
                method: 'PATCH',
                body: JSON.stringify(profileData),
                headers: {
                    'Content-Type': 'application/json'
                }
            })
        } else {
            await authenticatedFetch('/api/v1/reviews/profiles', {
                method: 'POST',
                body: JSON.stringify(profileData),
                headers: {
                    'Content-Type': 'application/json'
                }
            })
        }

        navigateTo('/rank-games')
    } catch (err) {
        console.error(`Failed to ${isEditMode.value ? 'update' : 'create'} profile:`, err)
        error.value = `Failed to ${isEditMode.value ? 'update' : 'create'} profile`
    } finally {
        submitLoading.value = false
    }
}

const handleDelete = async () => {
    if (!isEditMode.value || !props.profileId) return

    try {
        await authenticatedFetch(`/api/v1/reviews/profiles/${props.profileId}`, {
            method: 'DELETE'
        })

        navigateTo('/rank-games')
    } catch (err) {
        console.error('Failed to delete profile:', err)
        error.value = 'Failed to delete profile'
    }

    showDeleteModal.value = false
}

// Lifecycle
onMounted(async () => {
    await fetchCriteria()

    if (isEditMode.value) {
        await fetchProfile()
    }
})
</script>

<style scoped>
.ranking-profile-form {
    max-width: 800px;
    margin: 0 auto;
    padding: 1rem;
}

.loading-state,
.error-state {
    text-align: center;
    padding: 3rem 0;
}

.loading-text {
    margin-top: 1rem;
    color: #666;
    font-size: 1rem;
}

.profile-form {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.form-section {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.form-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.1rem;
    font-weight: 600;
    color: #374151;
}

.label-icon {
    color: var(--va-primary);
}

.profile-name-input {
    width: 100%;
}

.toggle-section {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 1.5rem;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 0.75rem;
}

.toggle-info {
    flex: 1;
    margin-right: 1rem;
}

.toggle-description {
    font-size: 0.875rem;
    color: #6b7280;
    margin: 0.5rem 0 0 0;
    line-height: 1.4;
}

.global-switch {
    flex-shrink: 0;
}

.section-header {
    margin-bottom: 1rem;
}

.section-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.1rem;
    font-weight: 600;
    color: #374151;
}

.section-subtitle {
    font-size: 0.875rem;
    color: #6b7280;
    margin-top: 0.25rem;
}

.weights-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
}

.weights-error {
    margin-top: 1rem;
}

.form-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid #e5e7eb;
}

.button-icon {
    margin-right: 0.5rem;
}

.cancel-button {
    margin-right: auto;
}

@media (max-width: 768px) {
    .ranking-profile-form {
        padding: 0.5rem;
    }

    .toggle-section {
        flex-direction: column;
        gap: 1rem;
        align-items: stretch;
    }

    .toggle-info {
        margin-right: 0;
    }

    .weights-grid {
        grid-template-columns: 1fr;
    }

    .form-actions {
        flex-direction: column;
        align-items: stretch;
    }

    .cancel-button {
        margin-right: 0;
        order: 3;
    }
}
</style>