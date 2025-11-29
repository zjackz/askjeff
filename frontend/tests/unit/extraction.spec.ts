/**
 * @vitest-environment jsdom
 */
import { mount, flushPromises } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ExtractionIndex from '@/views/extraction/index.vue'
import { extractionApi } from '@/api/extraction'

// Mock the API module
vi.mock('@/api/extraction', () => ({
    extractionApi: {
        upload: vi.fn(),
        start: vi.fn(),
        getTask: vi.fn(),
        getExportUrl: vi.fn()
    }
}))

vi.mock('@element-plus/icons-vue', () => ({
    UploadFilled: { template: '<div></div>' }
}))

let intervalCallback: (() => void) | null = null

vi.mock('@vueuse/core', async () => {
    const actual = await vi.importActual<any>('@vueuse/core')
    return {
        ...actual,
        useIntervalFn: (cb: () => void) => {
            intervalCallback = cb
            return {
                pause: vi.fn(),
                resume: vi.fn(),
                isActive: { value: false }
            }
        }
    }
})

import { ref } from 'vue'

// Mock Element Plus components to avoid rendering issues and focus on logic
// We can use stubs for complex components
const globalStubs = {
    'el-upload': {
        template: '<div><slot></slot></div>',
        props: ['onChange', 'autoUpload']
    },
    'el-card': { template: '<div><slot name="header"></slot><slot></slot></div>' },
    'el-descriptions': { template: '<div><slot></slot></div>' },
    'el-descriptions-item': { template: '<div><slot></slot></div>' },
    'el-tag': { template: '<div><slot></slot></div>', props: ['closable'], emits: ['close'] },
    'el-input': {
        template: '<input @keyup.enter="$emit(\'keyup.enter\')" @blur="$emit(\'blur\')" :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
        props: ['modelValue'],
        emits: ['update:modelValue', 'keyup.enter', 'blur'],
        setup(props, { expose }) {
            const inputMock = { focus: vi.fn() }
            expose({ input: inputMock })
            return { input: inputMock }
        }
    },
    'el-button': {
        template: '<button @click="$emit(\'click\')" :disabled="disabled"><slot></slot></button>',
        props: ['disabled', 'loading']
    },
    'el-alert': { template: '<div></div>' },
    'el-icon': { template: '<div></div>' },
    'upload-filled': { template: '<div></div>' }
}

