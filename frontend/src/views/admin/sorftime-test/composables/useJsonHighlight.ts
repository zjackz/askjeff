import { reactive, computed } from 'vue'

/**
 * JSON 高亮显示 Composable
 * 提供 JSON 语法高亮和过滤功能
 */
export function useJsonHighlight(response: any) {
    const jsonViewOptions = reactive({
        compact: false,
        wrap: true,
        selectedKeys: [] as string[]
    })

    // 可用的字段列表
    const availableKeys = computed(() => {
        if (!response.value) return []
        const target = response.value.data || response.value
        if (typeof target === 'object' && target !== null && !Array.isArray(target)) {
            return Object.keys(target)
        }
        return Object.keys(response.value)
    })

    // 过滤后的响应数据
    const filteredResponse = computed(() => {
        if (!response.value) return null

        if (jsonViewOptions.selectedKeys.length === 0) {
            return response.value
        }

        const target = response.value.data || response.value

        if (typeof target === 'object' && target !== null && !Array.isArray(target)) {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const filtered: any = {}
            jsonViewOptions.selectedKeys.forEach(key => {
                if (key in target) {
                    filtered[key] = target[key]
                }
            })
            return filtered
        }

        return response.value
    })

    /**
     * JSON 语法高亮
     */
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const highlightJson = (json: any) => {
        if (typeof json !== 'string') {
            json = JSON.stringify(json, null, 2)
        }
        json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        // eslint-disable-next-line no-useless-escape
        return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, (match: string) => {
            let cls = 'number'
            if (/^"/.test(match)) {
                if (/:$/.test(match)) {
                    cls = 'key'
                } else {
                    cls = 'string'
                }
            } else if (/true|false/.test(match)) {
                cls = 'boolean'
            } else if (/null/.test(match)) {
                cls = 'null'
            }
            return `<span class="${cls}">${match}</span>`
        })
    }

    return {
        jsonViewOptions,
        availableKeys,
        filteredResponse,
        highlightJson
    }
}
