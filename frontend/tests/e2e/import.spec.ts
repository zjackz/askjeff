import { test, expect } from '@playwright/test'

const BASE_URL = process.env.BASE_URL || 'http://localhost:5174'

test('运营可上传 Sorftime 文件', async ({ page }) => {
  await page.route('**/imports', async (route) => {
    await route.fulfill({ status: 201, contentType: 'application/json', body: JSON.stringify({ ok: true }) })
  })

  await page.goto(`${BASE_URL}/import`)
  await expect(page.getByRole('heading', { name: '文件导入' })).toBeVisible()

  const fileInput = page.locator('input[type="file"]')
  await fileInput.setInputFiles({
    name: 'demo.xlsx',
    mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    buffer: Buffer.from('demo')
  })

  await page.getByRole('button', { name: '开始导入' }).click()
  await expect(page.getByText('导入任务已提交')).toBeVisible()
})
