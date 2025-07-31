<template>
  <div>
    <NuxtLayout>
      <NuxtRouteAnnouncer />
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>

<style>
:root {
  --container-max-width: 1200px;
  --container-padding: 1rem;
}

body {
  margin: 0;
}

/* Fix for Nuxt DevTools interfering with modals */
.va-modal,
[data-va-modal],
.va-modal__dialog,
.va-modal__container {
  z-index: 9999999 !important;
}
</style>