<template>
  <TemplateSection 
    section-title="Gespeicherte Kollektionen" 
    fill-space
  >
    <template #header-right>
      <TemplateButton 
        tooltip="Kollektionen löschen" 
        iconName="flowbite:trash-bin-outline"
        :button-type="StyleType.Danger"
        @click="() =>{
        if (collectionTable.getSelectionRows().length > 0) {
          confirmationDialogRef.toggleVisibility();
        } else {
          ElMessage({
            type: 'info',
            message: 'Bitte wählen Sie mindestens eine Kollektion aus'
          });
        }
      }" />
      <TemplateButton tooltip="Neue Kollektion" iconName="flowbite:plus-outline" @click="showConnectionsDialog" />
    </template>
    <div class="table-container">
      <TemplateFetchStatus :status="status" error-title="Fehler beim laden der gespeicherten Kollektionen">
        <ElTable
          ref="collectionTable"
          :data="collectionsTableData"
          stripe
        >
          <ElTableColumn type="selection" />
          <ElTableColumn prop="title" label="Titel" />
          <ElTableColumn prop="id" label="ID" />
          <ElTableColumn prop="description" label="Beschreibung" />
          <ElTableColumn prop="connection_name" label="Verbindung" />
          <ElTableColumn prop="url" label="URL" >
            <template #default="scope">
              <ElLink 
                :href="scope.row.url + '?f=html'" 
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
      dialog-title="Neue Kollektion hinzufügen"
      :close-on-click-modal="false"
      :dialog-type="DialogType.Blank"
      :dialog-style="StyleType.Normal"
      @closed="layerTableData = null"
    >
      <div v-if="!layerTableData">
        <h3 style="color: black;">Wählen Sie die gewünschte Datenquelle aus:</h3>
        <ElTable
          :data="conectionsTableData"
          stripe
          style="width: 100%"
        >
          <ElTableColumn prop="name" label="Name" />
          <ElTableColumn>
            <template #default="scope" >
              <div style="display: flex; justify-content: end;">
                <ElButton type="primary" @click="getDatasetInformation(scope.row.uuid)">Auswählen</ElButton>
              </div>
            </template>
          </ElTableColumn>
        </ElTable>
      </div>
      <div v-else>
        <h3 style="color: black;">Wählen Sie die Ebene aus:</h3>
        <ElTable
          :data="layerTableData"
          stripe
          style="width: 100%"
        >
          <ElTableColumn prop="name" label="Name" />
          <ElTableColumn>
            <template #default="scope" >
              <div style="display: flex; justify-content: end;">
                <ElButton type="primary" @click="addCollection(datasetUuid, scope.row.name)">Auswählen</ElButton>
              </div>
            </template>
          </ElTableColumn>
        </ElTable>
      </div>
    </TemplateDialog>
    <TemplateDialog
      ref="confirmationDialogRef"
      :dialogStyle="StyleType.Danger"
      :dialogTitle="'Ausgewählte Kollektionen löschen ?'"
      :close-on-click-modal="true"
      :dialog-type="DialogType.Confirmation"
      @confirm="deleteCollections"  
    >
      <span>Sind Sie sicher, dass Sie die Kollektionen löschen möchten ?
      <br>Diese Aktion kann nicht rückgängig gemacht werden.
      </span>
    </TemplateDialog>
  </ClientOnly>
</template>

<script setup lang="ts">
definePageMeta({
  name: "Kollektionen"
});
// FIXME: The client (Nuxt) fetches data from the server with an offset, so the client isnt overloaded (Server handles pagination)
const { status, data, refresh } = useBaseUrlFetch<Collection[]>('/data/collections');

const collectionTable = ref<any>(null);
const collectionsTableData = ref<Collection[] | undefined>([]);
const conectionsTableData = ref<Connection[]>([]);
const layerTableData = ref<any>(null);
const pageSize = ref(10);

const dialogRef = ref<any>(null);
const datasetUuid = ref<string>('');
const timeField = ref<string>('');
const confirmationDialogRef = ref<any>(null);

watchEffect(() => {
  if (status.value === 'success' && data.value) {
    data.value.sort((a, b) => a.title.localeCompare(b.title));
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
    const response: any = await useBaseUrlFetchRaw('/data/settings/connections', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    conectionsTableData.value = response;
    conectionsTableData.value.sort((a, b) => a.name.localeCompare(b.name));
  } catch (error) {
    console.error(error);
    useServerErrorNotification();
  } finally {
    dialogRef.value.toggleVisibility();
  }
}

async function getDatasetInformation(uuid: string) {
  try {
    const response = await useBaseUrlFetchRaw(`/data/settings/datasets/${uuid}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    datasetUuid.value = uuid;
    layerTableData.value = JSON.parse(response as any)["layers"];
  } catch (error) {
    console.error(error);
    useServerErrorNotification();
  }
}

async function addCollection(datasetUuid: string, layerName: string) {
  try {
    const response = await useBaseUrlFetchRaw('/data/collections', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ uuid: datasetUuid, layer_name: layerName })
    });
    // if (!response.ok) throw new Error('Failed to add collections');
    ElMessage({
      type: 'success',
      message: 'Kollektionen erfolgreich hinzugefügt'
    });
  } catch (error: any) {
    if (error.status === 409) {
      ElMessage({
        type: 'error',
        message: 'Kollektion existiert bereits'
      });
    } else {
      console.error(error);
      useServerErrorNotification();
    }
  } finally {
    dialogRef.value.toggleVisibility();
    refresh();
  }
}

async function deleteCollections() {
  const collections: Collection[] = collectionTable.value.getSelectionRows();

  try {
    const response = await useBaseUrlFetchRaw('/data/collections', {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ uuids: collections.map(collection => collection.uuid) })
    });
    ElMessage({
      type: 'success',
      message: 'Kollektionen erfolgreich gelöscht'
    });
  } catch (error) {
    console.error(error);
    useServerErrorNotification();
  } finally {
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