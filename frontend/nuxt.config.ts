// https://nuxt.com/docs/api/configuration/nuxt-config
function getBaseUrl() {
  let root = process.env.API_SERVER_ROOT_PATH
  if (root) {
    return root + (process.env.DASHBOARD_URL ? "/" + process.env.DASHBOARD_URL + "/" : "/dashboard/");
  }

  return process.env.DASHBOARD_URL ? "/" + process.env.DASHBOARD_URL + "/" : "/dashboard/";
}

export default defineNuxtConfig({
  compatibilityDate: '2024-11-13',
  devtools: { enabled: true },
  ssr: false,
  app: {
    head: {
      charset: 'utf-8',
      title: 'MapSage Dashboard',
    },
    // If env-variable DASHBOARD_URL is set, the dashboard will be available under /DASHBOARD_URL/ else under /dashboard/
    // Prefix that with the API_SERVER_ROOT_PATH if set
    baseURL: getBaseUrl(),
  },
  // Development and production configuration
  // Both set the serverBaseURL to the correct value
  $development: {
    runtimeConfig: {
      public: {
        // Set serverBaseURL to: Base URL of Flask server + Port of FastAPI server + baseURL of Nuxt app (dashboard url)
        // Needed for correct API requests (otherwise it will just send requests to the Nuxt server, which doesn't exist))
        // Following line only works with local (non-docker) api server 
        // serverBaseURL: process.env.SERVER_BASE_URL + ":" + process.env.HOST_PORT_API_SERVER + "/" + (process.env.DASHBOARD_URL ? process.env.DASHBOARD_URL + "/" : "dashboard/"),

        // Following line works with dockerized api server
        serverBaseURL: process.env.SERVER_BASE_URL + "" + process.env.API_SERVER_ROOT_PATH + "/" + (process.env.DASHBOARD_URL ? process.env.DASHBOARD_URL + "/" : "dashboard/"),
      }
    }
  },
  $production: {
    runtimeConfig: {
      public: {
        // Set serverBaseURL to: URL of current hosting server + baseURL of Nuxt app (dashboard url)
        // For example if FastAPI server is hosted on https://localhost:8000 and the Flask portion serves this Nuxt app, the serverBaseURL will be https://localhost:8000/dashboard/
        // Following line only works with local (non-docker) api server 
        // serverBaseURL: "/" + (process.env.DASHBOARD_URL ? process.env.DASHBOARD_URL + "/" : "dashboard/"),

        serverBaseURL: getBaseUrl(),
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
      terserOptions: {
        compress: {
          drop_console: false
        }
      }
    },
  },
  nitro: {
    static: true,
    preset: 'static',
    output: {
      publicDir: (process.env.BUILD_OUTPUT_DIR ? process.env.BUILD_OUTPUT_DIR : '../server/web/static'),
    }
  }
})