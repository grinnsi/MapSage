<template>
  <ElButton size="default" class="icon-button" :type="buttonType">
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
  },
  buttonType: {
    type: String as () => StyleType,
    default: StyleType.Normal,
  }
});
</script>

<style scoped></style>