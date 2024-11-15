<template>
  <ElContainer class="base-layout">
    <ElAside class="sidebar" width="170px">
      <ElMenu class="vertical-menu navigation-menu">
        <template v-for="route in nav" :key="route.name">
          <NuxtLink :to="route" class="navigation-link" :class="(route.path === $route.path)?'navigation-current-page':'navigation-different-page'">
            <ElMenuItem :index="route.name?.toString()">
              <span>{{ route.name }}</span>
            </ElMenuItem>
          </NuxtLink>
        </template>
      </ElMenu>
    </ElAside>
    <ElMain class="main-content">
      <ElScrollbar>
        <h2 class="page-name">{{ $route.name }}</h2>
        <NuxtErrorBoundary>
          <NuxtPage />
          <template #error="{ error }">
            <p>An error occured: {{ error }}</p>
          </template>
        </NuxtErrorBoundary>
      </ElScrollbar>
    </ElMain>
  </ElContainer>
</template>

<script setup lang="ts">
const nav = [
  {path: '/', name: 'Startseite'},
  // {path: '/layers', name: 'Ebenen'},
  // {path: '/settings', name: 'Einstellungen'},
];
</script>

<style lang="scss">
@import url('./scss/elementPlus.scss');
@import url('./scss/main.scss');
@import url('./scss/navigationbar.scss');

html,
body,
#__nuxt {
  position: absolute;
  left: 0px;
  right: 0px;
  top:0px;
  height: 100%;
  margin: 0;
  padding: 0;
  font-family: Arial, Helvetica, sans-serif;
  background-color: rgb(243, 243, 243);
}

.page-name {
  margin-top: 0;
}
</style>