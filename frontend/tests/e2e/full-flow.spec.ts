import { test, expect } from '@playwright/test'

const baseURL = 'http://localhost:5173'

const screenshotPath = 'tests/e2e/screenshots/full-flow.png'

test('导入→问答→导出全流程占位', async ({ page }) => {
  await page.goto(`${baseURL}/import`)
  await expect(page.getByText('文件导入')).toBeVisible()

  await page.goto(`${baseURL}/chat`)
  await expect(page.getByText('自然语言数据洞察')).toBeVisible()

  await page.goto(`${baseURL}/export`)
  await expect(page.getByText('数据导出')).toBeVisible()

  await page.screenshot({ path: screenshotPath, fullPage: true })
})
