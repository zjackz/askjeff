/**
 * 一个极简的 Markdown 渲染工具，用于在无法安装外部库的环境下提供基础渲染。
 * 支持：标题、加粗、列表、换行。
 */
export function renderMarkdown(text: string): string {
    if (!text) return ''

    let html = text
        // 处理标题 (h1-h3)
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')

        // 处理加粗
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')

        // 处理无序列表
        .replace(/^\- (.*$)/gim, '<li>$1</li>')
        .replace(/^\* (.*$)/gim, '<li>$1</li>')

        // 处理有序列表
        .replace(/^\d+\. (.*$)/gim, '<li>$1</li>')

        // 处理换行 (将非标签结尾的换行转为 <br>)
        .replace(/\n/g, '<br />')

    // 简单的列表包装逻辑：将连续的 <li> 包装在 <ul> 中
    html = html.replace(/((?:<li>.*?<\/li>)+)/gs, '<ul>$1</ul>')

    return html
}
