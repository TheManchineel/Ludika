<script setup lang="ts">
import { useGames } from '../composables/useGames'

definePageMeta({
  layout: 'home'
})

const searchQuery = ref('')
const { games, loading, error, fetchGames } = useGames()

// Fetch games on page load
onMounted(() => {
  fetchGames()
})
</script>

<template>
  <div>
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">Ludika</h1>
        <p class="hero-subtitle">An ever–growing collection of educational games</p>
        <div class="search-container">
          <VaInput
            v-model="searchQuery"
            placeholder="Search for games..."
            class="search-input"
            prepend-inner="search"
            preset="solid"
            clearable
          />
        </div>
      </div>
    </div>

    <!-- Games Grid Section -->
    <div class="games-section">
      <div class="container">
        <div v-if="loading" class="loading-container">
          <VaProgressCircle indeterminate />
          <p>Loading games...</p>
        </div>
        
        <div v-else-if="error" class="error-container">
          <VaAlert color="danger" :title="error" />
        </div>
        
        <div v-else-if="games.length === 0" class="empty-container">
          <p>No games found.</p>
        </div>
        
        <div v-else class="games-grid">
          <GameCard
            v-for="game in games"
            :key="game.id"
            :game="game"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.hero-section {
  background: linear-gradient(135deg, #9423e0 0%, #4f1377 100%);
  min-height: 20vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.hero-content {
  text-align: center;
  max-width: 800px;
  width: 100%;
}

.hero-title {
  font-size: 4rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.hero-subtitle {
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2rem;
  font-weight: 400;
  line-height: 1.5;
}

.search-container {
  max-width: 500px;
  margin: 0 auto;
}

.search-input {
  width: 100%;
}

/* :deep(.va-input) {
  background: white;
  border-radius: 50px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
} */

:deep(.va-input__input) {
  font-size: 1.1rem;
  padding: 1rem 1.5rem;
}

:deep(.va-input__prepend-inner) {
  color: #666;
  margin-right: 0.5rem;
}

.games-section {
  padding: 3rem 0;
  background-color: #f8f9fa;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.loading-container,
.error-container,
.empty-container {
  text-align: center;
  padding: 3rem 0;
}

.loading-container p {
  margin-top: 1rem;
  color: #666;
}

.empty-container p {
  color: #666;
  font-size: 1.1rem;
}

.games-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem;
  padding: 1rem 0;
}
</style>
