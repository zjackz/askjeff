import { test, expect } from '@playwright/test';

test.describe('Chat Feature', () => {
    test('should open chat drawer and send message', async ({ page }) => {
        // 1. Visit the insight page
        await page.goto('/');
        await page.getByText('数据洞察').click();
        await expect(page).toHaveURL(/.*chat/);

        // 2. Click the FAB button to open chat
        const chatButton = page.locator('.chat-fab button');
        await expect(chatButton).toBeVisible();
        await chatButton.click();

        // 3. Verify drawer is open
        const drawer = page.locator('.chat-drawer');
        await expect(drawer).toBeVisible();
        await expect(page.getByText('智能数据洞察')).toBeVisible();

        // 4. Type a question
        const input = page.locator('.chat-input-area textarea');
        await input.fill('Test Question');

        // 5. Send message
        // Mock the backend response to avoid real API calls and costs
        await page.route('**/chat/query', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    answer: 'This is a mock answer from Playwright.',
                    sessionId: 'mock-session-id',
                    references: []
                })
            });
        });

        const sendButton = page.locator('.chat-actions button');
        await sendButton.click();

        // 6. Verify user message appears
        await expect(page.locator('.chat-message.user .message-bubble')).toHaveText('Test Question');

        // 7. Verify assistant response appears
        await expect(page.locator('.chat-message.assistant .message-bubble').last()).toHaveText('This is a mock answer from Playwright.');
    });
});
