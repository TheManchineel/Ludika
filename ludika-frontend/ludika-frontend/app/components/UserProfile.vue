<script setup lang="ts">
import type { UserPublic } from '~~/types/auth'
import { getUserRoleDisplayName } from '~/composables/useAuth'

interface Props {
    user: UserPublic | null
    loading?: boolean
    error?: string | null
    showBackButton?: boolean
}

const props = withDefaults(defineProps<Props>(), {
    loading: false,
    error: null,
    showBackButton: true
})

const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    })
}

const getStatusColor = (enabled: boolean) => {
    return enabled ? 'success' : 'danger'
}

const getStatusText = (enabled: boolean) => {
    return enabled ? 'Active' : 'Inactive'
}

const getRoleColor = (role: string) => {
    switch (role) {
        case 'platform_administrator': return 'danger'
        case 'content_moderator': return 'warning'
        default: return 'primary'
    }
}
</script>

<template>
    <div class="user-profile-container">
        <!-- Loading state -->
        <div v-if="loading" class="loading-container">
            <VaProgressCircle indeterminate />
            <p>Loading user profile...</p>
        </div>

        <!-- Error state -->
        <div v-else-if="error" class="error-container">
            <VaAlert color="danger" :title="error" />
            <VaButton v-if="showBackButton" to="/" preset="secondary">
                Return to Homepage
            </VaButton>
        </div>

        <!-- User profile content -->
        <div v-else-if="user" class="profile-content">
            <VaCard class="profile-card">
                <VaCardContent>
                    <!-- Header section -->
                    <div class="profile-header">
                        <div class="avatar-section">
                            <UserAvatar :name="user.visible_name" size="80px" />
                        </div>
                        <div class="info-section">
                            <h1 class="user-name">{{ user.visible_name }}</h1>
                            <div class="user-badges">
                                <VaBadge :text="getUserRoleDisplayName(user.user_role)"
                                    :color="getRoleColor(user.user_role)" class="role-badge" />
                                <VaBadge :text="getStatusText(user.enabled)" :color="getStatusColor(user.enabled)"
                                    class="status-badge" />
                            </div>
                        </div>
                    </div>

                    <VaDivider />

                    <!-- Details section -->
                    <div class="profile-details">
                        <h2 class="section-title">Profile Information</h2>

                        <div class="details-grid">
                            <div class="detail-item">
                                <VaIcon name="person" class="detail-icon" />
                                <div class="detail-content">
                                    <span class="detail-label">Display Name</span>
                                    <span class="detail-value">{{ user.visible_name }}</span>
                                </div>
                            </div>

                            <div class="detail-item">
                                <VaIcon name="admin_panel_settings" class="detail-icon" />
                                <div class="detail-content">
                                    <span class="detail-label">Role</span>
                                    <span class="detail-value">{{ getUserRoleDisplayName(user.user_role) }}</span>
                                </div>
                            </div>

                            <div class="detail-item">
                                <VaIcon name="schedule" class="detail-icon" />
                                <div class="detail-content">
                                    <span class="detail-label">Member Since</span>
                                    <span class="detail-value">{{ formatDate(user.created_at) }}</span>
                                </div>
                            </div>

                            <div class="detail-item">
                                <VaIcon name="login" class="detail-icon" />
                                <div class="detail-content">
                                    <span class="detail-label">Last Seen</span>
                                    <span class="detail-value">
                                        {{ user.last_login ? formatDate(user.last_login) : 'Never' }}
                                    </span>
                                </div>
                            </div>

                            <div class="detail-item">
                                <VaIcon name="fingerprint" class="detail-icon" />
                                <div class="detail-content">
                                    <span class="detail-label">User ID</span>
                                    <span class="detail-value">{{ user.uuid }}</span>
                                </div>
                            </div>

                            <div class="detail-item">
                                <VaIcon name="toggle_on" class="detail-icon" />
                                <div class="detail-content">
                                    <span class="detail-label">Account Status</span>
                                    <span class="detail-value">{{ getStatusText(user.enabled) }}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Actions -->
                    <div v-if="showBackButton" class="profile-actions">
                        <VaButton to="/" preset="secondary">
                            <VaIcon name="home" left />
                            Back to Homepage
                        </VaButton>
                    </div>

                    <slot name="actions" />
                </VaCardContent>
            </VaCard>
        </div>
    </div>
</template>

<style scoped>
.user-profile-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
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

.profile-content {
    width: 100%;
}

.profile-card {
    width: 100%;
}

.profile-header {
    display: flex;
    align-items: center;
    gap: 2rem;
    margin-bottom: 2rem;
}

.avatar-section {
    flex-shrink: 0;
}

.info-section {
    flex: 1;
}

.user-name {
    font-size: 2rem;
    font-weight: 600;
    color: #333;
    margin-bottom: 1rem;
}

.user-badges {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.role-badge,
.status-badge {
    font-weight: 500;
}

.section-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #333;
    margin-bottom: 1.5rem;
}

.details-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.detail-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background-color: #f8f9fa;
    border-radius: 0.5rem;
}

.detail-icon {
    color: #666;
    flex-shrink: 0;
}

.detail-content {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    min-width: 0;
}

.detail-label {
    font-size: 0.875rem;
    color: #666;
    font-weight: 500;
}

.detail-value {
    font-size: 1rem;
    color: #333;
    word-break: break-all;
}

.profile-actions {
    display: flex;
    justify-content: center;
    margin-top: 2rem;
}

@media (max-width: 768px) {
    .profile-header {
        flex-direction: column;
        text-align: center;
    }

    .details-grid {
        grid-template-columns: 1fr;
    }

    .user-profile-container {
        padding: 1rem;
    }
}
</style>