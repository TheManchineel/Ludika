<script setup lang="ts">
definePageMeta({
  layout: 'default'
})

useHead({
  title: 'Ludika',
  meta: [
    { name: 'description', content: 'Share and discover new educational games with Ludika.' }
  ]
})

</script>

<template>
  <div>
    <GameLibrary />
  </div>
</template>
