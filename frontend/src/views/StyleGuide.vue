<!--
组件样式指南页面
访问路径: /style-guide
-->
<template>
  <div class="style-guide">
    <div class="style-guide-header">
      <h1>ASKJeff 组件样式指南</h1>
      <p class="subtitle">组件库文档和使用示例</p>
    </div>

    <el-tabs v-model="activeTab" class="style-guide-tabs">
      <!-- 按钮组件 -->
      <el-tab-pane label="按钮 Button" name="button">
        <div class="component-section">
          <h2>基础按钮</h2>
          <div class="demo-block">
            <BaseButton>默认按钮</BaseButton>
            <BaseButton type="primary">主要按钮</BaseButton>
            <BaseButton type="success">成功按钮</BaseButton>
            <BaseButton type="warning">警告按钮</BaseButton>
            <BaseButton type="danger">危险按钮</BaseButton>
            <BaseButton type="info">信息按钮</BaseButton>
          </div>

          <h2>朴素按钮</h2>
          <div class="demo-block">
            <BaseButton plain>朴素按钮</BaseButton>
            <BaseButton type="primary" plain>主要按钮</BaseButton>
            <BaseButton type="success" plain>成功按钮</BaseButton>
            <BaseButton type="warning" plain>警告按钮</BaseButton>
            <BaseButton type="danger" plain>危险按钮</BaseButton>
          </div>

          <h2>圆角按钮</h2>
          <div class="demo-block">
            <BaseButton round>圆角按钮</BaseButton>
            <BaseButton type="primary" round>主要按钮</BaseButton>
            <BaseButton type="success" round>成功按钮</BaseButton>
          </div>

          <h2>按钮状态</h2>
          <div class="demo-block">
            <BaseButton :loading="true">加载中</BaseButton>
            <BaseButton :disabled="true">禁用按钮</BaseButton>
            <BaseButton type="primary" :loading="true">提交中</BaseButton>
          </div>

          <h2>按钮尺寸</h2>
          <div class="demo-block">
            <BaseButton size="large">大型按钮</BaseButton>
            <BaseButton>默认按钮</BaseButton>
            <BaseButton size="small">小型按钮</BaseButton>
          </div>

          <div class="code-block">
            <h3>代码示例</h3>
            <pre><code>&lt;BaseButton type="primary"&gt;主要按钮&lt;/BaseButton&gt;
&lt;BaseButton type="success" :loading="true"&gt;加载中&lt;/BaseButton&gt;
&lt;BaseButton type="danger" :disabled="true"&gt;禁用&lt;/BaseButton&gt;</code></pre>
          </div>
        </div>
      </el-tab-pane>

      <!-- 表格组件 -->
      <el-tab-pane label="表格 Table" name="table">
        <div class="component-section">
          <h2>基础表格</h2>
          <div class="demo-block">
            <BaseTable
              :data="tableData"
              :columns="tableColumns"
              :show-pagination="false"
            />
          </div>

          <h2>带分页的表格</h2>
          <div class="demo-block">
            <BaseTable
              :data="tableData"
              :columns="tableColumns"
              :total="100"
              :page="1"
              :page-size="10"
            />
          </div>

          <h2>带操作列的表格</h2>
          <div class="demo-block">
            <BaseTable
              :data="tableData"
              :columns="tableColumns"
              :show-actions="true"
              :show-pagination="false"
            >
              <template #actions="{ row }">
                <el-button size="small" type="primary">编辑</el-button>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </BaseTable>
          </div>

          <div class="code-block">
            <h3>代码示例</h3>
            <pre><code>&lt;BaseTable
  :data="tableData"
  :columns="columns"
  :total="total"
  @page-change="handlePageChange"
&gt;
  &lt;template #actions="{ row }"&gt;
    &lt;el-button @click="handleEdit(row)"&gt;编辑&lt;/el-button&gt;
  &lt;/template&gt;
