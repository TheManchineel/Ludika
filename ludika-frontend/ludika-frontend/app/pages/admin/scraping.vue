<script setup lang="ts">

import { useAuth } from "~/composables/useAuth";
import { useToast } from 'vuestic-ui'

definePageMeta({
  layout: 'default'
})

const { isPrivileged, authenticatedFetch } = useAuth()
const { init: toast } = useToast()

type ScrapingState = {
  status: 'running' | 'stopped' | string,
  posts_found: number,
  posts_processed: number,
  games_found: number,
  games_added: number,
}

const state = ref<ScrapingState | null>(null)
const loading = ref(false)

const fetchStatus = async () => {
  loading.value = true
  try {
    const data = await authenticatedFetch<ScrapingState>('/api/v1/ai/reddit-scraping')
    state.value = data
  } catch (error: any) {
    const detail = error?.data?.detail || error?.response?._data?.detail || 'Failed to fetch scraping status.'
    toast({ message: detail, color: 'danger' })
  } finally {
    loading.value = false
  }
}

const startScraping = async () => {
  loading.value = true
  try {
    const data = await authenticatedFetch<ScrapingState>('/api/v1/ai/reddit-scraping', { method: 'POST' })
    state.value = data
  } catch (error: any) {
    if (error?.status === 400 || error?.statusCode === 400) {
      const detail = error?.data?.detail || error?.response?._data?.detail || 'Cannot start scraping.'
      toast({ message: detail, color: 'danger' })
    } else {
      toast({ message: 'Unexpected error while starting scraping.', color: 'danger' })
    }
  } finally {
    loading.value = false
  }
}

// Redirect if not privileged user
onMounted(() => {
  if (!isPrivileged()) {
    navigateTo('/')
    return
  }
  fetchStatus()
})

</script>

<template>
  <div class="container">
    <div class="header">
      <h2>Reddit Scraping</h2>
      <div class="actions">
        <VaButton preset="primary" :loading="loading" @click="fetchStatus">
          <font-awesome-icon icon="fa-solid fa-rotate-right" />
        </VaButton>
        <VaButton color="success" :loading="loading" @click="startScraping">
          <font-awesome-icon icon="fa-solid fa-play" /> Start scraping
        </VaButton>
      </div>
    </div>

    <div v-if="state" class="table-wrapper">
      <table class="status-table">
        <tbody>
          <tr>
            <th>Status</th>
            <td>{{ state.status }}</td>
          </tr>
          <tr>
            <th>Posts found</th>
            <td>{{ state.posts_found }}</td>
          </tr>
          <tr>
            <th>Posts processed</th>
            <td>{{ state.posts_processed }}</td>
          </tr>
          <tr>
            <th>Games found</th>
            <td>{{ state.games_found }}</td>
          </tr>
          <tr>
            <th>Games added</th>
            <td>{{ state.games_added }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <VaAlert v-else color="info" class="mt-4">No data yet. Click "Update" to fetch current status.</VaAlert>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.table-wrapper {
  overflow-x: auto;
}

.status-table {
  width: 100%;
  border-collapse: collapse;
}

.status-table th,
.status-table td {
  text-align: left;
  padding: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
}

.status-table th {
  width: 220px;
  color: #6b7280;
  font-weight: 600;
}
</style>