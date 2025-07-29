<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'

const { user, isAuthenticated, logout, isAdmin } = useAuth()

const handleLogout = () => {
  logout()
  navigateTo('/')
}
</script>

<template>
  <div class="user-menu">
    <VaDropdown v-if="isAuthenticated && user" placement="bottom-end">
      <template #anchor>
        <VaButton preset="secondary" icon="person" :text="user.visible_name" class="user-button" />
      </template>

      <VaDropdownContent class="user-dropdown">
        <div class="user-info">
          <div class="user-name">{{ user.visible_name }}</div>
          <div class="user-role">{{ user.user_role.replace('_', ' ') }}</div>
        </div>

        <VaDivider />

        <VaList>
          <VaListItem v-if="isAdmin()" clickable @click="navigateTo('/admin')">
            <VaListItemSection avatar>
              <VaIcon name="admin_panel_settings" />
            </VaListItemSection>
            <VaListItemSection>
              <VaListItemLabel>Admin Panel</VaListItemLabel>
            </VaListItemSection>
          </VaListItem>

          <VaListItem clickable @click="navigateTo('/profile')">
            <VaListItemSection avatar>
              <VaIcon name="account_circle" />
            </VaListItemSection>
            <VaListItemSection>
              <VaListItemLabel>Profile</VaListItemLabel>
            </VaListItemSection>
          </VaListItem>

          <VaListItem clickable @click="handleLogout">
            <VaListItemSection avatar>
              <VaIcon name="logout" />
            </VaListItemSection>
            <VaListItemSection>
              <VaListItemLabel>Sign Out</VaListItemLabel>
            </VaListItemSection>
          </VaListItem>
        </VaList>
      </VaDropdownContent>
    </VaDropdown>

    <VaButton v-else @click="navigateTo('/login')" icon="login" class="login-button">
      <span class="login-text">Sign In</span>
    </VaButton>
  </div>
</template>

<style scoped>
.user-menu {
  display: flex;
  align-items: center;
}

.user-button {
  text-transform: none;
}

.user-dropdown {
  min-width: 200px;
}

.user-info {
  padding: 1rem;
  text-align: center;
}

.user-name {
  font-weight: 600;
  color: #333;
}

.user-role {
  font-size: 0.875rem;
  color: #666;
  text-transform: capitalize;
}

.login-button {
  flex-shrink: 0;
}

.login-text {
  display: none;
}

/* Show text on larger screens */
@media (min-width: 640px) {
  .login-text {
    display: inline;
    margin-left: 0.5rem;
  }
}
</style>