<template>
  <section class="section" :class="{ 'fill-space': fillSpace }">
    <div class="section-header">
      <h4>{{ sectionTitle }}</h4>
      <div>
        <slot name="header-right"></slot>
      </div>
    </div>
    <div class="section-content" :class="{ 'fill-space': fillSpace }" :style="sectionContentStyle">
      <slot>ABSCHNITTINHALT</slot>
    </div>
    <div class="section-footer">
      <slot name="footer"></slot>
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
  fillSpace: {
    type: Boolean,
    default: false
  },
  sectionContentStyle: {
    type: String,
  }
})
</script>

<style scoped lang="scss">
.section {
  display: flex;
  flex-direction: column;
}

.fill-space {
  flex: 1;
}

.section-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}

.section-content {
  display: flex;
  flex-direction: column;
}

.section-footer {
  display: flex;
  flex-direction: column;
}
</style>