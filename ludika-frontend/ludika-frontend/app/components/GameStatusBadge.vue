<template>
    <VaChip v-if="shouldShowBadge" :color="badgeColor" :outline="outline" size="medium" class="status-badge">
        <div class="badge-content">
            <font-awesome-icon :icon="badgeIcon" class="badge-icon" />
            <span class="badge-text">{{ badgeText }}</span>
        </div>
    </VaChip>
</template>

<script setup lang="ts">
interface Props {
    status: string
    outline?: boolean
}

const props = withDefaults(defineProps<Props>(), {
    outline: false
})

const statusConfig = {
    draft: {
        text: 'Draft',
        icon: 'edit',
        color: 'warning'
    },
    submitted: {
        text: 'Submitted',
        icon: 'clock',
        color: 'info'
    },
    rejected: {
        text: 'Rejected',
        icon: 'times-circle',
        color: 'danger'
    }
}

const shouldShowBadge = computed(() => {
    return props.status !== 'approved'
})

const badgeConfig = computed(() => {
    return statusConfig[props.status as keyof typeof statusConfig]
})

const badgeText = computed(() => badgeConfig.value?.text || '')
const badgeIcon = computed(() => badgeConfig.value?.icon || 'circle')
const badgeColor = computed(() => badgeConfig.value?.color || 'secondary')
</script>

<style scoped>
.status-badge {
    font-weight: 600;
}

.badge-content {
    display: flex;
    align-items: center;
    gap: 0.375rem;
}

.badge-icon {
    font-size: 0.875rem;
}

.badge-text {
    font-size: 0.875rem;
}
</style>