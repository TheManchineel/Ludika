<script setup lang="ts">
import { useGames } from '~/composables/useGames'
import GameTagSelector from './GameTagSelector.vue'
import Pagination from './Pagination.vue'

interface Props {
    searchable?: boolean
    tagFilterable?: boolean
    title?: string
    subtitle?: string
    apiEndpoint?: string
    showHero?: boolean
}

const props = withDefaults(defineProps<Props>(), {
    searchable: true,
    tagFilterable: true,
    title: 'Ludika',
    subtitle: 'An ever–growing collection of educational games.',
    apiEndpoint: '/api/v1/games/',
    showHero: true
})

const searchQuery = ref('')
const selectedTags = ref<number[]>([])

const {
    games,
    loading,
    error,
    fetchGames,
    fetchGamesFromEndpoint,
    tags,
    tagsLoading,
    tagsError,
    fetchTags,
    currentPage,
    totalPages,
    totalCount,
    hasNextPage,
    hasPreviousPage,
    nextPage,
    previousPage,
    goToPage,
    clearPagination
} = useGames()

// Use custom endpoint if provided, otherwise use default fetchGames
const loadGames = (searchQuery?: string, selectedTags?: number[], page?: number) => {
    if (props.apiEndpoint === '/api/v1/games/') {
        fetchGames(searchQuery, selectedTags, page)
    } else {
        fetchGamesFromEndpoint(props.apiEndpoint, searchQuery, selectedTags, page)
    }
}

// Watch for search query changes
watch(searchQuery, (newQuery) => {
    if (props.searchable) {
        clearPagination()
        loadGames(newQuery, selectedTags.value, 0)
    }
})

// Watch for tag selection changes
watch(selectedTags, (newTags) => {
    if (props.tagFilterable) {
        clearPagination()
        loadGames(searchQuery.value, newTags, 0)
    }
})

// Watch for page changes
watch(currentPage, (newPage) => {
    loadGames(searchQuery.value, selectedTags.value, newPage)
})

// Pagination handlers
const handleNextPage = () => {
    nextPage()
}

const handlePreviousPage = () => {
    previousPage()
}

const handleGoToPage = (page: number) => {
    goToPage(page)
}

// Initial load
onMounted(() => {
    if (props.tagFilterable) {
        fetchTags()
    }
    loadGames()
})
</script>

<template>
    <div>
        <div v-if="showHero" class="hero-section">
            <div class="hero-content">
                <h1 class="hero-title">{{ title }}</h1>
                <p class="hero-subtitle">{{ subtitle }}</p>
                <div v-if="searchable" class="search-container">
                    <VaInput v-model="searchQuery" placeholder="Search for games..." class="search-input"
                        prepend-inner="search" preset="solid" clearable />
                </div>
                <div v-if="tagFilterable" class="tag-filter-container">
                    <GameTagSelector v-model:selectedTags="selectedTags" :availableTagsData="tags"
                        :tagsLoading="tagsLoading" :tagsError="tagsError" size="medium" />
                </div>
            </div>
        </div>

        <div class="games-section">
            <div class="container">
                <div v-if="loading" class="loading-container">
                    <VaProgressCircle indeterminate />
                </div>

                <div v-else-if="error" class="error-container">
                    <VaAlert color="danger" :title="error" />
                </div>

                <div v-else-if="games.length === 0" class="empty-container">
                    <p>No games found.</p>
                </div>

                <div v-else class="games-grid">
                    <GameCard v-for="game in games" :key="game.id" :game="game" />
                </div>

                <!-- Pagination -->
                <Pagination v-if="!loading && !error && games.length > 0" :currentPage="currentPage"
                    :totalPages="totalPages" :totalCount="totalCount" :hasNextPage="hasNextPage"
                    :hasPreviousPage="hasPreviousPage" @next="handleNextPage" @previous="handlePreviousPage"
                    @goto="handleGoToPage" />
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

.tag-filter-container {
    max-width: 800px;
    margin: 1.5rem auto 0;
    padding: 0 1rem;
}

.games-section {
    padding: 3rem 0;
    background-color: #f8f9fa;
}

.container {
    max-width: var(--container-max-width);
    margin: 0 auto;
    padding: 0 var(--container-padding);
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

/* White [+Add Tag] button */
:deep(.add-tag-chip) {
    border-color: white !important;
    color: white !important;
}

:deep(.add-tag-chip .tag-content) {
    color: white !important;
}

:deep(.add-tag-chip .tag-icon),
:deep(.add-tag-chip .tag-name) {
    color: white !important;
}
</style>