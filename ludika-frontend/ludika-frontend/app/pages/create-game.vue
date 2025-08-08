<template>
    <div class="create-game-page">
        <div class="create-game-content">
            <!-- Game creation form -->
            <GameFormEditor :is-editing="false" @success="handleSuccess" @cancel="handleCancel" />
        </div>
    </div>
</template>

<script setup lang="ts">
import type { GamePublic } from '~~/types/game'
import { useAuth } from '~/composables/useAuth'
import GameFormEditor from '~/components/GameFormEditor.vue'

const { isAuthenticated } = useAuth()

useHead({
    title: 'Create New Game - Ludika'
})

const handleSuccess = (createdGame: GamePublic) => {
    navigateTo(`/games/${createdGame.id}`)
}

const handleCancel = () => {
    navigateTo('/')
}

watch(isAuthenticated, (authenticated) => {
    if (!authenticated) {
        navigateTo('/login')
    }
}, { immediate: true })
</script>

<style scoped>
.create-game-page {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
    min-height: calc(100vh - 4rem);
}

.create-game-content {
    padding: 0 1rem;
}

@media (max-width: 768px) {
    .create-game-page {
        padding: 1rem;
    }

    .create-game-content {
        padding: 0;
    }
}
</style>