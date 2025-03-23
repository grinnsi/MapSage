<template>
  <TemplateDialog
    ref="dialogRef"
    :dialog-type="DialogType.Form"
    :dialog-title="'Kollektion \'' + (props.collection ? props.collection.id : '') + '\' bearbeiten'"
    :dialogStyle="StyleType.Normal"
    :close-on-click-modal="false"
    :form-model="form"
    :form-rules="rules"
    @submit="saveCollection"
    @resetFields="resetFields"
  >
    <ElFormItem label="Titel" prop="title">
      <ElInput v-model="form.title" placeholder="Kollektionstitel" />
    </ElFormItem>
    <ElFormItem label="Beschreibung" prop="description">
      <ElInput 
        v-model="form.description" 
        placeholder="Kollektionsbeschreibung" 
        type="textarea"
        :rows="4"
      />
    </ElFormItem>
    <ElFormItem label="Lizenz" prop="license_title">
      <ElSelectV2
        v-model="form.license_title"
        :options="(() => licenseData ? licenseData.map(item => ({ label: item.title, value: item.title })) : [])()"
        placeholder="Lizenz"
        filterable
        clearable
        :value-on-clear="undefined"
      />
    </ElFormItem>
    <ElFormItem label="Zeitliche Ausdehnung" prop="selected_date_time_field">
      <ElSelect
        v-model="form.selected_date_time_field" 
        placeholder="Attributfeld für zeitliche Ausdehnung und Filterung"
        clearable
        :disabled="props.collection.date_time_fields.length === 0"
      >
        <ElOption 
          v-for="item in props.collection.date_time_fields" 
          :key="item" 
          :label="item" 
          :value="item"
        />
      </ElSelect>
    </ElFormItem>
  </TemplateDialog>
</template>

<script setup lang="ts">
import type { CollectionDetail } from '~/utils/types';

const defaultForm: Partial<CollectionDetail> = {
  title: '',
  description: '',
  license_title: '',
  selected_date_time_field: ''
};

const dialogRef = ref();
const form: Partial<CollectionDetail> = reactive(defaultForm);
const rules = {
  title: [{ 
    required: true, 
    message: 'Bitte geben Sie einen Titel ein', 
    trigger: 'blur' 
  }],
}

const props = defineProps({
  collection: {
    type: Object as PropType<CollectionDetail>,
    required: true
  },
  getEntireCollection: {
    type: Boolean,
    default: false,
    required: false
  }
})

const emit = defineEmits<{
  (e: 'submitInformation', data: Partial<CollectionDetail>, toggleButtonState: () => void): void
}>();

watchEffect(() => {
  if (props.collection) {
    Object.assign(form, props.collection);
  } else {
    Object.assign(form, defaultForm);
  }
});

function toggleVisibility() {
  dialogRef.value.toggleVisibility();
}

defineExpose({
  toggleVisibility
});

const { data: licenseData } = await useBaseUrlFetch<{title: string}[]>("/data/collections/licenses", {
  method: "GET",
  onResponseError({ request, response, options }) {
    throw new Error("Error fetching general options");
  }
});

function resetDialog() {
  dialogRef.value.toggleLoadingState(false);
  // TODO: Check whether the form gets updated, when updating is successful
  resetFields();
}

function saveCollection() {
  let changedData: Partial<CollectionDetail> = {};
  
  if (!props.getEntireCollection) {
    for (const key in form) {
      const formKey = key as keyof Partial<CollectionDetail>;
      if (form[formKey] !== props.collection[formKey]) {
        changedData[formKey] = form[formKey] as any;
      }
    }
  } else {
    changedData = { ...form };
  }

  // Replace undefined values with null so Python receives them
  for (const key in changedData) {
    const typedKey = key as keyof Partial<CollectionDetail>;
    if (changedData[typedKey] === undefined) {
      (changedData as any)[typedKey] = null;
    }
  }

  if (Object.keys(changedData).length === 0) {
    ElMessage({
      type: 'info',
      message: 'Keine Änderungen zum Speichern gefunden',
    });
    return;
  }

  try {
    emit('submitInformation', changedData, resetDialog);
  } catch (error) {
    console.error(error);
  }
}

function resetFields() {
  if (props.collection) {
    Object.assign(form, props.collection);
  } else {
    Object.assign(form, defaultForm);
  }
}
</script>

<style scoped>

</style>