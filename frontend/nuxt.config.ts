// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-13',
  devtools: { enabled: true },
  app: {
    head: {
      charset: 'utf-8',
      title: 'Interface',
    },
  },
  modules: [
    ['@nuxt/eslint', { fix: true }],
    '@element-plus/nuxt',
  ],
  elementPlus: {
    importStyle: 'scss',
  },
  router: {
    options: {
      hashMode: true,
    }
  },
  vite: {
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: '@use "~/scss/theming.scss" as *;',
          api: 'modern-compiler',
        },
      },
    },
  },
  vue: {
    compilerOptions: {
      isCustomElement: (tag) => tag === 'iconify-icon',
    },
  },
  nitro: {
    preset: 'static',
    baseURL: "/interface",
  }
})