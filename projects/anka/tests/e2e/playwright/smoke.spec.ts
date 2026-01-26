import { test, expect } from '@playwright/test';

test.describe('Smoke Tests', () => {
  test('should load landing page', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Anka/);
  });

  test('should allow login', async ({ page }) => {
    await page.goto('/login');
    
    // Fill login form
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'testpass123');
    
    // Submit
    await page.click('button[type="submit"]');
    
    // Expect dashboard
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.getByText('Dashboard')).toBeVisible();
  });
});
