<template>
  <TemplateSection 
    section-title="Gespeicherte Kollektionen" 
    fill-space
  >
    <template #header-right>
      <TemplateButton tooltip="Neue Kollektion" iconName="flowbite:plus-outline" @click="showConnectionsDialog" />
    </template>
    <div class="table-container">
      <TemplateFetchStatus :status="status" error-title="Fehler beim laden der gespeicherten Kollektionen">
        <!-- TODO: Use expanding rows or all informations and an edit button -->
        <ElTable
          :data="collectionsTableData"
          stripe
        >
          <ElTableColumn prop="title" label="Titel" />
          <ElTableColumn prop="id" label="ID" />
          <ElTableColumn prop="description" label="Beschreibung" />
          <ElTableColumn prop="connection_name" label="Verbindung" />
          <ElTableColumn prop="url" label="URL" >
            <template #default="scope">
              <ElLink 
                :href="scope.row.url" 
                target="_blank" 
                :underline="false"
                class="collection-link"
              >
                {{ scope.row.url }}
              </ElLink>
            </template>
          </ElTableColumn>
        </ElTable>
      </TemplateFetchStatus>
    </div>
    <template #footer>
      <div class="pagination-container">
        <ElPagination 
          layout="prev, pager, next" 
          :page-size="pageSize"
          :total="data?.length"
          :hide-on-single-page="true"
          @current-change="handlePageChange"  
        />
      </div>
    </template>
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
      <h3 style="color: black;">Wählen Sie die gewünschte Datenquelle aus:</h3>
      <ElTable
        :data="connectionsTableData"
        stripe
        style="width: 100%"
      >
        <ElTableColumn prop="name" label="Name" />
        <ElTableColumn>
          <template #default="scope" >
            <div style="display: flex; justify-content: end;">
              <ElButton type="primary" @click="addCollections(scope.row.uuid)">Hinzufügen</ElButton>
            </div>
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

const collectionsTableData = ref<Collection[] | undefined>([]);
const connectionsTableData = ref<Connection[]>([]);
const pageSize = ref(10);
const dialogRef = ref<any>(null);

watchEffect(() => {
  if (status.value === 'success' && data.value) {
    handlePageChange(1);
  }
});

function handlePageChange(newPage: number) {
  if (data.value) {
    collectionsTableData.value = data.value.slice((newPage - 1) * pageSize.value, newPage * pageSize.value);
  } else {
    throw new Error('Collection data is not available');
  }
}

async function showConnectionsDialog() {
  try {
    const response: any = await useBaseUrlFetchRaw('/data/connections', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    connectionsTableData.value = response;
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
.table-container {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  width: 100%;
}

.collection-link {
  overflow-wrap: break-word;
  word-wrap: break-word;
  word-break: break-word;
  hyphens: none;
  display: block;
  max-width: 100%;
}

.pagination-container {
  display: flex;
  justify-content: center;
}
</style>