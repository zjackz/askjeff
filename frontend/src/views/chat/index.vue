<template>
  <div class="chat-page">
    <el-card class="chat-input">
      <h2>自然语言数据洞察</h2>
      <el-input
        v-model="question"
        type="textarea"
        :rows="3"
        placeholder="例如：最近两次导入中销量排名前十的 ASIN"
      />
      <el-button type="primary" :loading="loading" @click="send">提交问题</el-button>
    </el-card>

    <el-card v-if="answer" class="chat-answer">
      <h3>回答</h3>
      <p>{{ answer }}</p>
      <h4 v-if="referenceBatches.length">引用批次</h4>
      <el-tag v-for="bid in referenceBatches" :key="bid" class="ref-tag">{{ bid }}</el-tag>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import axios from 'axios'

const question = ref('')
const answer = ref('')
// 后端返回的引用结构：[{ batchId: string, asin?: string | null, fields: string[] }]
interface ChatReference {
  batchId: string
  asin?: string | null
  fields: string[]
}
const references = ref<ChatReference[] | null>(null)
const loading = ref(false)

// 便于模板渲染引用批次列表
const referenceBatches = computed<string[]>(() => {
  return references.value?.map(r => r.batchId) ?? []
})

const send = async () => {
  if (!question.value.trim()) {
    return
  }
  loading.value = true
  try {
    const { data } = await axios.post('http://localhost:8000/chat/query', {
      question: question.value
    })
    answer.value = data.answer
    references.value = data.references as ChatReference[] | null
  } catch (err) {
    answer.value = '暂时无法获取回答，请稍后重试'
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.chat-page {
  display: grid;
  gap: 16px;
}
.chat-input textarea {
  margin-bottom: 12px;
}
.ref-tag {
  margin-right: 8px;
}
</style>
