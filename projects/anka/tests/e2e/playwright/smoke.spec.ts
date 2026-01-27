import { test, expect } from '@playwright/test';
import { seedJwtAuth } from './helpers/auth';

test.describe('Smoke Tests', () => {
  test('should redirect to login when unauthenticated', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByText('Giriş Yap')).toBeVisible();
  });

  test('should allow accessing dashboard with seeded JWT', async ({ page }) => {
    await seedJwtAuth(page);
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.getByText('Dashboard')).toBeVisible();
  });
});