&lt;/BaseTable&gt;</code></pre>
          </div>
        </div>
      </el-tab-pane>

      <!-- 对话框组件 -->
      <el-tab-pane label="对话框 Dialog" name="dialog">
        <div class="component-section">
          <h2>基础对话框</h2>
          <div class="demo-block">
            <BaseButton type="primary" @click="dialogVisible1 = true">
              打开对话框
            </BaseButton>
            <BaseDialog
              v-model="dialogVisible1"
              title="基础对话框"
              @confirm="handleConfirm"
            >
              <p>这是对话框内容</p>
              <p>可以放置任何内容</p>
            </BaseDialog>
          </div>

          <h2>自定义底部</h2>
          <div class="demo-block">
            <BaseButton type="success" @click="dialogVisible2 = true">
              自定义底部
            </BaseButton>
            <BaseDialog
              v-model="dialogVisible2"
              title="自定义底部"
            >
              <p>自定义底部按钮</p>
              <template #footer>
                <el-button @click="dialogVisible2 = false">取消</el-button>
                <el-button type="warning">保存草稿</el-button>
                <el-button type="primary">提交</el-button>
              </template>
            </BaseDialog>
          </div>

          <h2>无底部按钮</h2>
          <div class="demo-block">
            <BaseButton type="info" @click="dialogVisible3 = true">
              无底部按钮
            </BaseButton>
            <BaseDialog
              v-model="dialogVisible3"
              title="提示"
              :show-footer="false"
            >
              <p>这是一个提示信息</p>
            </BaseDialog>
          </div>

          <div class="code-block">
            <h3>代码示例</h3>
            <pre><code>&lt;BaseDialog
  v-model="visible"
  title="编辑"
  @confirm="handleConfirm"
&gt;
  &lt;p&gt;对话框内容&lt;/p&gt;
&lt;/BaseDialog&gt;</code></pre>
          </div>
        </div>
      </el-tab-pane>

      <!-- 表单组件 -->
      <el-tab-pane label="表单 Form" name="form">
        <div class="component-section">
          <h2>基础表单</h2>
          <div class="demo-block">
            <BaseForm
              :model="formData"
              :rules="formRules"
              :items="formItems"
              @submit="handleSubmit"
              @reset="handleReset"
            />
          </div>

          <h2>内联表单</h2>
          <div class="demo-block">
            <BaseForm
              :model="searchForm"
              :items="searchItems"
              :inline="true"
              :show-buttons="false"
            >
              <template #actions>
                <el-button type="primary">搜索</el-button>
                <el-button>重置</el-button>
              </template>
            </BaseForm>
          </div>

          <div class="code-block">
            <h3>代码示例</h3>
            <pre><code>&lt;BaseForm
  :model="formData"
  :rules="rules"
  :items="formItems"
  @submit="handleSubmit"
/&gt;

