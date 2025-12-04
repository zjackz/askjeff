<template>
  <div class="chat-bot-container">
    <!-- 悬浮按钮 -->
    <div class="chat-fab" @click="toggleChat" :class="{ 'is-active': visible }">
      <img v-if="!visible" src="/chat-icon.png" alt="Chat" class="fab-img" />
      <el-icon class="fab-icon" v-else><Close /></el-icon>
    </div>

    <!-- 聊天窗口 -->
    <transition name="chat-slide">
      <div v-show="visible" class="chat-window" :class="{ 'is-expanded': isExpanded }">
        <!-- 头部 -->
        <div class="chat-header">
          <div class="header-left">
            <div class="avatar-wrapper">
              <el-icon><Service /></el-icon>
            </div>
            <div class="header-info">
              <h3>AskJeff 助手</h3>
              <span class="status-dot"></span>
              <span class="status-text">在线</span>
            </div>
          </div>
          <div class="header-actions">
            <el-icon class="action-icon" @click="toggleExpand" :title="isExpanded ? '退出全屏' : '全屏模式'">
              <FullScreen v-if="!isExpanded" />
              <ScaleToOriginal v-else />
            </el-icon>
            <el-icon class="action-icon" @click="clearHistory" title="清空对话"><Delete /></el-icon>
            <el-icon class="action-icon" @click="visible = false"><Minus /></el-icon>
          </div>
        </div>

        <!-- 消息列表 -->
        <div class="chat-body" ref="chatBodyRef">
          <div v-if="messages.length === 0" class="chat-welcome">
            <div class="welcome-icon">👋</div>
            <h3>你好！我是你的数据助手。</h3>
            <p>我可以帮你分析产品数据、查询销量排行或解答业务问题。</p>
            <div class="quick-questions">
              <div 
                v-for="(q, index) in quickQuestions" 
                :key="index" 
                class="quick-tag"
                @click="useQuickQuestion(q)"
              >
                {{ q }}
              </div>
            </div>
          </div>

          <div 
            v-for="(msg, index) in messages" 
            :key="index" 
            class="message-row"
            :class="msg.role"
          >
            <div class="message-avatar" v-if="msg.role === 'assistant'">
              <el-avatar :size="32" :icon="Service" class="assistant-avatar" />
            </div>
            <div class="message-content">
              <div class="message-bubble">
                {{ msg.content }}
              </div>
              <div class="message-time">{{ formatTime(new Date()) }}</div>
            </div>
            <div class="message-avatar" v-if="msg.role === 'user'">
              <el-avatar :size="32" :icon="UserFilled" class="user-avatar" />
            </div>
          </div>

          <div v-if="loading" class="message-row assistant">
            <div class="message-avatar">
              <el-avatar :size="32" :icon="Service" class="assistant-avatar" />
            </div>
            <div class="message-content">
              <div class="message-bubble typing">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入框 -->
        <div class="chat-footer">
          <el-input
            v-model="input"
            type="textarea"
            :rows="1"
            :autosize="{ minRows: 1, maxRows: 4 }"
            placeholder="输入问题..."
            resize="none"
            @keydown.enter.prevent="handleEnter"
            :disabled="loading"
          />
          <el-button 
            type="primary" 
            class="send-btn" 
            :loading="loading" 
            @click="sendMessage"
            :disabled="!input.trim()"
          >
            <el-icon><Position /></el-icon>
          </el-button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { 
  Close, Service, UserFilled, 
  Position, Delete, Minus, FullScreen, ScaleToOriginal
} from '@element-plus/icons-vue'
import { http } from '@/utils/http'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

interface ChatResponse {
  answer: string
}

const visible = ref(false)
const isExpanded = ref(false)
const input = ref('')
const loading = ref(false)
const messages = ref<ChatMessage[]>([])
const chatBodyRef = ref<HTMLElement>()

const quickQuestions = [
  "销量前 10 的产品有哪些？",
  "最近一次导入的批次情况如何？",
  "分析一下当前的价格分布"
]

const toggleChat = () => {
  visible.value = !visible.value
  if (visible.value) {
    scrollToBottom()
  }
}

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
  scrollToBottom()
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatBodyRef.value) {
    chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
  }
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const handleEnter = (e: KeyboardEvent) => {
  if (!e.shiftKey) {
    sendMessage()
  }
}

const useQuickQuestion = (q: string) => {
  input.value = q
  sendMessage()
}

const clearHistory = () => {
  messages.value = []
}

