<template>
    <VaModal v-model="isOpen" :title="title" size="small" blur hide-default-actions no-outside-dismiss>
        <template #default>
            <p v-if="message">{{ message }}</p>
            <p v-if="warningMessage" class="text-danger">{{ warningMessage }}</p>
            <slot />
        </template>

        <template #footer>
            <VaButton preset="secondary" @click="handleCancel" :disabled="loading">
                {{ cancelText }}
            </VaButton>
            <VaButton :color="confirmColor" @click="handleConfirm" :loading="loading">
                {{ confirmText }}
            </VaButton>
        </template>
    </VaModal>
</template>

<script setup lang="ts">
interface Props {
    modelValue: boolean
    title: string
    message?: string
    warningMessage?: string
    confirmText?: string
    cancelText?: string
    confirmColor?: string
    loading?: boolean
}

interface Emits {
    (e: 'update:modelValue', value: boolean): void
    (e: 'confirm'): void
    (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
    confirmText: 'Confirm',
    cancelText: 'Cancel',
    confirmColor: 'primary',
    loading: false
})

const emit = defineEmits<Emits>()

const isOpen = computed({
    get: () => props.modelValue,
    set: (value) => emit('update:modelValue', value)
})

const handleConfirm = () => {
    emit('confirm')
}

const handleCancel = () => {
    emit('cancel')
    isOpen.value = false
}
</script>

<style scoped>
.text-danger {
    color: #dc3545;
    font-weight: 500;
}
</style>