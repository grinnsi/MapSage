<template>
  <section>
    <div class="section-header">
      <h4>{{ sectionTitle }}</h4>
      <div>
        <slot name="header-right"></slot>
      </div>
    </div>
    <div class="section-content">
      <slot>ABSCHNITTINHALT</slot>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps({
  sectionTitle: {
    type: String,
    required: true,
    default: "Titel"
  },

})
</script>

<style scoped lang="scss">
.section-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}

.section-content {
  display: flex;
  align-items: center;
}
</style>