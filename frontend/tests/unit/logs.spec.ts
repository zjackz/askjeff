import { describe, it, expect } from 'vitest'
import LogsView from '@/views/logs/index.vue'

describe('LogsView', () => {
  it('组件可加载', () => {
    expect(LogsView).toBeTruthy()
  })
})
