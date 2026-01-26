import { test, expect } from '@playwright/test';

test.describe('Credit Purchase', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'testpass123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('should navigate to checkout page', async ({ page }) => {
    await page.goto('/checkout');
    await expect(page.locator('h1')).toHaveText('Kredi Satın Al');
    
    // Future: Test credit package selection and payment flow
  });
});
