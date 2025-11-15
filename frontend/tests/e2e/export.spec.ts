import { test, expect } from '@playwright/test'

test('导出页面存在表单与按钮', async ({ page }) => {
  await page.goto('http://localhost:5173/export')
  await expect(page.getByText('数据导出')).toBeVisible()
  await expect(page.getByRole('button', { name: '创建导出' })).toBeVisible()
})
