<template>
    <div v-if="totalPages > 1" class="pagination-container">
        <div class="pagination">
            <!-- Previous button -->
            <VaButton :disabled="!hasPreviousPage" preset="secondary" size="small" @click="$emit('previous')"
                class="pagination-btn">
                <font-awesome-icon icon="chevron-left" />
                Previous
            </VaButton>

            <!-- Page numbers -->
            <div class="page-numbers">
                <!-- First page -->
                <VaButton v-if="showFirstPage" :preset="currentPage === 0 ? 'primary' : 'secondary'" size="small"
                    @click="$emit('goto', 0)" class="page-btn">
                    1
                </VaButton>

                <!-- First ellipsis -->
                <span v-if="showFirstEllipsis" class="ellipsis">...</span>

                <!-- Visible page range -->
                <VaButton v-for="page in visiblePages" :key="page"
                    :preset="currentPage === page ? 'primary' : 'secondary'" size="small" @click="$emit('goto', page)"
                    class="page-btn">
                    {{ page + 1 }}
                </VaButton>

                <!-- Last ellipsis -->
                <span v-if="showLastEllipsis" class="ellipsis">...</span>

                <!-- Last page -->
                <VaButton v-if="showLastPage" :preset="currentPage === totalPages - 1 ? 'primary' : 'secondary'"
                    size="small" @click="$emit('goto', totalPages - 1)" class="page-btn">
                    {{ totalPages }}
                </VaButton>
            </div>

            <!-- Next button -->
            <VaButton :disabled="!hasNextPage" preset="secondary" size="small" @click="$emit('next')"
                class="pagination-btn">
                Next
                <font-awesome-icon icon="chevron-right" />
            </VaButton>
        </div>

        <!-- Page info -->
        <div class="page-info">
            <span>
                Page {{ currentPage + 1 }} of {{ totalPages }}
                ({{ totalCount }} total items)
            </span>
        </div>
    </div>
</template>

<script setup lang="ts">
interface Props {
    currentPage: number
    totalPages: number
    totalCount: number
    hasNextPage: boolean
    hasPreviousPage: boolean
}

interface Emits {
    (e: 'next'): void
    (e: 'previous'): void
    (e: 'goto', page: number): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Configuration for visible page range
const VISIBLE_PAGES = 5

const visiblePages = computed(() => {
    const start = Math.max(
        0,
        Math.min(
            props.currentPage - Math.floor(VISIBLE_PAGES / 2),
            props.totalPages - VISIBLE_PAGES
        )
    )
    const end = Math.min(start + VISIBLE_PAGES, props.totalPages)

    return Array.from({ length: end - start }, (_, i) => start + i)
})

const showFirstPage = computed(() => {
    return props.totalPages > VISIBLE_PAGES && visiblePages.value[0] > 0
})

const showLastPage = computed(() => {
    return props.totalPages > VISIBLE_PAGES &&
        visiblePages.value[visiblePages.value.length - 1] < props.totalPages - 1
})

const showFirstEllipsis = computed(() => {
    return showFirstPage.value && visiblePages.value[0] > 1
})

const showLastEllipsis = computed(() => {
    return showLastPage.value &&
        visiblePages.value[visiblePages.value.length - 1] < props.totalPages - 2
})
</script>

<style scoped>
.pagination-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    margin: 2rem 0;
}

.pagination {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.pagination-btn {
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.page-numbers {
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.page-btn {
    min-width: 2.5rem;
}

.ellipsis {
    padding: 0 0.5rem;
    color: #6b7280;
    font-weight: 600;
}

.page-info {
    font-size: 0.875rem;
    color: #6b7280;
    text-align: center;
}

@media (max-width: 768px) {
    .pagination {
        flex-wrap: wrap;
        justify-content: center;
    }

    .page-numbers {
        order: -1;
        width: 100%;
        justify-content: center;
        margin-bottom: 0.5rem;
    }
}
</style>