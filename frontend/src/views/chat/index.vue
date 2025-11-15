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
      <h4 v-if="references?.batches?.length">引用批次</h4>
      <el-tag v-for="bid in references?.batches" :key="bid" class="ref-tag">{{ bid }}</el-tag>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const question = ref('')
const answer = ref('')
const references = ref<Record<string, any> | null>(null)
const loading = ref(false)

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
    references.value = data.references
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