describe('ExtractionIndex.vue', () => {
    beforeEach(() => {
        vi.clearAllMocks()
    })

    it('renders upload section initially', () => {
        const wrapper = mount(ExtractionIndex, {
            global: {
                stubs: globalStubs
            }
        })
        expect(wrapper.text()).toContain('LLM 产品特征提取')
        expect(wrapper.find('.upload-section').exists()).toBe(true)
        expect(wrapper.find('.task-section').exists()).toBe(false)
    })

    it('handles file upload success', async () => {
        const mockTask = {
            id: '123',
            filename: 'test.csv',
            status: 'PENDING',
            columns: ['col1', 'col2'],
            target_fields: [],
            created_at: '',
            updated_at: ''
        }

        // Mock upload response
        vi.mocked(extractionApi.upload).mockResolvedValue({ data: mockTask } as any)

        const wrapper = mount(ExtractionIndex, {
            global: {
                stubs: globalStubs
            }
        })

        // Simulate file selection (triggering handleFileChange manually since we stubbed el-upload)
        // We need to access the component instance to call the method or trigger the event on the stub if we implemented it right.
        // Since we stubbed el-upload with a simple div, we can't easily trigger the 'on-change' prop callback from the DOM.
        // However, we can use `wrapper.vm` to access internal state if needed, or better, make the stub emit the event.
        // But `el-upload` uses a prop `on-change`, not an emitted event `change`.

        // Let's try to find the upload component and trigger the prop function.
        // Since we passed `onChange` as a prop in the stub, we might be able to access it.
        // But `mount` with stubs replaces the component.

        // A better way for `el-upload` might be to just call the method directly if we want to test the logic,
        // or use a more functional stub.

        // Let's try to set the fileList directly to simulate "file selected" state, 
        // then click the upload button.

        // Actually, the button is disabled if fileList is empty.
        // The `handleFileChange` updates `fileList`.

        // Let's access the component instance to set data for testing simplicity
        const vm = wrapper.vm as any
        vm.fileList = [{ name: 'test.csv', raw: new File([''], 'test.csv') }]

        await wrapper.vm.$nextTick()

        // Find upload button
        const buttons = wrapper.findAll('button')
        const uploadBtn = buttons.find(b => b.text().includes('下一步'))
        expect(uploadBtn?.exists()).toBe(true)
        expect((uploadBtn?.element as HTMLButtonElement).disabled).toBe(false)
        // Actually with our stub: :disabled="disabled". If false, it might be absent or "false".

        await uploadBtn?.trigger('click')

        expect(extractionApi.upload).toHaveBeenCalled()
        await flushPromises()

        // Should now show task section
        expect(wrapper.find('.task-section').exists()).toBe(true)
        expect(wrapper.text()).toContain('test.csv')
        expect(wrapper.text()).toContain('PENDING')
    })

    it('adds and removes fields', async () => {
        const mockTask = {
            id: '123',
            filename: 'test.csv',
            status: 'PENDING',
            columns: ['col1'],
            target_fields: [],
            created_at: '',
            updated_at: ''
        }

        const wrapper = mount(ExtractionIndex, {
            global: { stubs: globalStubs }
        })

        // Set state to having a task
        const vm = wrapper.vm as any
        vm.currentTask = mockTask
        await wrapper.vm.$nextTick()

        // Check initial state
        expect(wrapper.find('.tags-input').exists()).toBe(true)

        // Click "+ 添加字段"
        const addBtn = wrapper.findAll('button').find(b => b.text().includes('+ 添加字段'))
        await addBtn?.trigger('click')

        // Input should appear
        const input = wrapper.find('input')
        expect(input.exists()).toBe(true)

        // Type value and enter
        await input.setValue('Battery')
        await input.trigger('keyup.enter')

        // Tag should appear
        expect(wrapper.text()).toContain('Battery')
        expect(vm.dynamicTags).toContain('Battery')

        // Remove tag (simulate close event on stub)
        const tag = wrapper.findComponent('.mx-1')
        tag.vm.$emit('close', 'Battery')

        expect(vm.dynamicTags).not.toContain('Battery')
    })

    it('starts extraction and polls status', async () => {
        const mockTask = {
            id: '123',
            filename: 'test.csv',
            status: 'PENDING',
            columns: ['col1'],
            target_fields: [],
            created_at: '',
            updated_at: ''
        }

        const wrapper = mount(ExtractionIndex, {
            global: { stubs: globalStubs }
        })

        const vm = wrapper.vm as any
        vm.currentTask = mockTask
        vm.dynamicTags = ['Battery']
        await wrapper.vm.$nextTick()

        // Mock start API
        vi.mocked(extractionApi.start).mockResolvedValue({} as any)

        // Click start
        const startBtn = wrapper.findAll('button').find(b => b.text().includes('开始提取'))
        await startBtn?.trigger('click')

        expect(extractionApi.start).toHaveBeenCalledWith('123', ['Battery'])
        await flushPromises()

        expect(vm.currentTask.status).toBe('PROCESSING')

        // Test polling

        // Mock getTask response for polling
        vi.mocked(extractionApi.getTask).mockResolvedValue({
            data: { ...mockTask, status: 'COMPLETED' }
        } as any)

        // Trigger polling manually
        if (intervalCallback) intervalCallback()

        // Wait for promises
        await flushPromises()

        expect(extractionApi.getTask).toHaveBeenCalledWith('123')
        expect(vm.currentTask.status).toBe('COMPLETED')

        vi.useRealTimers()
    })
})
