# AI UI/UX 统一规范（模板）

> 建议放置位置：项目根目录 `AGENTS/`（便于跨项目复制）。

## MUST（先统一再美化）

- 先用项目现成 UI 组件与封装组件，禁止手搓一套风格
- 先定 Token 再写样式（颜色/字号/间距/圆角/阴影来自 CSS 变量/主题），禁止魔法数字散落
- 同类页面同一骨架（列表/表单/详情/弹窗），间距与布局一致
- 默认克制：无明确需求不引入新字体/新动效/新图标风格

## MUST（Token）

- 项目必须有 Token（哪怕很小），AI 新增样式只能用 Token
- 验收：新增页面/组件不得出现大量不可复用内联样式（如 `padding:13px`、`margin:7px`）

## MUST（页面骨架）

- 列表页：顶栏（标题+主操作）→ 可折叠筛选（3–5 项）→ 内容区占满高度（避免双滚动）→ 统一分页
- 表单页：分组（基础/高级/风险）→ 底部固定按钮（保存/取消）→ 字段级校验 + 首错聚焦
- 详情页：头部摘要（名称/状态/时间/关键指标）→ Tabs/分区一致

## MUST（组件与尺寸）

- 全局统一默认尺寸；禁止随意 `small/mini`（仅允许密集表格行内操作）
- 每个视图最多 1 个主按钮（Primary）；危险操作必须二次确认并用 Danger
- 表格：数字右对齐、文本左对齐、状态居中；操作列固定右侧；空/错/加载态统一
- 分页页大小必须全仓统一（默认建议 `[20,50,100,200]`，默认 50；项目可改但必须一致）

## MUST（交互反馈）

- 所有异步请求必须有 loading（按钮/局部/全局择一）
- 错误提示必须中文且可执行（重试/检查输入/联系管理员），禁止直接抛英文/堆栈
- 成功提示克制；优先用页面状态更新替代频繁弹 toast

## MUST（文案与可用性）

- 按钮用统一动词（新增/保存/导入/导出/重试），同义词不混用
- 字段名全仓一致（如“开始时间/结束时间”）
- 基本可访问：可聚焦、弹窗焦点管理、颜色不作为唯一信息来源

## 推荐门禁

- `check-ui-consistency`：阻止硬编码尺寸/分页不一致/过多内联样式等回退

## 🎨 Design System (Premium Intelligence)

### 1. Color Palette (Dark Mode Default)

**Backgrounds**:
- Main: `#0F172A` (Deep Slate Blue) - `var(--color-studio-bg)`
- Surface: `#1E293B` (Lighter Slate) - `var(--color-studio-surface)`
- Surface Hover: `#334155` - `var(--color-studio-surface-hover)`

**Accents**:
- Primary: `#D48B78` (Rose Gold) - `var(--color-accent-primary)`
- Secondary: `#B89628` (Gold) - `var(--color-accent-secondary)`
- Glow: `rgba(212, 139, 120, 0.5)` - `var(--color-accent-glow)`

**Text**:
- Main: `#F8FAFC` (Off-white) - `var(--color-text-main)`
- Muted: `#94A3B8` (Slate grey) - `var(--color-text-muted)`

**Borders**:
- Default: `#334155` - `var(--color-border)`
- Highlight: `#475569` - `var(--color-border-highlight)`

### 2. Typography

- **UI Font**: `'DM Sans', sans-serif` - `var(--font-ui)`
- **Heading Font**: `'Playfair Display', serif` - `var(--font-heading)`
- **Monospace**: `'JetBrains Mono', monospace` - `var(--font-mono)`

### 3. Effects & Components

**Glassmorphism**:
- Background: `rgba(30, 41, 59, 0.7)` - `var(--glass-bg)`
- Border: `1px solid rgba(255, 255, 255, 0.1)` - `var(--glass-border)`

**Shadows**:
- Card: `0 4px 6px -1px rgba(0, 0, 0, 0.3)` - `var(--shadow-card)`
- Glow: `0 0 15px var(--color-accent-glow)` - `var(--shadow-glow)`

**Component Styles**:
- **Inputs**: Minimal style, transparent background, bottom border or subtle outline.
- **Buttons**: Icon-based actions, hover effects with scaling, rounded corners (`9999px`).
- **Tables**: Glass panel container, minimal input cells, sticky headers.

### 4. Spacing System

- `xs`: 4px (`var(--space-xs)`)
- `sm`: 8px (`var(--space-sm)`)
- `md`: 16px (`var(--space-md)`)
- `lg`: 24px (`var(--space-lg)`)
- `xl`: 32px (`var(--space-xl)`)
- `2xl`: 48px (`var(--space-2xl)`)

## 🚫 常见错误 (Must Avoid)

- ❌ **硬编码颜色**: 严禁使用 hex 值，必须使用 `var(--color-...)`。
- ❌ **随意尺寸**: 严禁使用 `padding: 13px` 这种魔法数字。
- ❌ **默认滚动条**: 必须使用自定义的极简滚动条样式。
