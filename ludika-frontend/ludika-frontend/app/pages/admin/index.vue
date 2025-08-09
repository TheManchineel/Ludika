<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'
import {FontAwesomeIcon} from "@fortawesome/vue-fontawesome";

definePageMeta({
    layout: 'default'
})

const { isPrivileged } = useAuth()

onMounted(() => {
    if (!isPrivileged()) {
        console.log('Unauthorized access to admin panel')
        navigateTo('/')
    }
})

const adminSections = [
    {
        title: 'Games Waiting for Approval',
        description: 'Review and manage games submitted by users that are waiting for approval',
        route: '/admin/games-waiting-for-approval',
        icon: 'fa-solid fa-clock',
        color: 'dark'
    },
    {
        title: 'User Management',
        description: 'View, edit, and manage user accounts and permissions',
        route: '/admin/users/',
        icon: 'fa-solid fa-users',
        color: 'primary'
    },
    {
        title: 'Reddit Scraping',
        description: 'Manage the Reddit scraping process',
        route: '/admin/scraping',
        icon: 'fab fa-reddit',
        color: 'danger'
    }
]
</script>

<template>
    <div class="admin-container">
        <div class="admin-header">
            <h1 class="admin-title">Administration Panel</h1>
            <p class="admin-subtitle">Manage the Ludika platform</p>
        </div>

        <div class="admin-content">
            <div class="sections-grid">
                <NuxtLink v-for="section in adminSections" :key="section.route" :to="section.route"
                    class="section-link">
                    <VaCard class="section-card" :color="section.color" gradient>
                        <div class="section-content">
                            <div class="section-main">
                                <div class="section-icon">
                                    <font-awesome-icon :icon="section.icon" class="section-fa-icon" />
                                </div>
                                <h2 class="section-title">{{ section.title }}</h2>
                                <p class="section-description">{{ section.description }}</p>
                            </div>
                            <div class="section-action">
                                <span class="action-text">Open Section</span>
                                <font-awesome-icon icon="arrow-right" class="action-fa-icon" />
                            </div>
                        </div>
                    </VaCard>
                </NuxtLink>
            </div>
        </div>
    </div>
</template>

<style scoped>
.admin-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

.admin-header {
    text-align: center;
    margin-bottom: 3rem;
}

.admin-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #333;
    margin-bottom: 0.5rem;
}

.admin-subtitle {
    font-size: 1.25rem;
    color: #666;
    margin: 0;
}

.admin-content {
    width: 100%;
}

.sections-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 2rem;
}

.section-link {
    display: block;
    text-decoration: none;
    color: inherit;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.section-link:hover {
    transform: translateY(-4px);
}

.section-link:hover .section-card {
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
}

.section-card {
    height: 100%;
    min-height: 280px;
    cursor: pointer;
    transition: box-shadow 0.2s ease;
    width: 100%;
}

.section-content {
    padding: 2rem;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    box-sizing: border-box;
}

.section-main {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}

.section-icon {
    margin-bottom: 1.5rem;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: white;
    margin-bottom: 1rem;
}

.section-description {
    font-size: 1rem;
    color: rgba(255, 255, 255, 0.9);
    margin-bottom: 0;
    line-height: 1.5;
}

.section-action {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}

.action-text {
    font-weight: 600;
    color: white;
    font-size: 1rem;
}

.section-fa-icon {
    color: white;
    font-size: 2rem;
}

.action-fa-icon {
    color: white;
    font-size: 1rem;
}
</style>