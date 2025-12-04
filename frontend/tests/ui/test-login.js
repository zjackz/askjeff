// UI 自动化测试 - 登录功能（增强版）
const { chromium } = require('playwright');

async function testLogin() {
    console.log('1. 启动浏览器...');
    const browser = await chromium.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
    });
    const context = await browser.newContext();
    const page = await context.newPage();

    // 监听控制台消息
    page.on('console', msg => console.log('   [浏览器]', msg.text()));

    // 监听页面错误
    page.on('pageerror', error => console.error('   [页面错误]', error.message));

    // 监听请求失败
    page.on('requestfailed', request => {
        console.error('   [请求失败]', request.url(), request.failure().errorText);
    });

    try {
        console.log('2. 访问登录页面...');
        await page.goto('http://localhost:5174', { timeout: 30000 });
        await page.waitForLoadState('networkidle', { timeout: 30000 });
        console.log('   ✓ 页面加载完成');

        console.log('3. 检查登录表单...');
        const usernameInput = page.locator('input[placeholder*="username" i]');
        const passwordInput = page.locator('input[type="password"]');
        const loginButton = page.locator('button[type="submit"]');

        await usernameInput.waitFor({ state: 'visible', timeout: 10000 });
        await passwordInput.waitFor({ state: 'visible', timeout: 10000 });
        await loginButton.waitFor({ state: 'visible', timeout: 10000 });
        console.log('   ✓ 登录表单元素已找到');

        console.log('4. 验证自动填充...');
        const usernameValue = await usernameInput.inputValue();
        const passwordValue = await passwordInput.inputValue();

        console.log('   用户名:', usernameValue);
        console.log('   密码:', '*'.repeat(passwordValue.length));

        if (usernameValue !== 'admin') {
            throw new Error('用户名应为 admin，实际为 ' + usernameValue);
        }
        if (passwordValue !== 'admin666') {
            throw new Error('密码应为 admin666');
        }
        console.log('   ✓ 自动填充验证通过');

        console.log('5. 点击登录按钮...');

        // 截图：登录前
        await page.screenshot({ path: '/tmp/before_login.png' });
        console.log('   ✓ 登录前截图: /tmp/before_login.png');

        // 等待导航
        const navigationPromise = page.waitForURL(/localhost:5174/, { timeout: 30000 });
        await loginButton.click();

        console.log('6. 等待登录完成...');

        try {
            await navigationPromise;
            console.log('   ✓ 页面已跳转');
        } catch (e) {
            console.log('   ! 等待跳转超时，检查当前状态...');
        }

        // 等待一下让页面稳定
        await page.waitForTimeout(3000);

        // 截图：登录后
        await page.screenshot({ path: '/tmp/after_login.png' });
        console.log('   ✓ 登录后截图: /tmp/after_login.png');

        console.log('7. 验证登录状态...');
        const currentUrl = page.url();
        console.log('   当前 URL:', currentUrl);

        // 检查是否有错误提示
        const errorMessage = await page.locator('.el-message--error').count();
        if (errorMessage > 0) {
            const errorText = await page.locator('.el-message--error').first().textContent();
            throw new Error('登录失败: ' + errorText);
        }

        // 检查是否还在登录页面
        if (currentUrl.includes('login')) {
            throw new Error('登录失败，仍在登录页面');
        }

        // 检查是否有导航菜单（说明已登录）
        const hasNav = await page.locator('.el-menu, nav, .sidebar').count() > 0;
        if (hasNav) {
            console.log('   ✓ 检测到导航菜单，登录成功');
        } else {
            console.log('   ! 未检测到导航菜单，但已离开登录页');
        }

        console.log('\n✅ 登录测试通过！');
        console.log('   最终 URL:', currentUrl);

    } catch (error) {
        console.error('\n❌ 测试失败:', error.message);

        // 失败时的详细信息
        try {
            const currentUrl = page.url();
            console.error('   当前 URL:', currentUrl);

            // 截图
            await page.screenshot({ path: '/tmp/test_failed.png', fullPage: true });
            console.error('   失败截图: /tmp/test_failed.png');

            // 获取页面内容
            const bodyText = await page.locator('body').textContent();
            console.error('   页面内容（前200字符）:', bodyText.substring(0, 200));
        } catch (e) {
            console.error('   无法获取失败详情:', e.message);
        }

        throw error;
    } finally {
        await browser.close();
    }
}

async function main() {
    console.log('='.repeat(60));
    console.log('UI 自动化测试 - 登录功能（增强版）');
    console.log('='.repeat(60));

    try {
        await testLogin();
        console.log('\n' + '='.repeat(60));
        console.log('所有测试通过！✅');
        console.log('='.repeat(60));
    } catch (error) {
        console.error('\n' + '='.repeat(60));
        console.error('测试失败 ❌');
        console.error('='.repeat(60));
        process.exit(1);
    }
}

main();
