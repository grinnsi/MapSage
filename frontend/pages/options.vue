<template>
  <TemplateSection section-title="Allgemeine Einstellungen:">
    <FormsGeneralOptions />
  </TemplateSection>
  <ElDivider style="margin-bottom: calc(24px - 1em);"/>
  <TemplateSection section-title="Gespeicherte Verbindungen:">
    <template #header-right>
      <TemplateButton tooltip="Neue Datenbankverbindung" iconName="flowbite:plus-outline" @click="useEmitter().value.emit('show-new-connection-dialog')"/>
    </template>
    <TemplateFetchStatus 
      :status="status"
      errorTitle="Fehler beim Laden der gespeicherten Datenbankverbindungen"
    >
      <div class="saved-db-connections">
        <template v-for="connection in data" :key="connection.uuid">
          <ElCard shadow="hover" style="width: 300px;">
            <template #header>
              <div class="card-header">
                <span>{{ connection.name }}</span>
                <TemplateButton 
                  tooltip="Verbindung löschen"
                  iconName="flowbite:trash-bin-outline"
                  type="danger"
                  @click="showConfirmationDialog(connection)"
                />
              </div>
            </template>
            <div class="base-column-container">
              <div class="base-column">
                <span>Host:</span>
                <span>Port:</span>
                <span>Rolle:</span>
                <span>Datenbank:</span>
              </div>
              <div class="base-column">
                <span>{{ connection.host }}</span>
                <span>{{ connection.port }}</span>
                <span>{{ connection.role }}</span>
                <span>{{ connection.database_name }}</span>
              </div>
            </div>
          </ElCard>
        </template>
      </div>
    </TemplateFetchStatus>
    <ClientOnly>
      <DialogsNewDBConn />
      <TemplateDialog
        ref="confirmationDialogRef"
        :dialogStyle="StyleType.Danger"
        :dialogTitle="`Verbindung '` + selectedConnection.name + `' löschen ?`"
        :close-on-click-modal="true"
        :dialog-type="DialogType.Confirmation"
        @confirm="deleteConnection(selectedConnection.uuid)"
      >
        <span>Sind Sie sicher, dass Sie die Verbindung löschen möchten ?
        <br>Alle Ebenen, die diese Verbindung verwenden, werden ebenfalls gelöscht.
        <br>Diese Aktion kann nicht rückgängig gemacht werden.
        </span>
      </TemplateDialog>
    </ClientOnly>
  </TemplateSection>
</template>

<script setup lang="ts">
import useBaseUrlFetchRaw from '~/composables/useBaseUrlFetchRaw';
import useEmitter from '~/composables/useEmitter';
import useServerErrorNotification from '~/composables/useServerErrorNotification';
import type { Connection } from '~/utils/types';

const selectedConnection = reactive<Connection | {name: string, uuid: string}>({
  name: "Name der Verbindung",
  uuid: ""
});
const confirmationDialogRef = ref();

definePageMeta({
  name: "Einstellungen"
});

const { status, data, refresh } = await useBaseUrlFetch<Connection[]>('/data/connections', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
});

function showConfirmationDialog(connection: Connection) {
  Object.assign(selectedConnection, connection);
  confirmationDialogRef.value!.toggleVisibility();
}

async function deleteConnection(uuid: string) {
  confirmationDialogRef.value!.toggleVisibility();

  try {
    const response = await useBaseUrlFetchRaw('/data/connections', {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ uuid }),
    });
    // if (!response.ok) throw new Error('Antwort des Löschens nicht verständlich');
    ElMessage({
      type: 'success',
      message: 'Verbindung erfolgreich gelöscht'
    });
  } catch (error) {
    console.error(error);
    useServerErrorNotification();
  } finally {
    refresh();
  }
}

onMounted(() => {
  const emitter = useEmitter().value;
  // @ts-ignore
  emitter.on('update-connections-list', refresh)
})
</script>

<style scoped lang="scss">
.saved-db-connections {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 5px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--el-color-primary); 
  font-weight: bold;
  font-size: larger;

  >span {
    position: relative;
    top: 0.1em;
  }
}

.card-content {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap; 
  column-gap: 20px;
  
  >.connection-column {
    display: flex;
    flex-direction: column;
    flex-wrap: wrap;

    >span {
      margin-bottom: 5px;

      &:last-child {
        margin-bottom: 0px;
      }
    }
  }
}
</style>