<script setup lang="ts">
import { useAuth, getUserRoleDisplayName } from '~/composables/useAuth'

const { user, isAuthenticated, logout, isPrivileged } = useAuth()

const handleLogout = () => {
  logout()
  navigateTo('/')
}
</script>

<template>
  <div class="user-menu">
    <VaDropdown v-if="isAuthenticated && user" placement="bottom-end">
      <template #anchor>
        <VaButton preset="secondary" :text="user.visible_name" class="user-button">
          <UserAvatar :name="user.visible_name" size="small" class="button-avatar" />
        </VaButton>
      </template>

      <VaDropdownContent class="user-dropdown">
        <div class="user-info">
          <UserAvatar :name="user.visible_name" size="medium" class="dropdown-avatar" />
          <div class="user-name">{{ user.visible_name }}</div>
          <div class="user-role">{{ getUserRoleDisplayName(user.user_role) }}</div>
        </div>

        <VaDivider />

        <VaList>
          <VaListItem clickable @click="navigateTo('/create-game')">
            <VaListItemSection avatar>
              <font-awesome-icon icon="plus-circle" />
            </VaListItemSection>
            <VaListItemSection>
              <VaListItemLabel>Create Game</VaListItemLabel>
            </VaListItemSection>
          </VaListItem>

          <VaListItem clickable @click="navigateTo('/my-games')">
            <VaListItemSection avatar>
              <font-awesome-icon icon="gamepad" />
            </VaListItemSection>
            <VaListItemSection>
              <VaListItemLabel>My Games</VaListItemLabel>
            </VaListItemSection>
          </VaListItem>

          <VaListItem v-if="isPrivileged()" clickable @click="navigateTo('/admin')">
            <VaListItemSection avatar>
              <font-awesome-icon icon="cog" />
            </VaListItemSection>
            <VaListItemSection>
              <VaListItemLabel>Admin Panel</VaListItemLabel>
            </VaListItemSection>
          </VaListItem>

          <VaListItem v-if="isPrivileged()" clickable @click="navigateTo('/create-game-ai')">
            <VaListItemSection avatar>
              <font-awesome-icon icon="hand-sparkles" />
            </VaListItemSection>
            <VaListItemSection>
              <VaListItemLabel>Create Games with AI</VaListItemLabel>
            </VaListItemSection>
          </VaListItem>

          <VaListItem clickable @click="navigateTo('/profile')">
            <VaListItemSection avatar>
              <font-awesome-icon icon="user-circle" />
            </VaListItemSection>
            <VaListItemSection>
              <VaListItemLabel>Profile</VaListItemLabel>
            </VaListItemSection>
          </VaListItem>

          <VaListItem clickable @click="handleLogout">
            <VaListItemSection avatar>
              <font-awesome-icon icon="sign-out-alt" />
            </VaListItemSection>
            <VaListItemSection>
              <VaListItemLabel>Sign Out</VaListItemLabel>
            </VaListItemSection>
          </VaListItem>
        </VaList>
      </VaDropdownContent>
    </VaDropdown>

    <VaButton v-else @click="navigateTo('/login')" class="login-button">
      <font-awesome-icon icon="sign-in-alt" class="button-icon" />
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
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.dropdown-avatar {
  margin-bottom: 0.25rem;
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

.button-avatar {
  margin-right: 0.5rem;
}

.login-button {
  flex-shrink: 0;
}



.login-text {
  display: none;
}

@media (min-width: 640px) {
  .login-text {
    display: inline;
  }
}
</style>