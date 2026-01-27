/**
 * MVP E2E: Auth (test-login) → checkout
 * Not: Prod'da auth Google-only; e2e ortamında test-login endpoint'i kullanılır.
 */

import { test, expect } from '@playwright/test';
import { seedJwtAuth } from './helpers/auth';

test.describe('Checkout (MVP)', () => {
  test('should show login page (Google-only)', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByText('Giriş Yap')).toBeVisible();
    await expect(page.locator('#googleSignInButton')).toBeVisible();
  });

  test('should access checkout when authenticated', async ({ page }) => {
    await seedJwtAuth(page);
    await page.goto('/checkout');
    await expect(page.locator('h1')).toHaveText('Kredi Satın Al');
  });
});
