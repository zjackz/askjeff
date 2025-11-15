import { describe, it, expect } from 'vitest'
import ChatView from '@/views/chat/index.vue'

describe('ChatView', () => {
  it('组件可加载', () => {
    expect(ChatView).toBeTruthy()
  })
})
