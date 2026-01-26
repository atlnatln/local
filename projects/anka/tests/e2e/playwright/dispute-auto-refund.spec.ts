import { test, expect } from '@playwright/test';

test.describe('Dispute Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'testpass123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('should view disputes', async ({ page }) => {
    await page.goto('/disputes');
    // Exact match for the main heading
    await expect(page.getByRole('heading', { name: 'İtirazlar', exact: true })).toBeVisible();
    
    // Future: Test creating a dispute and checking status
  });
});
