<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'
import { useUsers } from '~/composables/useUsers'

definePageMeta({
    layout: 'default'
})

const route = useRoute()
const { isAdmin, isContentModerator, user: currentUser } = useAuth()
const { user, userLoading, userError, fetchUserById, updateUser } = useUsers()

const userUuid = route.params.uuid as string

// Check if viewing current user
const isCurrentUser = computed(() => {
    return currentUser.value?.uuid === userUuid
})

// Role options for dropdown - using the enum directly from the import
const roleOptions = [
    { value: 'user', text: 'User' },
    { value: 'content_moderator', text: 'Content Moderator' },
    { value: 'platform_administrator', text: 'Platform Administrator' }
]

// Handle role change
const handleRoleChange = async (newRole: string) => {
    if (!user.value || isCurrentUser.value) return

    try {
        await updateUser(userUuid, { user_role: newRole })
    } catch (error) {
        console.error('Failed to update user role:', error)
        // Could add toast notification here
    }
}

// Handle enabled/disabled toggle
const handleEnabledChange = async (enabled: boolean) => {
    if (!user.value || isCurrentUser.value) return

    try {
        await updateUser(userUuid, { enabled })
    } catch (error) {
        console.error('Failed to update user status:', error)
        // Could add toast notification here
    }
}

// Redirect if not privileged user
onMounted(() => {
    if (!isAdmin()) {
        navigateTo('/')
    } else {
        fetchUserById(userUuid)
    }
})
</script>

<template>
    <div class="edit-user-container">
        <!-- Breadcrumb navigation -->
        <div class="breadcrumb-container">
            <VaBreadcrumbs>
                <VaBreadcrumbsItem to="/admin">Admin</VaBreadcrumbsItem>
                <VaBreadcrumbsItem to="/admin/users/">User Management</VaBreadcrumbsItem>
                <VaBreadcrumbsItem :to="`/admin/users/${userUuid}`">Edit User</VaBreadcrumbsItem>
            </VaBreadcrumbs>
        </div>

        <!-- Header -->
        <div class="edit-user-header">
            <h1 class="edit-user-title">Edit User</h1>
            <p class="edit-user-subtitle">Modify user account status and permissions</p>
        </div>

        <!-- Content -->
        <div class="edit-user-content">
            <div v-if="userLoading" class="loading-container">
                <VaProgressCircle indeterminate />
                <p>Loading user information...</p>
            </div>

            <div v-else-if="userError" class="error-container">
                <VaAlert color="danger" :title="userError" />
                <VaButton to="/admin/users/">
                    Back to User Management
                </VaButton>
            </div>

            <div v-else-if="user" class="form-container">
                <VaCard>
                    <VaCardTitle>
                        Editing: {{ user.visible_name }}
                    </VaCardTitle>
                    <VaCardContent>
                        <div class="user-info">
                            <h3>Current User Information</h3>
                            <VaList>
                                <VaListItem>
                                    <VaListItemSection>
                                        <VaListItemLabel>Name</VaListItemLabel>
                                        <VaListItemLabel caption>{{ user.visible_name }}</VaListItemLabel>
                                    </VaListItemSection>
                                </VaListItem>

                                <VaListItem>
                                    <VaListItemSection>
                                        <VaListItemLabel>UUID</VaListItemLabel>
                                        <VaListItemLabel caption>{{ user.uuid }}</VaListItemLabel>
                                    </VaListItemSection>
                                </VaListItem>

                                <VaListItem>
                                    <VaListItemSection>
                                        <VaListItemLabel>Role</VaListItemLabel>
                                        <VaSelect v-model="user.user_role" :options="roleOptions"
                                            :disabled="isCurrentUser" @update:model-value="handleRoleChange"
                                            value-by="value" text-by="text" class="role-select" />
                                    </VaListItemSection>
                                </VaListItem>

                                <VaListItem>
                                    <VaListItemSection>
                                        <VaListItemLabel>Status</VaListItemLabel>
                                        <VaSwitch v-model="user.enabled" :disabled="isCurrentUser"
                                            @update:model-value="handleEnabledChange"
                                            :label="user.enabled ? 'Active' : 'Disabled'" class="status-switch" />
                                    </VaListItemSection>
                                </VaListItem>

                                <VaListItem>
                                    <VaListItemSection>
                                        <VaListItemLabel>Created</VaListItemLabel>
                                        <VaListItemLabel caption>{{ new Date(user.created_at).toLocaleString() }}
                                        </VaListItemLabel>
                                    </VaListItemSection>
                                </VaListItem>

                                <VaListItem>
                                    <VaListItemSection>
                                        <VaListItemLabel>Last Login</VaListItemLabel>
                                        <VaListItemLabel caption>{{ user.last_login ? new
                                            Date(user.last_login).toLocaleString() : 'Never' }}</VaListItemLabel>
                                    </VaListItemSection>
                                </VaListItem>
                            </VaList>
                        </div>

                        <div class="actions">
                            <VaButton to="/admin/users/" preset="secondary">
                                Back to User Management
                            </VaButton>
                            <VaButton :to="`/users/${user.uuid}`" color="primary">
                                View Public Profile
                            </VaButton>
                        </div>
                    </VaCardContent>
                </VaCard>
            </div>
        </div>
    </div>
</template>

<style scoped>
.edit-user-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 1rem;
}

.breadcrumb-container {
    margin-bottom: 1rem;
    padding: 1rem;
    background-color: #f8f9fa;
    border-radius: 0.5rem;
}

.edit-user-header {
    text-align: center;
    margin-bottom: 2rem;
}

.edit-user-title {
    font-size: 2rem;
    font-weight: 600;
    color: #333;
    margin-bottom: 0.5rem;
}

.edit-user-subtitle {
    font-size: 1.1rem;
    color: #666;
    margin: 0;
}

.edit-user-content {
    width: 100%;
}

.loading-container,
.error-container {
    text-align: center;
    padding: 3rem 0;
}

.loading-container p {
    margin-top: 1rem;
    color: #666;
}

.form-container {
    width: 100%;
}

.user-info {
    margin: 2rem 0;
}

.user-info h3 {
    margin-bottom: 1rem;
    color: #333;
}

.actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    margin-top: 2rem;
}

.role-select {
    margin-top: 0.5rem;
    max-width: 300px;
}

.status-switch {
    margin-top: 0.5rem;
}

@media (max-width: 768px) {
    .actions {
        flex-direction: column;
    }
}
</style>