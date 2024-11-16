<template>
  <ElButton size="default" class="icon-button" type="primary">
    <ElTooltip :content="tooltip" :placement="tooltipPlacement" :hide-after="80" :show-after="300">
      <iconify-icon :icon="iconName" :width="iconSize" :height="iconSize" />
    </ElTooltip>
  </ElButton>
</template>

<script setup lang="ts">
import 'iconify-icon';

defineProps({
  iconName: {
    type: String,
    required: true,
    default: 'gis:pirate-poi',
  },
  iconSize: {
    type: Number,
    default: 25,
  },
  tooltip: {
    type: String,
    default: '',
    required: true,
  },
  tooltipPlacement: {
    type: String,
    default: 'top',
  }
});
</script>

<style scoped></style>