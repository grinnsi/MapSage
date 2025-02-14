// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-13',
  devtools: { enabled: true },
  ssr: false,
  app: {
    head: {
      charset: 'utf-8',
      // TODO Set name of application everywhere (here, in other pages, in nginx, ...; noted as [name])
      title: '[name] Dashboard',
    },
    // If env-variable DASHBOARD_URL is set, the dashboard will be available under /DASHBOARD_URL/ else under /dashboard/
    baseURL: (process.env.DASHBOARD_URL ? "/" + process.env.DASHBOARD_URL + "/" : "/dashboard/"),
  },
  // Development and production configuration
  // Both set the serverBaseURL to the correct value
  $development: {
    runtimeConfig: {
      public: {
        // Set serverBaseURL to: Base URL of Flask server + Port of FastAPI server + baseURL of Nuxt app (dashboard url)
        // Needed for correct API requests (otherwise it will just send requests to the Nuxt server, which doesn't exist))
        serverBaseURL: process.env.SERVER_BASE_URL + ":" + process.env.APISERVER_PORT + "/" + (process.env.DASHBOARD_URL ? process.env.DASHBOARD_URL + "/" : "dashboard/"),
      }
    }
  },
  $production: {
    runtimeConfig: {
      public: {
        // Set serverBaseURL to: URL of current hosting server + baseURL of Nuxt app (dashboard url)
        // For example if FastAPI server is hosted on https://localhost:8000 and the Flask portion serves this Nuxt app, the serverBaseURL will be https://localhost:8000/dashboard/
        serverBaseURL: "/" + (process.env.DASHBOARD_URL ? process.env.DASHBOARD_URL + "/" : "dashboard/"),
      }
    }
  },
  modules: [
    ['@nuxt/eslint', { fix: true }],
    '@element-plus/nuxt',
  ],
  elementPlus: {
    importStyle: 'scss',
  },
  imports: {
    dirs: [
      'utils/**',
    ],
  },
  vue: {
    compilerOptions: {
      isCustomElement: (tag) => tag === 'iconify-icon',
    },
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
  nitro: {
    static: true,
    preset: 'static',
    output: {
      publicDir: '../server/web/static',
    }
  }
})