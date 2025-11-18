import { test, expect } from '@playwright/test'

const BASE_URL = process.env.BASE_URL || 'http://localhost:5174'

test('创建导出任务成功提示', async ({ page }) => {
  await page.route('**/exports', async (route) => {
    await route.fulfill({ status: 201, contentType: 'application/json', body: JSON.stringify({ id: 'job-1' }) })
  })

  await page.goto(`${BASE_URL}/export`)
  await expect(page.getByRole('heading', { name: '数据导出' })).toBeVisible()
  await page.getByRole('button', { name: '创建导出' }).click()
  await expect(page.getByText('导出任务已创建')).toBeVisible()
})
