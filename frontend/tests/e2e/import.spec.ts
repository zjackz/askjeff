import { test, expect } from '@playwright/test'

test('运营可上传 Sorftime 文件', async ({ page }) => {
  await page.goto('http://localhost:5173/import')
  await expect(page.locator('h1')).toContainText('文件导入')
  const fileInput = page.locator('input[type="file"]')
  await fileInput.setInputFiles('tests/fixtures/sorftime-demo.xlsx')
  await page.getByRole('button', { name: '开始导入' }).click()
  await expect(page.getByText('导入成功')).toBeVisible()
})
