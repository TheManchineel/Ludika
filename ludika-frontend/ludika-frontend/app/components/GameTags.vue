        <script setup lang="ts">
        import type { TagPublic } from '~~/types/game'

        interface Props {
            tags: readonly TagPublic[]
            limit?: number
            size?: 'small' | 'medium' | 'large'
        }

        const props = withDefaults(defineProps<Props>(), {
            limit: undefined,
            size: 'small'
        })

        const displayTags = computed(() => {
            if (props.limit !== undefined) {
                return props.tags.slice(0, props.limit)
            }
            return props.tags
        })
</script>

<template>
    <div class="game-tags">
        <VaChip v-for="tag in displayTags" :key="tag.id" :color="'primary'" :size="size" class="game-tag">
            <div class="tag-content">
                <font-awesome-icon v-if="tag.icon" :icon="tag.icon" class="tag-icon" />
                <span class="tag-name">{{ tag.name }}</span>
            </div>
        </VaChip>
    </div>
</template>

<style scoped>
.game-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: flex-start;
}

.game-tag {
    font-size: 0.75rem;
}

.tag-content {
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.tag-icon {
    font-size: 0.875rem;
}

.tag-name {
    line-height: 1;
}
</style>