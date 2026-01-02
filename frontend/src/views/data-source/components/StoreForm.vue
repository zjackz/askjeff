<template>
  <BaseDialog v-model:visible="visible" :title="mode === 'create' ? '添加 Amazon 店铺' : '编辑店铺'" width="600px">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
    >
      <el-form-item label="店铺名称" prop="store_name">
        <el-input v-model="formData.store_name" placeholder="例如：我的美国店铺" />
      </el-form-item>

      <el-form-item label="市场" prop="marketplace_id">
        <el-select v-model="formData.marketplace_id" placeholder="选择市场" @change="handleMarketChange">
          <el-option
            v-for="market in markets"
            :key="market.id"
            :label="`${market.flag} ${market.name}`"
            :value="market.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="卖家 ID" prop="seller_id">
        <el-input v-model="formData.seller_id" placeholder="Amazon Seller ID" />
      </el-form-item>

      <el-divider content-position="left">API 凭证</el-divider>

      <el-form-item label="SP API Token" prop="sp_api_refresh_token">
        <el-input
          v-model="formData.sp_api_refresh_token"
          type="textarea"
          :rows="3"
          placeholder="SP API Refresh Token"
          show-password
        />
        <template #label>
          <span>SP API Token</span>
          <el-tooltip content="用于获取库存、订单、业务报告等数据" placement="top">
            <el-icon><QuestionFilled /></el-icon>
          </el-tooltip>
        </template>
      </el-form-item>

      <el-form-item label="Ads API Token" prop="advertising_api_refresh_token">
        <el-input
          v-model="formData.advertising_api_refresh_token"
          type="textarea"
          :rows="3"
          placeholder="Advertising API Refresh Token"
          show-password
        />
        <template #label>
          <span>Ads API Token</span>
          <el-tooltip content="用于获取广告数据、关键词、广告组等" placement="top">
            <el-icon><QuestionFilled /></el-icon>
          </el-tooltip>
        </template>
      </el-form-item>

      <el-form-item label="启用同步" prop="is_active">
        <el-switch v-model="formData.is_active" />
        <template #label>
          <span>启用同步</span>
          <el-tooltip content="启用后将自动执行定时数据同步" placement="top">
            <el-icon><QuestionFilled /></el-icon>
          </el-tooltip>
        </template>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        {{ mode === 'create' ? '创建' : '保存' }}
      </el-button>
    </template>
  </BaseDialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import BaseDialog from '@/components/common/BaseDialog.vue'
import type { AmazonStore, StoreCreate, StoreUpdate } from '@/api/stores'

interface Props {
  visible: boolean
  store?: AmazonStore | null
  mode: 'create' | 'edit'
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:visible': [value: boolean]
  submit: [data: StoreCreate | StoreUpdate]
}>()

const formRef = ref<FormInstance>()
const loading = ref(false)

const markets = [
  { id: 'ATVPDKIKX0DER', name: 'United States', flag: '🇺🇸' },
  { id: 'A1PA6795UKMFR9', name: 'Germany', flag: '🇩🇪' },
  { id: 'A1VC38T7YXB528', name: 'Japan', flag: '🇯🇵' },
  { id: 'A13UK1VYFJ83R7', name: 'United Kingdom', flag: '🇬🇧' },
  { id: 'A2NODRKZP66I6WI', name: 'Italy', flag: '🇮🇹' },
  { id: 'A1F83G8C2OOF0N7', name: 'Spain', flag: '🇪🇸' },
  { id: 'A2Q3Y263D00KWC', name: 'France', flag: '🇫🇷' },
  { id: 'A1AM78C64UM0SV', name: 'Canada', flag: '🇨🇦' },
  { id: 'A1RKKUPIH0ZJDM', name: 'Australia', flag: '🇦🇺' }
]

const formData = reactive<StoreCreate>({
  store_name: '',
  marketplace_id: '',
  marketplace_name: '',
  seller_id: '',
  sp_api_refresh_token: '',
  advertising_api_refresh_token: '',
  is_active: true
})

const formRules: FormRules = {
  store_name: [
    { required: true, message: '请输入店铺名称', trigger: 'blur' }
  ],
  marketplace_id: [
    { required: true, message: '请选择市场', trigger: 'change' }
  ],
  seller_id: [
    { required: true, message: '请输入卖家 ID', trigger: 'blur' }
  ]
}

const handleMarketChange = (marketId: string) => {
  const market = markets.find(m => m.id === marketId)
  if (market) {
    formData.marketplace_name = market.name
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    loading.value = true

    // 提交数据（去除空字符串）
    const submitData: any = {}
    Object.keys(formData).forEach(key => {
      const value = formData[key as keyof StoreCreate]
      if (value !== '') {
        submitData[key] = value
      }
    })

    emit('submit', submitData)
  } catch (error) {
    ElMessage.error('请检查表单填写')
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  emit('update:visible', false)
}

// 监听 store 变化，填充表单
watch(() => props.store, (newStore) => {
  if (newStore && props.mode === 'edit') {
    formData.store_name = newStore.store_name
    formData.marketplace_id = newStore.marketplace_id
    formData.marketplace_name = newStore.marketplace_name
    formData.seller_id = newStore.seller_id
    formData.sp_api_refresh_token = newStore.sp_api_refresh_token || ''
    formData.advertising_api_refresh_token = newStore.advertising_api_refresh_token || ''
    formData.is_active = newStore.is_active
  } else {
    // 重置表单
    formData.store_name = ''
    formData.marketplace_id = ''
    formData.marketplace_name = ''
    formData.seller_id = ''
    formData.sp_api_refresh_token = ''
    formData.advertising_api_refresh_token = ''
    formData.is_active = true
  }
}, { immediate: true })

// 监听 visible 变化，重置表单
watch(() => props.visible, (newVisible) => {
  if (newVisible && props.mode === 'create') {
    formData.store_name = ''
    formData.marketplace_id = ''
    formData.marketplace_name = ''
    formData.seller_id = ''
    formData.sp_api_refresh_token = ''
    formData.advertising_api_refresh_token = ''
    formData.is_active = true
  }
})
</script>

<style scoped lang="scss">
:deep(.el-form-item__label) {
  display: flex;
  align-items: center;
  gap: 4px;
}

.el-divider {
  margin: var(--spacing-lg) 0;
}
</style>