const sendMessage = async () => {
  const content = input.value.trim()
  if (!content || loading.value) return

  messages.value.push({ role: 'user', content })
  input.value = ''
  loading.value = true
  scrollToBottom()

  try {
    const { data } = await http.post<ChatResponse>('/chat/query', {
      question: content
    })
    messages.value.push({ role: 'assistant', content: data.answer })
  } catch (error) {
    messages.value.push({ 
      role: 'assistant', 
      content: '抱歉，我遇到了一些问题，请稍后再试。' 
    })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

// 自动聚焦
watch(visible, (val) => {
  if (val) {
    scrollToBottom()
  }
})
</script>

<style scoped lang="scss">
.chat-bot-container {
  position: fixed;
  right: 30px;
  bottom: 30px;
  z-index: 2000;
  font-family: var(--font-family-base);
}

.chat-fab {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #fff;
  box-shadow: var(--shadow-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  color: #fff;
  font-size: 28px;
  position: relative;
  z-index: 2002;

  &:hover {
    transform: scale(1.1);
    box-shadow: 0 15px 30px -5px rgba(102, 126, 234, 0.6);
  }

  &.is-active {
    transform: rotate(90deg);
    background: var(--danger-color);
    box-shadow: var(--shadow-danger);
  }

  .fab-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 50%;
  }
}

.chat-window {
  position: absolute;
  bottom: 80px;
  right: 0;
  width: 380px;
  height: 600px;
  max-height: calc(100vh - 120px);
  background: #fff;
  border-radius: 16px;
  box-shadow: var(--shadow-2xl);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--border-light);
  transform-origin: bottom right;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &.is-expanded {
    width: 50vw;
    height: 80vh;
    max-height: 80vh;
    min-width: 600px;
  }}

.chat-header {
  padding: 16px;
  background: var(--primary-gradient);
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);

  .header-left {
    display: flex;
    align-items: center;
    gap: 12px;

    .avatar-wrapper {
      width: 40px;
      height: 40px;
      background: rgba(255, 255, 255, 0.2);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      backdrop-filter: blur(5px);
    }

    .header-info {
      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
      }

      .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        margin-right: 6px;
      }

      .status-text {
        font-size: 12px;
        opacity: 0.9;
      }
    }
  }

  .header-actions {
    display: flex;
    gap: 12px;

    .action-icon {
      cursor: pointer;
      opacity: 0.8;
      transition: opacity 0.2s;
      font-size: 18px;

      &:hover {
        opacity: 1;
      }
    }
  }
}

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f9fafb;
  display: flex;
  flex-direction: column;
  gap: 20px;

  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #e5e7eb;
    border-radius: 3px;
  }
}

.chat-welcome {
  text-align: center;
  margin-top: 40px;
  padding: 0 20px;

  .welcome-icon {
    font-size: 48px;
    margin-bottom: 16px;
    animation: wave 2s infinite;
  }

  h3 {
    margin: 0 0 8px;
    color: var(--text-primary);
  }

  p {
    margin: 0 0 24px;
    color: var(--text-secondary);
    font-size: 14px;
    line-height: 1.5;
  }
}

.quick-questions {
  display: flex;
  flex-direction: column;
  gap: 8px;

  .quick-tag {
    background: #fff;
    padding: 10px 16px;
    border-radius: 20px;
    font-size: 13px;
    color: var(--primary-color);
    border: 1px solid var(--primary-light);
    cursor: pointer;
    transition: all 0.2s;
    text-align: left;

    &:hover {
      background: var(--primary-light);
      color: #fff;
      transform: translateX(4px);
    }
  }
}

.message-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;

  &.user {
    flex-direction: row-reverse;

    .message-bubble {
      background: var(--primary-gradient);
      color: #fff;
      border-bottom-right-radius: 4px;
      box-shadow: var(--shadow-primary);
    }

    .message-time {
      text-align: right;
    }
  }

  &.assistant {
    .message-bubble {
      background: #fff;
      color: var(--text-primary);
      border-bottom-left-radius: 4px;
      box-shadow: var(--shadow-sm);
    }
  }
}

.assistant-avatar {
  background: var(--primary-light);
}

.user-avatar {
  background: var(--success-light);
}

.message-content {
  max-width: 75%;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.message-time {
  font-size: 10px;
  color: var(--text-tertiary);
  margin: 0 4px;
}

.typing {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 16px 20px;

  span {
    width: 6px;
    height: 6px;
    background: var(--text-tertiary);
    border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out both;

    &:nth-child(1) { animation-delay: -0.32s; }
    &:nth-child(2) { animation-delay: -0.16s; }
  }
}

.chat-footer {
  padding: 16px;
  background: #fff;
  border-top: 1px solid var(--border-light);
  display: flex;
  gap: 12px;
  align-items: flex-end;

  :deep(.el-textarea__inner) {
    border-radius: 20px;
    padding: 10px 16px;
    background: #f9fafb;
    border-color: transparent;
    transition: all 0.2s;

    &:focus {
      background: #fff;
      border-color: var(--primary-light);
      box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
    }
  }

  .send-btn {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--primary-gradient);
    border: none;
    transition: all 0.2s;

    &:hover {
      transform: scale(1.05);
      box-shadow: var(--shadow-md);
    }

    &:disabled {
      background: var(--text-tertiary);
      transform: none;
    }
  }
}

// 动画
.chat-slide-enter-active,
.chat-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.chat-slide-enter-from,
.chat-slide-leave-to {
  opacity: 0;
  transform: scale(0.9) translateY(20px);
}

@keyframes wave {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(20deg); }
  75% { transform: rotate(-15deg); }
}

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
</style>
