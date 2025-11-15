<template>
  <div class="export-page">
    <el-card class="export-form">
      <h2>数据导出</h2>
      <el-form label-width="120px">
        <el-form-item label="导出类型">
          <el-select v-model="form.exportType">
            <el-option label="标准化产品" value="clean_products" />
            <el-option label="失败行" value="failed_rows" />
          </el-select>
        </el-form-item>
        <el-form-item label="批次 ID">
          <el-input v-model="form.filters.batch_id" placeholder="可选" />
        </el-form-item>
        <el-form-item label="选择字段">
          <el-select v-model="form.selectedFields" multiple>
            <el-option label="ASIN" value="asin" />
            <el-option label="标题" value="title" />
            <el-option label="价格" value="price" />
            <el-option label="批次 ID" value="batch_id" />
          </el-select>
        </el-form-item>
        <el-button type="primary" :loading="submitting" @click="submit">创建导出</el-button>
      </el-form>
      <p v-if="message" class="hint">{{ message }}</p>
    </el-card>

    <el-card>
      <h3>导出任务</h3>
      <el-table :data="jobs">
        <el-table-column prop="id" label="任务 ID" />
        <el-table-column prop="status" label="状态" />
        <el-table-column prop="file_path" label="文件">
          <template #default="scope">
            <el-link v-if="scope.row.file_path" @click="download(scope.row.id)">下载</el-link>
            <span v-else>--</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import axios from 'axios'

const form = reactive({
  exportType: 'clean_products',
  filters: { batch_id: '' },
  selectedFields: ['asin', 'title']
})
const jobs = ref<any[]>([])
const submitting = ref(false)
const message = ref('')

const submit = async () => {
  submitting.value = true
  try {
    await axios.post('http://localhost:8000/exports', {
      exportType: form.exportType,
      filters: { batch_id: form.filters.batch_id || undefined },
      selectedFields: form.selectedFields,
      fileFormat: 'csv'
    })
    message.value = '导出任务已创建'
    await fetchJobs()
  } catch (err) {
    message.value = '导出失败'
    console.error(err)
  } finally {
    submitting.value = false
  }
}

const fetchJobs = async () => {
  // 简化：示例中未提供列表 API，可根据需要扩展
}

const download = async (jobId: string) => {
  window.open(`http://localhost:8000/exports/${jobId}/download`, '_blank')
}

onMounted(() => {
  fetchJobs()
})
</script>

<style scoped>
.export-page {
  display: grid;
  gap: 16px;
}
.hint {
  color: #67c23a;
}
</style>
