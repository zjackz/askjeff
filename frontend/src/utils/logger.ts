/**
 * 统一日志工具
 * 
 * 替代 console.log/error/warn,支持环境区分
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error'

class Logger {
    private isDev = import.meta.env.DEV

    /**
     * 调试日志 (仅开发环境)
     */
    debug(message: string, ...args: any[]) {
        if (this.isDev) {
            console.log(`[DEBUG] ${message}`, ...args)
        }
    }

    /**
     * 信息日志 (仅开发环境)
     */
    info(message: string, ...args: any[]) {
        if (this.isDev) {
            console.log(`[INFO] ${message}`, ...args)
        }
    }

    /**
     * 警告日志
     */
    warn(message: string, ...args: any[]) {
        if (this.isDev) {
            console.warn(`[WARN] ${message}`, ...args)
        }
    }

    /**
     * 错误日志
     */
    error(message: string, error?: Error | unknown, ...args: any[]) {
        if (this.isDev) {
            console.error(`[ERROR] ${message}`, error, ...args)
        }

        // 生产环境可以发送到错误监控服务
        // if (!this.isDev) {
        //   sendToErrorTracking(message, error)
        // }
    }

    /**
     * 记录 API 调用
     */
    api(method: string, url: string, data?: any) {
        if (this.isDev) {
            console.log(`[API] ${method} ${url}`, data)
        }
    }
}

// 导出单例
export const logger = new Logger()

// 默认导出
export default logger
