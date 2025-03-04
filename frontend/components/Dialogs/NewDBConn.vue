<template>
  <TemplateDialog ref="dialogRef" dialog-title="Neue Verbindung speichern" :close-on-click-modal="false" :form-model="form" :form-rules="rules"
    @submit="saveConnection">
    <ElFormItem label="Verbindungsname" prop="name">
      <ElInput v-model="form.name" placeholder="Datenbank 1" maxlength="30" />
    </ElFormItem>
    <!-- <ElFormItem label="Verbindungs-Url" prop="entireConnUrl">
      <ElInput 
        v-model="form.entireConnUrl"
        placeholder="postgres://user:passwort@hostUrl:port/datenbank"
        maxlength="150"
      />
    </ElFormItem>
    <ElDivider>oder</ElDivider> -->
    <ElFormItem ref="hostRef" label="Host" prop="host">
      <ElInput v-model="form.host" placeholder="localhost" maxlength="50" />
    </ElFormItem>
    <ElFormItem ref="portRef" label="Port" prop="port">
      <ElInputNumber v-model="form.port" placeholder="5432" :controls="false" :max="65535" :min="1" />
    </ElFormItem>
    <ElFormItem ref="roleRef" label="Benutzer" prop="role">
      <ElInput v-model="form.role" placeholder="[name]" maxlength="30" />
    </ElFormItem>
    <ElFormItem ref="passwordRef" label="Passwort" prop="password">
      <ElInput v-model="form.password" placeholder="Passwort12345" maxlength="50" type="password" show-password />
    </ElFormItem>
    <ElFormItem ref="database_nameRef" label="Datenbank" prop="database_name">
      <ElInput v-model="form.database_name" maxlength="30" placeholder="postgres" />
    </ElFormItem>
  </TemplateDialog>
</template>

<script setup lang="ts">
import { type FormItemInstance } from 'element-plus';
import useEmitter from '~/composables/useEmitter';
import useServerErrorNotification from '~/composables/useServerErrorNotification';

const dialogRef = ref(null);
const emitter = useEmitter().value;

onMounted(() => {
  emitter.on('show-new-connection-dialog', (dialogRef.value! as any).toggleVisibility)
});

const form = reactive({
  name: '',
  // entireConnUrl: '',
  host: '',
  port: 5432,
  role: '',
  password: '',
  database_name: '',
});

const hostRef = ref<FormItemInstance>();
const portRef = ref<FormItemInstance>();
const roleRef = ref<FormItemInstance>();
const passwordRef = ref<FormItemInstance>();
const database_nameRef = ref<FormItemInstance>();

const rules = {
  name: [{
    required: true,
    message: "Bitte der Verbindung einen Namen geben",
    trigger: 'blur'
  }],
  // entireConnUrl: [{
  //   required: true,
  //   message: "Bitte eine gültige Datenbank Url eingeben",
  //   trigger: 'blur'
  // }],
  host: [
    {
      required: true,
      message: "Bitte eine Url eingeben",
      trigger: 'blur'
    },
    // Intranet Adressen könnten dadurch als ungültig gelten, obwohl sie funktioniern
    // Bsp. Die Intranet Adresse meines Dev-Servers beim ITC
    //
    // {
    //   type: "url",
    //   message: "Bitte eine gültige Url eingeben",
    //   trigger: 'blur'
    // }
  ],
  port: [{
    required: true,
    message: "Bitte einen gültigen Port eingeben",
    trigger: 'blur'
  }],
  role: [{
    required: true,
    message: "Bitte einen Benutzernamen eingeben",
    trigger: 'blur'
  }],
  password: [{
    required: true,
    message: "Bitte das Passwort des Benutzers eingeben",
    trigger: 'blur'
  }],
  database_name: [{
    required: true,
    message: "Bitte die Datenbank eingeben",
    trigger: 'blur'
  }],
};

async function saveConnection() {
  try {
    const response = await useBaseUrlFetchRaw('/data/settings/connections', {
      method: 'POST',
      body: form
    });
    // if (!response.ok) throw new Error("Response not ok");

    ElMessage({
      type: 'success',
      message: 'Verbindung erfolgreich gespeichert'
    });

    (dialogRef.value! as any).toggleVisibility(false);
    emitter.emit('update-connections-list');
  } catch (error) {
    const statusText: string = (error as any).response.statusText;
    const type = statusText.split(' ')[0];

    switch (type) {
      case 'host':
        hostRef.value!.validateState = "error";
        hostRef.value!.validateMessage = "Host kann nicht erreicht werden";
        break;

      case 'port':
        portRef.value!.validateState = "error";
        portRef.value!.validateMessage = "Port kann nicht erreicht werden";
        break;

      case 'credentials':
        passwordRef.value!.validateState = "error";
        passwordRef.value!.validateMessage = "Keine Rolle mit diesen Daten vorhanden";
        roleRef.value!.validateState = "error";
        roleRef.value!.validateMessage = "Keine Rolle mit diesen Daten vorhanden";
        break;

      case 'db_name':
        database_nameRef.value!.validateState = "error";
        database_nameRef.value!.validateMessage = "Datenbank existiert nicht oder keinen Zugriff";
        break;

      default:
        useServerErrorNotification();
        break;
    }
  } finally {
    (dialogRef.value! as any).toggleLoadingState(false);
  }
}
</script>

<style scoped></style>