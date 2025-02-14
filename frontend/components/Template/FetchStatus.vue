<template>
  <div v-if="status === 'pending'" class="display-status" v-loading="true">
    </div>
    <div v-else-if="status === 'error'" class="display-status">
      <ElResult
        icon="error"
        :title="errorTitle"
        sub-title="Bitte überprüfen Sie ob der Server läuft und versuchen Sie es erneut."
      />
    </div>
    <div v-else>
      <slot>INHALT</slot>
    </div>
</template>

<script setup lang="ts">
defineProps({
  status: {
    type: String,
    default: 'pending',
    required: true
  },
  errorTitle: {
    type: String,
    default: 'Fehler beim Laden der Daten'
  }
});
</script>

<style scoped>
.display-status {
  height: 300px; 
  width: 100%; 
  display: flex; 
  justify-content: center; 
  align-items: center;
}
</style>