// formItems 配置
const formItems = [
  { prop: 'name', label: '名称', type: 'input', required: true },
  { prop: 'email', label: '邮箱', type: 'input' },
  { prop: 'status', label: '状态', type: 'select', options: [...] }
]</code></pre>
          </div>
        </div>
      </el-tab-pane>

      <!-- 颜色系统 -->
      <el-tab-pane label="颜色 Colors" name="colors">
        <div class="component-section">
          <h2>主题色</h2>
          <div class="color-grid">
            <div class="color-item">
              <div class="color-box" style="background-color: #409EFF"></div>
              <div class="color-info">
                <div class="color-name">Primary</div>
                <div class="color-value">#409EFF</div>
              </div>
            </div>
            <div class="color-item">
              <div class="color-box" style="background-color: #67C23A"></div>
              <div class="color-info">
                <div class="color-name">Success</div>
                <div class="color-value">#67C23A</div>
              </div>
            </div>
            <div class="color-item">
              <div class="color-box" style="background-color: #E6A23C"></div>
              <div class="color-info">
                <div class="color-name">Warning</div>
                <div class="color-value">#E6A23C</div>
              </div>
            </div>
            <div class="color-item">
              <div class="color-box" style="background-color: #F56C6C"></div>
              <div class="color-info">
                <div class="color-name">Danger</div>
                <div class="color-value">#F56C6C</div>
              </div>
            </div>
            <div class="color-item">
              <div class="color-box" style="background-color: #909399"></div>
              <div class="color-info">
                <div class="color-name">Info</div>
                <div class="color-value">#909399</div>
              </div>
            </div>
          </div>

          <h2>中性色</h2>
          <div class="color-grid">
            <div class="color-item">
              <div class="color-box" style="background-color: #303133"></div>
              <div class="color-info">
                <div class="color-name">Text Primary</div>
                <div class="color-value">#303133</div>
              </div>
            </div>
            <div class="color-item">
              <div class="color-box" style="background-color: #606266"></div>
              <div class="color-info">
                <div class="color-name">Text Regular</div>
                <div class="color-value">#606266</div>
              </div>
            </div>
            <div class="color-item">
              <div class="color-box" style="background-color: #909399"></div>
              <div class="color-info">
                <div class="color-name">Text Secondary</div>
                <div class="color-value">#909399</div>
              </div>
            </div>
            <div class="color-item">
              <div class="color-box" style="background-color: #C0C4CC"></div>
              <div class="color-info">
                <div class="color-name">Text Placeholder</div>
                <div class="color-value">#C0C4CC</div>
              </div>
            </div>
          </div>

          <h2>边框色</h2>
          <div class="color-grid">
            <div class="color-item">
              <div class="color-box" style="background-color: #DCDFE6; border: 1px solid #ccc"></div>
              <div class="color-info">
                <div class="color-name">Border Base</div>
                <div class="color-value">#DCDFE6</div>
              </div>
            </div>
            <div class="color-item">
              <div class="color-box" style="background-color: #E4E7ED; border: 1px solid #ccc"></div>
              <div class="color-info">
                <div class="color-name">Border Light</div>
                <div class="color-value">#E4E7ED</div>
              </div>
            </div>
            <div class="color-item">
              <div class="color-box" style="background-color: #EBEEF5; border: 1px solid #ccc"></div>
              <div class="color-info">
                <div class="color-name">Border Lighter</div>
                <div class="color-value">#EBEEF5</div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 排版 -->
      <el-tab-pane label="排版 Typography" name="typography">
        <div class="component-section">
          <h2>标题</h2>
          <div class="demo-block">
            <h1>H1 标题 - 32px</h1>
            <h2>H2 标题 - 28px</h2>
            <h3>H3 标题 - 24px</h3>
            <h4>H4 标题 - 20px</h4>
            <h5>H5 标题 - 16px</h5>
            <h6>H6 标题 - 14px</h6>
          </div>

          <h2>正文</h2>
          <div class="demo-block">
            <p class="text-large">大号文本 - 16px</p>
            <p class="text-regular">常规文本 - 14px</p>
            <p class="text-small">小号文本 - 13px</p>
            <p class="text-mini">超小文本 - 12px</p>
          </div>

          <h2>文本颜色</h2>
          <div class="demo-block">
            <p style="color: #303133">主要文本 - #303133</p>
            <p style="color: #606266">常规文本 - #606266</p>
            <p style="color: #909399">次要文本 - #909399</p>
            <p style="color: #C0C4CC">占位文本 - #C0C4CC</p>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseTable from '@/components/common/BaseTable.vue'
import BaseDialog from '@/components/common/BaseDialog.vue'
import BaseForm from '@/components/common/BaseForm.vue'

const activeTab = ref('button')

// 对话框状态
const dialogVisible1 = ref(false)
const dialogVisible2 = ref(false)
const dialogVisible3 = ref(false)

