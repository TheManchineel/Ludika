<script setup lang="ts">
interface Props {
    name: string
    size?: string
    class?: string
}

const props = withDefaults(defineProps<Props>(), {
    size: 'large',
    class: ''
})

const getInitials = (name: string): string => {
    return name
        .split(' ')
        .map(word => word.charAt(0).toUpperCase())
        .slice(0, 2)
        .join('')
}

const getAvatarColor = (name: string): string => {
    // Generate a consistent color based on the name
    const colors = ['primary', 'secondary', 'success', 'info', 'warning', 'danger'] as const
    const index = name.length % colors.length
    return colors[index]
}

const initials = computed(() => getInitials(props.name))
const avatarColor = computed(() => getAvatarColor(props.name))
</script>

<template>
    <VaAvatar :color="avatarColor" :size="size" :class="class">
        {{ initials }}
    </VaAvatar>
</template>