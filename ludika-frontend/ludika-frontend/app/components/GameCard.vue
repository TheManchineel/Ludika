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

const displayTags = computed(() => {
  return props.game.tags.slice(0, 5)
})
</script>

<template>
  <VaCard class="game-card">
    <div class="game-image-container">
      <VaAspectRatio :ratio="4/3">
        <div v-if="imageUrl" class="game-image">
          <img :src="imageUrl" :alt="game.name" >
        </div>
        <div v-else class="game-image-placeholder">
          <VaIcon name="image" size="large" />
        </div>
      </VaAspectRatio>
    </div>
    
    <div class="game-content">
      <h3 class="game-title">{{ game.name }}</h3>
      
      <div class="game-tags">
        <VaChip
          v-for="tag in displayTags"
          :key="tag.id"
          :color="'primary'"
          size="small"
          class="game-tag"
        >
          {{ tag.name }}
        </VaChip>
      </div>
    </div>
  </VaCard>
</template>

<style scoped>
.game-card {
  height: 320px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.game-image-container {
  flex: 1;
  min-height: 0;
}

.game-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
}

.game-image img {
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

.game-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  min-height: 2.5rem;
  align-items: flex-start;
}

.game-tag {
  font-size: 0.75rem;
}
</style> 