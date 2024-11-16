// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-13',
  devtools: { enabled: true },
  ssr: false,
  app: {
    head: {
      charset: 'utf-8',
      title: '[name] Dashboard',
    },
    baseURL: "/dashboard",
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
  imports: {
    dirs: [
      'utils/**',
    ],
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
    build: {
      emptyOutDir: true,
    },
  },
  vue: {
    compilerOptions: {
      isCustomElement: (tag) => tag === 'iconify-icon',
    },
  },
  nitro: {
    static: true,
    preset: 'static',
    output: {
      publicDir: '../server/web/static',
    }
  }
})