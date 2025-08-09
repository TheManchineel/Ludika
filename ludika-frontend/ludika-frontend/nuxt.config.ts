// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    compatibilityDate: '2025-07-15',
    devtools: { enabled: true },

    app: {
        head: {
            link: [
                { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
                { rel: 'icon', type: 'image/png', sizes: '16x16', href: '/favicon-96x96.png' },
                { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
                { rel: 'apple-touch-icon', type: 'image/png', sizes: '180x180', href: '/apple-touch-icon.png' }
            ]
        }
    },

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