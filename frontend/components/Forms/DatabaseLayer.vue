<template>
  <div class="select-connection">
    <span>Ausgewählte Verbindung:</span>
    <!-- TODO: Klein neben dem Verbindungsname ein paar Parameter anzeigen, da der Naeme nicht unique (z.B. user, db) -->
    <ElSelectV2
      v-model="selecedConnection"
      :options="options"
      :props="{
        value: 'uuid',
        label: 'name'
      }"
      placeholder="Verbindung 1"
      style="width: 50%"
      filterable
    />
  </div>
  <ElTable
    ref="tableRef"
    v-loading="loading"
    :data="tableData"
    style="width: 100%"
    table-layout="auto"
    header-cell-class-name="column-header"
  >
    <ElTableColumn
      type="selection"
      :selectable="() => true"
    />
    <ElTableColumn
      prop="name"
      label="Name"
      sortable
    />
    <ElTableColumn
      prop="schema"
      label="Schema"
      sortable
    />
  </ElTable>
</template>

<script setup lang="ts">
import type { PropType } from 'vue';

const selecedConnection = ref('');
const loading = ref(false);
const tableRef = ref();
const tableData = ref<Array<{ name: string, schema: string }>>([]);

watchEffect(async () => {
  if (selecedConnection.value !== '') {
    loading.value = true;
    try {
      const response = await $fetch('/database/getPostgresLayers', {
        method: 'POST',
        headers: {
          'Content-Type': 'text/plain'
        },
        body: selecedConnection.value,
      });
      tableData.value = response.rows;
      loading.value = false;
    } catch (error) {
      console.error(error);
      useServerErrorNotification();
    }
  } else {
    tableData.value = [];
    loading.value = false;
  }
})

const props = defineProps({
  savedConnections: {
    type: Array as PropType<Array<Connection>>,
    default: []
  },
  savedCollections: {
    type: Array as PropType<Array<Collection>>,
    default: []
  }
});

const options = props.savedConnections.map((connection) => ({
  uuid: connection.uuid,
  name: connection.name
}));

</script>

<style scoped lang="scss">
.select-connection {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
</style>