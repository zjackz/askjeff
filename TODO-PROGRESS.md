# API 导入进度功能 - 待改进

## 当前状态

**临时方案**: 提交任务后5秒自动关闭弹窗,用户在导入列表中查看结果

## 问题描述

### 核心问题
API 导入的实时进度轮询功能不稳定:
1. 后台线程执行正常,数据导入成功
2. 但进度信息未能可靠地更新到数据库
3. 前端轮询时读取不到最新进度

### 已尝试的方案

#### 方案 1: JSON 嵌套进度对象
- **实现**: 在 `import_metadata.progress` 中存储完整进度信息
- **问题**: JSON 更新在后台线程中不可靠,数据库会话同步问题

#### 方案 2: 简化字段更新
- **实现**: 直接更新 `total_rows`, `success_rows`,在 metadata 中只存储简单字符串
- **问题**: 仍然存在更新失败的情况,可能是后台线程的数据库会话问题

### 根本原因分析

**后台线程数据库会话隔离**:
- 主请求和后台线程使用不同的数据库会话
- 后台线程的 commit 可能不会立即对其他会话可见
- PostgreSQL 的事务隔离级别可能影响实时性

## 临时方案

### 实施内容

```vue
// frontend/src/views/import/components/SorftimeImportDialog.vue

// 提交任务后:
// 1. 显示"任务已提交成功"
// 2. 5秒后自动关闭弹窗
// 3. 用户在导入列表中查看实际进度和结果
```

### 用户体验
- ✅ 任务提交成功有明确反馈
- ✅ 不会因为进度卡住而困惑
- ✅ 可以在列表中看到所有导入批次
- ⚠️ 无法实时看到进度百分比

## 待改进方案

### 方案 A: 使用 Redis 存储进度 (推荐)
**优势**:
- Redis 的发布/订阅机制天然适合实时进度
- 不受数据库事务隔离影响
- 性能更好

**实施**:
1. 后台线程更新进度到 Redis
2. 前端通过 WebSocket 或轮询 Redis
3. 完成后同步到数据库

**工作量**: 中等 (需要集成 Redis)

### 方案 B: 使用数据库通知机制
**优势**:
- PostgreSQL LISTEN/NOTIFY
- 不需要额外组件

**实施**:
1. 后台线程通过 NOTIFY 发送进度
2. 前端通过 SSE 接收通知

**工作量**: 中等

### 方案 C: 简化为批次完成通知
**优势**:
- 最简单可靠
- 不需要实时进度

**实施**:
1. 只在开始和完成时更新状态
2. 前端轮询批次状态 (pending/running/succeeded/failed)
3. 不显示百分比,只显示状态

**工作量**: 小

### 方案 D: 前端定时刷新列表
**优势**:
- 无需修改后端
- 用户可以看到所有批次的最新状态

**实施**:
1. 导入列表页面每5秒自动刷新
2. 高亮最新创建的批次
3. 显示状态变化动画

**工作量**: 小

## 推荐方案

**短期** (1-2天): 方案 D - 前端定时刷新列表
- 最小改动
- 用户体验可接受

**长期** (1-2周): 方案 A - Redis + WebSocket
- 最佳用户体验
- 可扩展到其他实时功能

## 相关文件

- `frontend/src/views/import/components/SorftimeImportDialog.vue` - 导入对话框
- `backend/app/services/progress_tracker.py` - 进度跟踪器
- `backend/app/services/api_import_service.py` - API 导入服务
- `backend/app/api/routes/imports.py` - 导入路由

## 参考资料

- PostgreSQL 事务隔离: <https://www.postgresql.org/docs/current/transaction-iso.html>
- Redis Pub/Sub: <https://redis.io/docs/manual/pubsub/>
- FastAPI WebSocket: <https://fastapi.tiangolo.com/advanced/websockets/>

---

**创建时间**: 2025-12-18  
**优先级**: 中  
**预计工作量**: 短期方案 2小时,长期方案 1-2天