// 表格数据
const tableData = ref([
  { id: 1, name: '张三', email: 'zhangsan@example.com', status: 'active' },
  { id: 2, name: '李四', email: 'lisi@example.com', status: 'inactive' },
  { id: 3, name: '王五', email: 'wangwu@example.com', status: 'active' }
])

const tableColumns = [
  { prop: 'id', label: 'ID', width: 80 },
  { prop: 'name', label: '姓名', minWidth: 120 },
  { prop: 'email', label: '邮箱', minWidth: 180 },
  { prop: 'status', label: '状态', width: 100 }
]

// 表单数据
const formData = reactive({
  name: '',
  email: '',
  gender: '',
  birthday: '',
  age: 0,
  active: true
})

const formRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱', trigger: 'blur' }
  ]
}

const formItems = [
  { prop: 'name', label: '姓名', type: 'input', placeholder: '请输入姓名', required: true },
  { prop: 'email', label: '邮箱', type: 'input', placeholder: '请输入邮箱', required: true },
  { prop: 'gender', label: '性别', type: 'select', options: [
    { label: '男', value: 'male' },
    { label: '女', value: 'female' }
  ]},
  { prop: 'birthday', label: '生日', type: 'date' },
  { prop: 'age', label: '年龄', type: 'number', min: 0, max: 150 },
  { prop: 'active', label: '激活', type: 'switch' }
]

const searchForm = reactive({
  keyword: '',
  status: ''
})

const searchItems = [
  { prop: 'keyword', label: '关键词', type: 'input', placeholder: '请输入关键词' },
  { prop: 'status', label: '状态', type: 'select', options: [
    { label: '全部', value: '' },
    { label: '激活', value: 'active' },
    { label: '禁用', value: 'inactive' }
  ]}
]

const handleConfirm = () => {
  console.log('确认')
  dialogVisible1.value = false
}

const handleSubmit = (values: any) => {
  console.log('提交表单:', values)
}

const handleReset = () => {
  console.log('重置表单')
}
</script>

<style scoped>
.style-guide {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.style-guide-header {
  text-align: center;
  margin-bottom: 48px;
  padding: 32px 0;
  border-bottom: 2px solid #EBEEF5;
}

.style-guide-header h1 {
  font-size: 36px;
  color: #303133;
  margin: 0 0 16px 0;
}

.subtitle {
  font-size: 16px;
  color: #909399;
  margin: 0;
}

.style-guide-tabs {
  margin-top: 24px;
}

.component-section {
  padding: 24px 0;
}

.component-section h2 {
  font-size: 24px;
  color: #303133;
  margin: 32px 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #EBEEF5;
}

.component-section h3 {
  font-size: 18px;
  color: #606266;
  margin: 16px 0 8px 0;
}

.demo-block {
  padding: 24px;
  border: 1px solid #EBEEF5;
  border-radius: 4px;
  margin-bottom: 24px;
  background-color: #FAFAFA;
}

.demo-block > * {
  margin-right: 12px;
  margin-bottom: 12px;
}

.code-block {
  margin-top: 24px;
  padding: 16px;
  background-color: #F5F7FA;
  border-radius: 4px;
}

.code-block pre {
  margin: 0;
  padding: 16px;
  background-color: #282c34;
  color: #abb2bf;
  border-radius: 4px;
  overflow-x: auto;
}

.code-block code {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.6;
}

/* 颜色系统 */
.color-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.color-item {
  border: 1px solid #EBEEF5;
  border-radius: 4px;
  overflow: hidden;
}

.color-box {
  height: 80px;
  width: 100%;
}

.color-info {
  padding: 12px;
  background-color: #fff;
}

.color-name {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
  margin-bottom: 4px;
}

.color-value {
  font-size: 12px;
  color: #909399;
  font-family: monospace;
}

/* 排版 */
.text-large {
  font-size: 16px;
}

.text-regular {
  font-size: 14px;
}

.text-small {
  font-size: 13px;
}

.text-mini {
  font-size: 12px;
}
</style>
