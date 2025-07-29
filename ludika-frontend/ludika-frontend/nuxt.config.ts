// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  modules: [
    "@vuestic/nuxt",
    "@nuxt/image"
  ],

  image: {
    provider: 'none'
  },

  vuestic: {
    config: {
      colors: {
        variables: {
          primary: "#9423e0",
          secondary: "#002c85",
          success: "#40e583",
          info: "#2c82e0",
          danger: "#e34b4a",
          warning: "#ffc200",
          gray: "#babfc2",
          dark: "#34495e",
        }
      }
    }
  },

  nitro: {
    devProxy: {
      '/api/v1': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        prependPath: true
      },
      '/static': {
        target: 'http://localhost:8000/static',
        changeOrigin: true,
        prependPath: true
      }
    }
  }
})