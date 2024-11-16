<template>
  <TemplateSection section-title="Vorhandene Kollektionen:">
    <template #header-right>
      <TemplateButton tooltip="Neue Kollektion" iconName="flowbite:plus-outline"
        @click="useEmitter().value.emit('show-new-namespace-dialog')" />
    </template>
    <ElTable :data="data as Namespace[]" style="width: 100%" table-layout="auto" header-cell-class-name="column-header">
      <ElTableColumn prop="name" label="Name" sortable />
      <ElTableColumn prop="url" label="Url" sortable 
        :formatter="(row) => '/' + row.url"
      />
      <ElTableColumn label="Aktionen">
        <template #default="scope">
          <TemplateButton tooltip="Namesapce löschen" iconName="flowbite:trash-bin-outline" type="danger"
            @click="showConfirmationDialog(scope.row)" />
        </template>
      </ElTableColumn>
    </ElTable>
    <TemplateDialog ref="confirmationDialogRef" :dialogStyle="StyleType.Danger"
      :dialogTitle="`Namespace '` + selectedNamespace.name + `' löschen ?`" :close-on-click-modal="true"
      :dialog-type="DialogType.Confirmation" @confirm="deleteNamespace(selectedNamespace.uuid)">
      <span>Sind Sie sicher, dass Sie die Kollektion löschen möchten ?
        <br>Diese Aktion kann nicht rückgängig gemacht werden
      </span>
    </TemplateDialog>
    <DialogsNewNamespace />
  </TemplateSection>
</template>

<script setup lang="ts">
definePageMeta({
  name: 'Kollektionen'
});

// const { data, refresh } = useFetch<Namespace[]>('/database/getNamespaces');
const data: any[] = [];
const refresh = console.log;

const confirmationDialogRef = ref();
const selectedNamespace = ref<Namespace>({
  uuid: '',
  name: '',
  url: ''
});

onMounted(() => {
  useEmitter().value.on('update-namespace-table', refresh as any);
});

async function showConfirmationDialog(namespace: Namespace) {
  selectedNamespace.value = namespace;
  confirmationDialogRef.value!.toggleVisibility();
}

async function deleteNamespace(uuid: string) {
  confirmationDialogRef.value!.toggleVisibility();

  try {
    const response = await $fetch('/database/deleteNamespace', {
      method: 'POST',
      headers: {
        'Content-Type': 'text/plain'
      },
      body: uuid
    });

    ElMessage({
      type: 'success',
      message: 'Namespace erfolgreich gelöscht'
    });
  } catch (error) {
    console.error(error)
    useServerErrorNotification();
  } finally {
    refresh();
  }
}
</script>

<style scoped lang="scss">

</style>