// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    compatibilityDate: '2025-07-15',
    devtools: {enabled: true},

    build: {
        transpile: [
            '@fortawesome/vue-fontawesome',
            '@fortawesome/free-brands-svg-icons',
            '@fortawesome/fontawesome-svg-core',
        ]
    },


    modules: [
        "@vuestic/nuxt",
        "@nuxt/image"
    ],

    image: {
        provider: 'none'
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
    },

    css: [
        '@fortawesome/fontawesome-svg-core/styles.css',
    ],

    plugins: [
        'plugins/fontawesome.js'
    ]
})