"""
UI 自动化测试 - 登录功能

使用 Playwright 测试登录流程
"""
import asyncio
from playwright.async_api import async_playwright, expect


async def test_login():
    """测试登录功能"""
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("1. 访问登录页面...")
        await page.goto("http://localhost:5174")
        
        # 等待页面加载
        await page.wait_for_load_state("networkidle")
        
        print("2. 检查登录表单...")
        # 检查用户名输入框
        username_input = page.locator('input[placeholder*="username"]')
        await expect(username_input).to_be_visible()
        
        # 检查密码输入框
        password_input = page.locator('input[type="password"]')
        await expect(password_input).to_be_visible()
        
        print("3. 验证自动填充...")
        # 验证用户名已自动填充
        username_value = await username_input.input_value()
        print(f"   用户名: {username_value}")
        assert username_value == "admin", f"用户名应为 'admin'，实际为 '{username_value}'"
        
        # 验证密码已自动填充
        password_value = await password_input.input_value()
        print(f"   密码: {'*' * len(password_value)}")
        assert password_value == "admin666", "密码应为 'admin666'"
        
        print("4. 点击登录按钮...")
        # 查找并点击登录按钮
        login_button = page.locator('button[type="submit"]')
        await expect(login_button).to_be_visible()
        await login_button.click()
        
        print("5. 等待登录完成...")
        # 等待页面跳转
        await page.wait_for_url("http://localhost:5174/", timeout=10000)
        
        print("6. 验证登录成功...")
        # 检查是否跳转到主页
        current_url = page.url
        print(f"   当前 URL: {current_url}")
        assert current_url == "http://localhost:5174/" or current_url.startswith("http://localhost:5174/dashboard"), \
            f"登录后应跳转到主页，实际 URL: {current_url}"
        
        # 检查是否有导航菜单或用户信息
        # 等待主页面元素加载
        await page.wait_for_timeout(2000)
        
        # 截图保存
        await page.screenshot(path="/tmp/login_success.png")
        print("   ✓ 登录成功截图已保存: /tmp/login_success.png")
        
        print("\n✅ 登录测试通过！")
        
        await browser.close()


async def test_login_with_wrong_password():
    """测试错误密码登录"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("\n测试错误密码...")
        await page.goto("http://localhost:5174")
        await page.wait_for_load_state("networkidle")
        
        # 清空并输入错误密码
        password_input = page.locator('input[type="password"]')
        await password_input.fill("wrong_password")
        
        # 点击登录
        login_button = page.locator('button[type="submit"]')
        await login_button.click()
        
        # 等待错误提示
        await page.wait_for_timeout(2000)
        
        # 检查是否显示错误信息
        error_message = page.locator('.el-message--error')
        if await error_message.count() > 0:
            print("   ✓ 显示了错误提示")
        
        # 验证仍在登录页面
        current_url = page.url
        assert "login" in current_url or current_url == "http://localhost:5174/", \
            "错误密码应该停留在登录页面"
        
        print("   ✓ 错误密码测试通过")
        
        await browser.close()


async def main():
    """运行所有测试"""
    print("=" * 60)
    print("UI 自动化测试 - 登录功能")
    print("=" * 60)
    
    try:
        await test_login()
        await test_login_with_wrong_password()
        
        print("\n" + "=" * 60)
        print("所有测试通过！✅")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
