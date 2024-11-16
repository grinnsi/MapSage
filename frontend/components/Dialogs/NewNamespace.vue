<template>
  <TemplateDialog
    ref="dialogRef"
    dialog-title="Neuer Namespace"
    width="400"
    :form-model="formModel" 
    :form-rules="rules"
    :close-on-click-modal="false" 
    @submit="saveNamespace"
  >
    <p style="margin-top: 0px;">Der Name wird in einen URL Parameter umgewandelt</p>
    <ElFormItem ref="nameRef" label="Name" prop="name">
      <ElInput v-model="formModel.name" placeholder="Namespace 1" maxlength="25" />
    </ElFormItem>
    <ElFormItem ref="urlRef" label="Url" prop="url">
      <ElInput v-model="formModel.url" placeholder="/namespace-1"  
        :formatter="(value: string) => {
          if (value === '') return '';
          return '/' + value
        }"
        :parser="(value: string) => value.replace(/[^a-z0-9_]+/gi, '-').replace(/^-/g, '').toLowerCase()"
      />
    </ElFormItem>
  </TemplateDialog>
</template>

<script setup lang="ts">
import { type FormItemInstance } from 'element-plus';
import useEmitter from '~/composables/useEmitter';

const dialogRef = ref();
const nameRef = ref<FormItemInstance>();
const urlRef = ref<FormItemInstance>();

onMounted(() => {
  const emitter = useEmitter().value;
  emitter.on('show-new-namespace-dialog', (dialogRef.value! as any).toggleVisibility)
});

const formModel = reactive({
  name: '',
  url: '',
});

const rules = {
  name: [{
    required: true,
    message: "Bitte dem Namespace einen Namen geben",
    trigger: 'blur'
  }],
  url: [{
    required: true,
    message: "Bitte dem Namespace eine gültige Url geben",
    trigger: 'blur'
  }]
};


watchEffect(async () => {
  if (formModel.name === '') formModel.url = '' 
  else formModel.url = formModel.name.replace(/[^a-z0-9_]+/gi, '-').replace(/^-|-$/g, '').toLowerCase();
});

async function saveNamespace() {
  formModel.url = formModel.url.replace(/^-|-$/g, '');

  try {
    await $fetch('/database/newNamespace', {
      method: 'POST',
      body: formModel
    });

    ElMessage({
      type: 'success',
      message: 'Namespace erfolgreich gespeichert'
    });
    (dialogRef.value! as any).toggleVisibility(false);
    useEmitter().value.emit('update-namespace-table');
  } catch (error) {
    const errorField = (error as any).data.data.field;
    switch (errorField) {
      case 'name':
        nameRef.value!.validateState = "error";
        nameRef.value!.validateMessage = "Name ist bereits vergeben"; 
        break;

      case 'url':
        urlRef.value!.validateState = "error";
        urlRef.value!.validateMessage = "Url ist bereits vergeben"; 
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

<style scoped lang="scss">
.url-parameter {
  position: relative;
  left: 7px;
  color: rgba(117, 117, 117, 0.655);
}
</style>