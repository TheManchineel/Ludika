<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'
import { useUsers } from '~/composables/useUsers'

definePageMeta({
    layout: 'default'
})

const route = useRoute()
const { isAdmin, isContentModerator } = useAuth()
const { user, userLoading, userError, fetchUserById } = useUsers()

const userUuid = route.params.uuid as string

// Redirect if not privileged user
onMounted(() => {
    if (!isAdmin() && !isContentModerator()) {
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
            <p class="edit-user-subtitle">Modify user account information and permissions</p>
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
                        <VaAlert color="info" title="Coming Soon" closeable>
                            User editing functionality will be implemented in a future update.
                            For now, you can view user information and use the other admin tools.
                        </VaAlert>

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
                                        <VaListItemLabel caption>{{ user.user_role }}</VaListItemLabel>
                                    </VaListItemSection>
                                </VaListItem>

                                <VaListItem>
                                    <VaListItemSection>
                                        <VaListItemLabel>Status</VaListItemLabel>
                                        <VaListItemLabel caption>{{ user.enabled ? 'Active' : 'Disabled' }}
                                        </VaListItemLabel>
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

@media (max-width: 768px) {
    .actions {
        flex-direction: column;
    }
}
</style>