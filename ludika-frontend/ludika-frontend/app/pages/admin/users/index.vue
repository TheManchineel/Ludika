<script setup lang="ts">
import { useAuth, getUserRoleDisplayName } from '~/composables/useAuth'
import { useUsers } from '~/composables/useUsers'
import type { UserPublic } from '~~/types/auth'
import ConfirmationModal from '~/components/ConfirmationModal.vue'

definePageMeta({
    layout: 'default'
})

const { isAdmin, isContentModerator, user: currentUser } = useAuth()
const { users, loading, error, fetchUsers, deleteUser, deleteLoading } = useUsers()

// Redirect if not privileged user
onMounted(() => {
    if (!isAdmin() && !isContentModerator()) {
        navigateTo('/')
    } else {
        fetchUsers()
    }
})

const columns = [
    { key: 'visible_name', label: 'Name', sortable: true },
    { key: 'uuid', label: 'UUID', sortable: true },
    { key: 'user_role', label: 'Role', sortable: true },
    { key: 'enabled', label: 'Status', sortable: true },
    { key: 'created_at', label: 'Created', sortable: true },
    { key: 'last_login', label: 'Last Login', sortable: true },
    { key: 'actions', label: 'Actions', width: '120px' }
]

const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never'
    return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString()
}

const getStatusColor = (enabled: boolean) => {
    return enabled ? 'success' : 'danger'
}

const getStatusText = (enabled: boolean) => {
    return enabled ? 'Active' : 'Disabled'
}

const showConfirmDeleteModal = ref(false)
const userToDelete = ref<UserPublic | null>(null)

const confirmDelete = (user: UserPublic) => {
    userToDelete.value = user
    showConfirmDeleteModal.value = true
}

const handleDelete = async () => {
    if (userToDelete.value) {
        try {
            await deleteUser(userToDelete.value.uuid)
            showConfirmDeleteModal.value = false
            userToDelete.value = null
        } catch (error) {
            console.error('Failed to delete user:', error)
        }
    }
}



const canDeleteUser = (user: UserPublic) => {
    // Don't allow deletion of current user
    return currentUser.value?.uuid !== user.uuid
}

const getDropdownActions = (user: UserPublic) => {
    const actions = [
        {
            text: 'Edit Info',
            icon: 'edit',
            action: () => navigateTo(`/admin/users/${user.uuid}`)
        },
        {
            text: 'View Profile',
            icon: 'visibility',
            action: () => navigateTo(`/users/${user.uuid}`)
        }
    ]

    if (canDeleteUser(user)) {
        actions.push({
            text: 'Delete',
            icon: 'delete',
            action: () => confirmDelete(user)
        })
    }

    return actions
}
</script>

<template>
    <div class="users-container">
        <!-- Breadcrumb navigation -->
        <div class="breadcrumb-container">
            <VaBreadcrumbs>
                <VaBreadcrumbsItem to="/admin">Admin</VaBreadcrumbsItem>
                <VaBreadcrumbsItem to="/admin/users/">User Management</VaBreadcrumbsItem>
            </VaBreadcrumbs>
        </div>

        <!-- Header -->
        <div class="users-header">
            <h1 class="users-title">User Management</h1>
            <p class="users-subtitle">Manage user accounts and permissions</p>
        </div>

        <!-- Content -->
        <div class="users-content">
            <VaCard>
                <VaCardContent>
                    <div v-if="loading" class="loading-container">
                        <VaProgressCircle indeterminate />
                        <p>Loading users...</p>
                    </div>

                    <div v-else-if="error" class="error-container">
                        <VaAlert color="danger" :title="error" />
                    </div>

                    <div v-else>
                        <VaDataTable :items="users" :columns="columns" :loading="loading" striped hoverable>
                            <template #cell(user_role)="{ rowData }">
                                <VaBadge :text="getUserRoleDisplayName(rowData.user_role)" :color="rowData.user_role === 'platform_administrator' ? 'danger' :
                                    rowData.user_role === 'content_moderator' ? 'warning' : 'primary'" />
                            </template>

                            <template #cell(enabled)="{ rowData }">
                                <VaBadge :text="getStatusText(rowData.enabled)"
                                    :color="getStatusColor(rowData.enabled)" />
                            </template>

                            <template #cell(created_at)="{ rowData }">
                                {{ formatDateTime(rowData.created_at) }}
                            </template>

                            <template #cell(last_login)="{ rowData }">
                                {{ formatDate(rowData.last_login) }}
                            </template>

                            <template #cell(actions)="{ rowData }">
                                <VaDropdown placement="bottom-end">
                                    <template #anchor>
                                        <VaButton preset="secondary" icon="more_vert" size="small"
                                            :loading="deleteLoading" />
                                    </template>

                                    <VaDropdownContent>
                                        <VaList>
                                            <VaListItem v-for="action in getDropdownActions(rowData)" :key="action.text"
                                                @click="action.action" class="dropdown-item">
                                                <VaListItemSection avatar>
                                                    <VaIcon :name="action.icon" />
                                                </VaListItemSection>
                                                <VaListItemSection>
                                                    <VaListItemLabel>{{ action.text }}</VaListItemLabel>
                                                </VaListItemSection>
                                            </VaListItem>
                                        </VaList>
                                    </VaDropdownContent>
                                </VaDropdown>
                            </template>
                        </VaDataTable>
                    </div>
                </VaCardContent>
            </VaCard>
        </div>

        <!-- Delete confirmation modal -->
        <ConfirmationModal v-model="showConfirmDeleteModal" title="Confirm User Deletion"
            :message="`Are you sure you want to delete the user ${userToDelete?.visible_name}?`"
            warning-message="This action cannot be undone." confirm-text="Delete User" confirm-color="danger"
            :loading="deleteLoading" @confirm="handleDelete"
            @cancel="showConfirmDeleteModal = false; userToDelete = null" />
    </div>
</template>

<style scoped>
.users-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 1rem;
}

.breadcrumb-container {
    margin-bottom: 1rem;
    padding: 1rem;
    background-color: #f8f9fa;
    border-radius: 0.5rem;
}

.users-header {
    text-align: center;
    margin-bottom: 2rem;
}

.users-title {
    font-size: 2rem;
    font-weight: 600;
    color: #333;
    margin-bottom: 0.5rem;
}

.users-subtitle {
    font-size: 1.1rem;
    color: #666;
    margin: 0;
}

.users-content {
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

.dropdown-item {
    cursor: pointer;
}

.dropdown-item:hover {
    background-color: #f5f5f5;
}

.text-danger {
    color: #dc3545;
    font-weight: 500;
}
</style>