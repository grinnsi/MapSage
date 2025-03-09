<template>
  <ElForm
    :model="form"
    :rules="rules"
    label-width="auto" 
    label-suffix=":" 
    label-position="left"
    :hide-required-asterisk="true"
  >
    <ElRow :gutter="20">
      <ElCol :span="12">
        <ElFormItem label="Dienstname" prop="service_title">
          <ElInput v-model="form.service_title" :maxlength="60"/>
        </ElFormItem>
      </ElCol>
      <ElCol :span="12">
        <ElFormItem label="Dienstbeschreibung" prop="service_description">
          <ElInput 
            v-model="form.service_description" 
            type="textarea" 
            :autosize="{minRows: 2, maxRows: 4}"
            :maxlength="300"
          />
        </ElFormItem>
      </ElCol>
    </ElRow>
  </ElForm>
  <div style="display: flex; flex-direction: row-reverse;">
    <ElButton 
      type="primary"
      @click="saveGeneralOptions"
      :loading="loadingSubmitButton"
    >
      Speichern
    </ElButton>
  </div>
</template>

<script setup lang="ts">
import { ElForm } from 'element-plus';
import type { GeneralOption } from '~/utils/types';

const loadingSubmitButton = ref(false);

const form: { [key: string]: string } = reactive({
  service_title: '',
  service_description: '',
});

const rules = {
  service_title: [{ 
    required: true, 
    message: 'Bitte geben Sie einen Dienstnamen ein', 
    trigger: 'blur' 
  }],
  service_description: [{ 
    required: true, 
    message: 'Bitte geben Sie eine Dienstbeschreibung ein',
    trigger: 'blur' 
  }]
}

const { data, refresh } = await useBaseUrlFetch<GeneralOption[]>("/data/settings/general", {
  method: "GET",
  onResponse({ request, response, options }) {
    (response._data as GeneralOption[]).forEach((option) => {
      if (option.key in form) {
        form[option.key] = option.value;
      } 
    });
  },
  onResponseError({ request, response, options }) {
    throw new Error("Error fetching general options");
  }
});

async function saveGeneralOptions() {
  let changedOptions: GeneralOption[] = [];
  if (!data.value) throw new Error("Error fetching general options");

  for (const key in form) {
    if (form[key] !== data.value.find((option) => option.key === key)?.value) {
      changedOptions.push({
        key: key,
        value: form[key]
      });
    }
  }

  if (changedOptions.length === 0) {
    ElMessage({
      type: 'info',
      message: 'Keine Änderungen zum Speichern gefunden',
    });
    return;
  }

  try {
    loadingSubmitButton.value = true;

    const response = await useBaseUrlFetchRaw('/data/settings/general', {
      method: "PATCH",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(changedOptions)
    });
    if (!response.ok) throw new Error(await response.text());
    ElMessage({
      type: 'success',
      message: 'Allgemeine Einstellungen erfolgreich gespeichert',
    });
  } catch (error) {
    console.error(error);
    useServerErrorNotification();
  } finally {
    refresh();
    loadingSubmitButton.value = false;
  }
}

</script>

<style scoped>

</style>