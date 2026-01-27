import { test, expect } from '@playwright/test';
import { seedJwtAuth } from './helpers/auth';

test.describe('Credit Purchase', () => {
  test.beforeEach(async ({ page }) => {
    await seedJwtAuth(page);
  });

  test('should navigate to checkout page', async ({ page }) => {
    await page.goto('/checkout');
    await expect(page.locator('h1')).toHaveText('Kredi Satın Al');
    
    // Future: Test credit package selection and payment flow
  });
});
