<template>
  <ElDialog v-model="dialogVisible" :show-close="false" destroy-on-close modal-class="dialog-background" width="500" :close-on-click-modal="true" @close="resetFields(formRef)">
    <template #header="{ close, titleId, titleClass }">
      <div class="dialog-header">
        <h3 :class="titleClass" :id="titleId" :style="{ color: 'var(--el-color-' + dialogStyle + ')' }">{{ dialogTitle }}
        </h3>
        <button :disabled="dialogLoading" type="button" class="close-button" :class="{ 'disabled': dialogLoading }"
          @click="close">&#x1F5D9</button>
      </div>
    </template>
    <div class="dialog-content">
      <template v-if="dialogType === DialogType.Form">
        <ElForm :model="formModel" ref="formRef" :rules="formRules" label-width="auto" label-suffix=":" label-position="left">
          <slot>FORMULARELEMENTE</slot>
        </ElForm>
      </template>
      <template v-else>
        <slot>NACHRICHT</slot>
      </template>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <template v-if="dialogType === DialogType.Form">
          <ElButton :disabled="dialogLoading" @click="resetFields(formRef)">
            Zurücksetzen
          </ElButton>
          <ElButton :loading="dialogLoading" type="primary" @click="submitForm(formRef)">
            Bestätigen
          </ElButton>
        </template>
        <template v-if="dialogType === DialogType.Confirmation">
          <ElButton @click="$emit('cancel'); dialogVisible = false">
            Abbrechen
          </ElButton>
          <ElButton :type="dialogStyle" @click="$emit('confirm'); dialogVisible = false">
            Bestätigen
          </ElButton>
        </template>
        <template v-if="dialogType === DialogType.Blank">
          <slot name="footer"></slot>
        </template>
      </div>
    </template>
  </ElDialog>
</template>

<script setup lang="ts">
import type { PropType } from 'vue';
import { type FormInstance } from 'element-plus';

const formRef = ref<FormInstance>() as any;
const dialogVisible = ref(false);
const dialogLoading = ref(false)

defineProps({
  dialogStyle: {
    type: String as PropType<StyleType>,
    default: StyleType.Normal
  },
  dialogType: {
    type: Number as PropType<DialogType>,
    default: DialogType.Form
  },
  dialogTitle: {
    type: String,
    default: "Titel",
    required: true
  },
  formModel: {
    type: Object,
    default: {}
  },
  formRules: {
    type: Object,
    default: {}
  },
});

const emit = defineEmits<{
  submit: [],  
  confirm: [],
  cancel: []
}>();

function toggleVisibility(visible?: boolean) {
  if (visible) dialogVisible.value = visible
  else dialogVisible.value = !(dialogVisible.value);
}

function toggleLoadingState(loading?: boolean) {
  if (loading) dialogLoading.value = loading
  else dialogLoading.value = !(dialogLoading.value);
}

function resetFields(form: FormInstance) {
  if (!form) return;
  form.resetFields();
}

async function submitForm(form: FormInstance) {
  if (!form) return;
  await form.validate((valid, fields) => {
    if (valid) {
      toggleLoadingState(true);
      emit('submit');
    } else {
      console.warn('Validierung fehlgeschlagen', fields)
    }
  })
}

defineExpose({
  toggleVisibility,
  toggleLoadingState,
  formRef
});
</script>

<style scoped lang="scss">
.dialog-header {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: space-between;

  >h3 {
    display: flex;
    vertical-align: text-bottom;
    line-height: 1;
    margin-top: 0px;
    margin-bottom: 0px;
  }
}

.close-button {
  display: flex;
  flex-wrap: wrap;
  position: relative;
  top: -0.15em;
  justify-content: center;
  line-height: 1;
  font-size: 20px;
  cursor: pointer;
  font-weight: 900;
  vertical-align: text-top;
  background: none;
  border: none;
  margin: 0;
  padding: 0;

  &:not(.disabled):hover {
    color: var(--el-color-danger);
  }

  &.disabled {
    cursor: not-allowed;
  }
}
</style>