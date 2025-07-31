import { defineVuesticConfig, createIconsConfig } from 'vuestic-ui'

export default defineVuesticConfig({
    icons: createIconsConfig({
        fonts: [
            {
                name: 'fa-{name}',
                resolve: ({ name }) => {
                    return {
                        class: `fas fa-${name}`,
                    };
                }
            },
        ]
    }),
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
    },
    components: {
        VaModal: {
            zIndex: 9999,
        }
    }
})