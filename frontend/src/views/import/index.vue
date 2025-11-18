<template>
  <div class="import-page">
    <el-card class="import-form">
      <h2>文件导入</h2>
      <el-form label-width="100px">
        <el-form-item label="导入策略">
          <el-select v-model="strategy">
            <el-option label="仅追加" value="append" />
            <el-option label="覆盖批次" value="overwrite" />
            <el-option label="仅更新" value="update_only" />
          </el-select>
        </el-form-item>
        <el-form-item label="Sorftime 文件">
          <input type="file" ref="fileInput" accept=".csv,.xlsx" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="submit">开始导入</el-button>
        </el-form-item>
      </el-form>
      <p v-if="message" class="hint">{{ message }}</p>
    </el-card>

    <el-card class="import-table">
      <h3>最近批次</h3>
      <el-table :data="batches" style="width: 100%">
        <el-table-column prop="id" label="批次 ID" />
        <el-table-column prop="filename" label="文件名" />
        <el-table-column prop="status" label="状态" />
        <el-table-column prop="success_rows" label="成功行" />
        <el-table-column prop="failed_rows" label="失败行" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const strategy = ref('append')
const submitting = ref(false)
const message = ref('')
// 批次列表行（按当前表格列字段）
interface BatchRow {
  id: string
  filename: string
  status: string
  success_rows?: number
  failed_rows?: number
}
const batches = ref<BatchRow[]>([])
const fileInput = ref<HTMLInputElement | null>(null)

const submit = async () => {
  if (!fileInput.value?.files?.length) {
    message.value = '请选择 Sorftime 文件'
    return
  }
  const file = fileInput.value.files[0]
  const form = new FormData()
  form.append('file', file)
  form.append('importStrategy', strategy.value)
  submitting.value = true
  try {
    await axios.post(`${API_BASE}/imports`, form)
    message.value = '导入任务已提交'
    await fetchBatches()
  } catch (err) {
    const detail = (err as any)?.response?.data?.detail
    message.value = detail ? `导入失败：${detail}` : '导入失败，请查看日志'
    console.error(err)
  } finally {
    submitting.value = false
  }
}

const fetchBatches = async () => {
  try {
    const { data } = await axios.get(`${API_BASE}/imports`)
    batches.value = data.items || []
  } catch (err) {
    console.error(err)
  }
}

onMounted(() => {
  fetchBatches()
})
</script>

<style scoped>
.import-page {
  display: grid;
  gap: 16px;
}
.hint {
  color: #409eff;
}
</style>
