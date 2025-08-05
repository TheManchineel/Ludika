<script setup lang="ts">
import { useUsers } from '~/composables/useUsers'

definePageMeta({
    layout: 'default'
})

const route = useRoute()
const { user, userLoading, userError, fetchUserById } = useUsers()

const userUuid = route.params.uuid as string

onMounted(() => {
    fetchUserById(userUuid)
})
</script>

<template>
    <UserProfile :user="user" :loading="userLoading" :error="userError" :show-back-button="true" />
</template>
