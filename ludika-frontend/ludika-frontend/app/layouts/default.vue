<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'

const { initializeAuth } = useAuth()

onMounted(() => {
  initializeAuth()
})
</script>

<template>
  <div class="app-layout">
    <VaAffix :offset-top="0">
      <VaNavbar class="app-navbar">
        <template #left>
          <div class="navbar-content">
            <VaNavbarItem class="navbar-item-padded">
              <NuxtLink to="/" class="navbar-brand">
                LUDIKA
              </NuxtLink>
            </VaNavbarItem>
          </div>
        </template>
        <template #right>
          <div class="navbar-content">
            <VaNavbarItem class="navbar-item-padded">
              <VaButton @click="navigateTo('/rank-games')" preset="secondary" class="rank-games-button">
                <font-awesome-icon icon="chart-line" class="button-icon" />
                <span class="button-text">Rank Games</span>
              </VaButton>
            </VaNavbarItem>

            <VaNavbarItem class="navbar-item-padded">
              <UserMenu />
            </VaNavbarItem>
          </div>
        </template>
      </VaNavbar>
    </VaAffix>
    <main class="app-main">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-navbar {
  flex-shrink: 0;
  border-bottom: 1px solid #e0e0e0;
  /* Remove default padding to control it ourselves */
  padding: 0 !important;
}

.navbar-container {
  max-width: var(--container-max-width);
  margin: 0 auto;
  padding: 0 var(--container-padding);
}

.navbar-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
}

.navbar-brand {
  font-size: 1.25rem;
  font-weight: 700;
  text-decoration: none;
  color: var(--va-primary);
}

.navbar-item-padded {
  padding: 0 16px;
  /* Horizontal padding */
}

.app-main {
  flex: 1;
}

.rank-games-button {
  flex-shrink: 0;
}

.button-icon {
  margin-right: 0.5rem;
}

.button-text {
  display: none;
}

/* Show text on larger screens */
@media (min-width: 640px) {
  .button-text {
    display: inline;
  }
}
</style>