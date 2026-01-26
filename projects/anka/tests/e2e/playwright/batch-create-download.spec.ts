import { test, expect } from '@playwright/test';

test.describe('Batch Creation Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'testpass123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('should create a new batch with criteria', async ({ page }) => {
    await page.goto('/batch/new');

    // Wait for form to load (config loading)
    await expect(page.locator('form')).toBeVisible();

    // Select Organization (selects first available by value if we don't know ID, 
    // but here we select by index or just the first option that isn't empty)
    // Actually the code defaults to selecting the first org, so we might not need to touch it if there is one.
    // Let's verify it has a value.
    const orgSelect = page.locator('select[name="organization"]');
    await expect(orgSelect).not.toHaveValue('');

    // Select City
    await page.selectOption('select[name="city"]', { index: 1 }); // Select second option (first is empty default)

    // Select Sector
    await page.selectOption('select[name="sector"]', { index: 1 });

    // Fill Estimate
    await page.fill('input[name="record_count_estimate"]', '500');

    // Submit
    await page.click('button[type="submit"]');

    // Expect redirect to dashboard or batch list
    await expect(page).toHaveURL(/\/dashboard/);
    
    // Optionally check for success message or new item in list
    // await expect(page.getByText('Batch oluşturuldu')).toBeVisible();
  });
});
