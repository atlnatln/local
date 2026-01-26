import { test, expect } from '@playwright/test';

test.describe('OpenAPI Contract', () => {
  test('should expose valid openapi schema', async ({ request }) => {
    const response = await request.get('/api/schema/');
    expect(response.ok()).toBeTruthy();
    
    const schema = await response.json();
    expect(schema).toHaveProperty('openapi');
    expect(schema).toHaveProperty('info');
    expect(schema).toHaveProperty('paths');
    expect(schema.info).toHaveProperty('title');
    expect(schema.info).toHaveProperty('version');
  });

  test('should expose swagger ui', async ({ page }) => {
    await page.goto('/api/docs/');
    await expect(page).toHaveTitle(/Swagger|API/i);
  });
});
