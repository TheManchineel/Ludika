// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },

  modules: [
    '@nuxt/ui',
    '@nuxt/eslint',
    '@nuxt/content',
    '@nuxt/icon',
    '@nuxt/fonts',
    '@nuxt/image',
    '@nuxt/scripts'
  ],

  css: ['~/assets/css/main.css'],

  future: {
    compatibilityVersion: 4
  },

  compatibilityDate: '2024-11-27'
})