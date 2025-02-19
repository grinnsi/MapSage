<template>
  <TemplateSection section-title="Gespeicherte Kollektionen">
    <template #header-right>
      <TemplateButton tooltip="Neue Kollektion" iconName="flowbite:plus-outline" @click="showConnectionsDialog" />
    </template>
    <TemplateFetchStatus :status="status" error-title="Fehler beim laden der gespeicherten Kollektionen">
      <div class="saved-collections">
        <!-- TODO: Use expanding rows or all informations and a edit button -->
        <ElTable
          :data="collectionsTableData"
          stripe
          style="width: 100%"
        >
          <ElTableColumn prop="title" label="Titel" />
          <ElTableColumn prop="id" label="ID" />
          <ElTableColumn prop="description" label="Beschreibung" />
          <ElTableColumn prop="connection_name" label="Verbindung" />
          <ElTableColumn prop="url" label="URL" >
            <template #default="scope">
              <a :href="scope.row.url" target="_blank">{{ scope.row.url }}</a>
            </template>
          </ElTableColumn>
        </ElTable>
        <ElPagination 
          layout="prev, pager, next" 
          :page-size="pageSize"
          :total="Math.ceil((data ? data.length/pageSize : 0))"  
          @current-change="handlePageChange"  
        />
      </div>
    </TemplateFetchStatus>
  </TemplateSection>
  <ClientOnly>
    <!-- FIXME: Testdialog, will be removed, once adding of collections properly implemented -->
    <TemplateDialog
      ref="dialogRef"
      dialog-title="Neue Kollektionen hinzufügen"
      :close-on-click-modal="false"
      :dialog-type="DialogType.Blank"
      :dialog-style="StyleType.Normal"
    >
      <ElTable
        :data="connectionsTableData"
        stripe
        style="width: 100%"
      >
        <ElTableColumn prop="name" label="Name" />
        <ElTableColumn>
          <template #default="scope">
            <ElButton type="primary" @click="addCollections(scope.row.uuid)">Hinzufügen</ElButton>
          </template>
        </ElTableColumn>
      </ElTable>
    </TemplateDialog>
  </ClientOnly>
</template>

<script setup lang="ts">
definePageMeta({
  name: "Kollektionen"
});
// FIXME: The client (Nuxt) fetches data from the server with an offset, so the client isnt overloaded (Server handles pagination)
const { status, data, refresh } = useBaseUrlFetch<Collection[]>('/data/collections');

const collectionsTableData = ref<Collection[] | null>([]);
const connectionsTableData = ref<Connection[]>([]);
const pageSize = ref(20);
const dialogRef = ref<any>(null);

watchEffect(() => {
  if (status.value === 'success' && data.value) {
    collectionsTableData.value = data.value.slice(0, pageSize.value);
  }
});

function handlePageChange(newPage: number) {
  if (data.value) {
    collectionsTableData.value = data.value.slice((newPage - 1) * pageSize.value, newPage * pageSize.value);
  }
}

async function showConnectionsDialog() {
  try {
    const respone = await useBaseUrlFetchRaw('/data/connections', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    if (!respone.ok) throw new Error('Failed to fetch connections');
    connectionsTableData.value = JSON.parse(await respone.json());
  } catch (error) {
    console.error(error);
    useServerErrorNotification();
  } finally {
    dialogRef.value.toggleVisibility();
  }
}

async function addCollections(uuid: string) {
  try {
    const response = await useBaseUrlFetchRaw('/data/collections', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ uuid })
    });
    if (!response.ok) throw new Error('Failed to add collections');
    ElMessage({
      type: 'success',
      message: 'Collections added successfully'
    });
  } catch (error) {
    console.error(error);
    useServerErrorNotification();
  } finally {
    dialogRef.value.toggleVisibility();
    refresh();
  }
}
</script>

<style scoped>

</style>