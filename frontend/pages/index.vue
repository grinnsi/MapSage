<template>
  <div>
    {{ $route.name }}
    <ElButton type="primary">Test</ElButton>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  name: "Startseite"
});
</script>

<style scoped>

</style>