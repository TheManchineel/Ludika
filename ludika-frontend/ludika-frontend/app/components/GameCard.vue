<script setup lang="ts">
import type { GamePublic } from '~~/types/game'

interface Props {
  game: GamePublic
}

const props = defineProps<Props>()

const firstImage = computed(() => {
  return props.game.images.length > 0 ? props.game.images[0] : null
})

const imageUrl = computed(() => {
  if (!firstImage.value) return null
  return `/static/${firstImage.value.image}`
})

const formattedScore = computed(() => {
  if (props.game.total_score === undefined) return null
  return `Score: ${props.game.total_score.toFixed(2)}`
})
</script>

<template>
  <NuxtLink :to="`/games/${game.id}`" class="game-card-link">
    <VaCard class="game-card">
      <div class="game-image-container">
        <div v-if="imageUrl" class="game-image">
          <NuxtImg :src="imageUrl" :alt="game.name" class="game-image-img" loading="lazy" />
          <div v-if="formattedScore" class="score-overlay">
            {{ formattedScore }}
          </div>
        </div>
        <div v-else class="game-image-placeholder">
          <VaIcon name="image" size="large" />
          <div v-if="formattedScore" class="score-overlay">
            {{ formattedScore }}
          </div>
        </div>
      </div>

      <div class="game-content">
        <h3 class="game-title">{{ game.name }}</h3>

        <GameTags :tags="game.tags" :limit="5" size="small" class="game-card-tags" />
      </div>
    </VaCard>
  </NuxtLink>
</template>

<style scoped>
.game-card-link {
  display: block;
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.game-card-link:hover {
  transform: translateY(-2px);
}

.game-card-link:hover .game-card {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.game-card {
  height: 320px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow 0.2s ease;
}

.game-image-container {
  flex: 1;
  min-height: 0;
  position: relative;
}

.game-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
}

.game-image-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.game-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  color: #999;
}

.game-content {
  padding: 1rem;
  flex-shrink: 0;
}

.game-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 0.75rem 0;
  color: #333;
  line-height: 1.3;
}

.game-card-tags {
  min-height: 2.5rem;
}

.score-overlay {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background-color: var(--va-info);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  z-index: 10;
}
</style>