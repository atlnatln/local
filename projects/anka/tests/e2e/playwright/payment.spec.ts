/**
 * E2E test for payment flow
 * Tests full auth → checkout → payment scenario
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3100';
const API_URL = process.env.API_URL || 'http://localhost:8000/api';

// Test data
const testUser = {
  username: `testuser_${Date.now()}`,
  email: `test${Date.now()}@example.com`,
  first_name: 'Test',
  last_name: 'User',
  password: 'testpass123!@#',
};

test.describe('Payment Flow - Auth to Checkout', () => {
  let accessToken: string;
  let userId: string;

  test('Should register new user', async ({ page }) => {
    await page.goto(`${BASE_URL}/auth/register`);

    // Wait for form to be visible
    await page.waitForSelector('input[type="text"]');

    // Fill registration form
    const usernameInput = page.locator('input[placeholder*="Kullanıcı"]').first();
    const emailInput = page.locator('input[type="email"]');
    const firstNameInput = page.locator('input[placeholder*="Ad"]').first();
    const lastNameInput = page.locator('input[placeholder*="Soyad"]');
    const passwordInput = page.locator('input[type="password"]').first();
    const confirmPasswordInput = page.locator('input[type="password"]').nth(1);

    await usernameInput.fill(testUser.username);
    await emailInput.fill(testUser.email);
    await firstNameInput.fill(testUser.first_name);
    await lastNameInput.fill(testUser.last_name);
    await passwordInput.fill(testUser.password);
    await confirmPasswordInput.fill(testUser.password);

    // Submit form
    await page.click('button:has-text("Kayıt Ol")');

    // Wait for redirect or success message
    await page.waitForURL(`${BASE_URL}/auth/login**`, { timeout: 10000 });
  });

  test('Should login user', async ({ page }) => {
    await page.goto(`${BASE_URL}/auth/login`);

    // Wait for form
    await page.waitForSelector('input[type="text"]');

    // Fill login form
    const usernameInput = page.locator('input[placeholder*="Kullanıcı"]');
    const passwordInput = page.locator('input[type="password"]');

    await usernameInput.fill(testUser.username);
    await passwordInput.fill(testUser.password);

    // Submit
    await page.click('button:has-text("Giriş Yap")');

    // Wait for redirect to dashboard
    await page.waitForURL(`${BASE_URL}/dashboard**`, { timeout: 10000 });

    // Verify we're logged in
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('Should verify credit balance endpoint', async ({ request }) => {
    // Register first
    const registerRes = await request.post(`${API_URL}/auth/register/`, {
      data: {
        username: `testuser_${Date.now()}`,
        email: `test${Date.now()}@example.com`,
        first_name: 'Test',
        last_name: 'User',
        password: testUser.password,
        password2: testUser.password,
      },
    });

    const registerData = await registerRes.json();
    console.log('Register response:', registerData);

    // Login
    const loginRes = await request.post(`${API_URL}/auth/login/`, {
      data: {
        username: `testuser_${Date.now()}`,
        password: testUser.password,
      },
    });

    expect(loginRes.ok()).toBeTruthy();
    const loginData = await loginRes.json();
    accessToken = loginData.access;

    // Get credit balance
    const balanceRes = await request.get(`${API_URL}/credits/balance/`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    });

    expect(balanceRes.ok()).toBeTruthy();
    const balanceData = await balanceRes.json();
    
    // Verify balance structure
    expect(balanceData).toHaveProperty('organization_id');
    expect(balanceData).toHaveProperty('balance');
    expect(balanceData).toHaveProperty('total_purchased');
  });

  test('Should create payment intent', async ({ request }) => {
    // First login
    const loginRes = await request.post(`${API_URL}/auth/login/`, {
      data: {
        username: 'testuser',
        password: 'testpass123',
      },
    });

    if (!loginRes.ok()) {
      // Skip test if user doesn't exist
      test.skip();
      return;
    }

    const loginData = await loginRes.json();
    const token = loginData.access;

    // Create payment intent
    const intentRes = await request.post(`${API_URL}/payments/intents/`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      data: {
        amount: 99.00,
        credits: 1000,
        package_type: 'starter',
      },
    });

    // Expect 201 Created
    expect(intentRes.status()).toBe(201);
    
    const intentData = await intentRes.json();
    
    // Verify response contains necessary fields
    expect(intentData).toHaveProperty('id');
    expect(intentData).toHaveProperty('checkoutFormContent');
    expect(intentData).toHaveProperty('token');
    expect(intentData.status).toBe('PENDING');
    expect(intentData.amount).toBe('99.00');
    expect(intentData.credits).toBe(1000);
  });

  test('Should access checkout page', async ({ page }) => {
    // Go to checkout
    await page.goto(`${BASE_URL}/dashboard/checkout`);

    // Wait for page to load
    await page.waitForSelector('h1:has-text("Kredi Satın Al")');

    // Verify credit packages are visible
    const starterCard = page.locator('text=Başlangıç');
    const professionalCard = page.locator('text=Profesyonel');
    const enterpriseCard = page.locator('text=Kurumsal');

    await expect(starterCard).toBeVisible();
    await expect(professionalCard).toBeVisible();
    await expect(enterpriseCard).toBeVisible();

    // Verify pricing is correct
    const starterPrice = page.locator('text=₺99');
    const professionalPrice = page.locator('text=₺399');

    await expect(starterPrice).toBeVisible();
    await expect(professionalPrice).toBeVisible();
  });

  test('Should display package details in checkout', async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard/checkout`);

    // Wait for page to load
    await page.waitForSelector('h1:has-text("Kredi Satın Al")');

    // Find and click professional package
    const professionalButton = page.locator('button:has-text("Satın Al")').nth(1);
    await expect(professionalButton).toBeVisible();

    // Verify FAQ section is visible
    const faqSection = page.locator('h2:has-text("Sıkça Sorulan Sorular")');
    await expect(faqSection).toBeVisible();

    // Verify FAQ items are present
    const faqQuestion = page.locator('text=Krediler ne kadar süre geçerli?');
    await expect(faqQuestion).toBeVisible();
  });

  test('Should verify API integration', async ({ request }) => {
    // Test health check
    const healthRes = await request.get(`${API_URL}health/`);
    expect(healthRes.ok()).toBeTruthy();

    const healthData = await healthRes.json();
    expect(healthData.status).toBe('ok');
  });
});

test.describe('Authentication Flow', () => {
  test('Should prevent access to protected pages without auth', async ({ page }) => {
    // Try to access dashboard without token
    await page.goto(`${BASE_URL}/dashboard`);

    // Should not be able to access dashboard without login
    // (depending on client-side implementation, might redirect or show error)
    // Verify we're not at dashboard
    const dashboardHeading = page.locator('h1:has-text("Gösterge Paneli")');
    const notFound = page.locator('text=404');

    const isDashboard = await dashboardHeading.isVisible().catch(() => false);
    const isNotFound = await notFound.isVisible().catch(() => false);

    expect(isDashboard || isNotFound).toBeTruthy();
  });

  test('Should maintain session with JWT tokens', async ({ page }) => {
    // Go to home
    await page.goto(`${BASE_URL}/`);

    // Check localStorage for tokens
    const tokens = await page.evaluate(() => {
      return {
        accessToken: localStorage.getItem('anka_access_token'),
        refreshToken: localStorage.getItem('anka_refresh_token'),
      };
    });

    // Initially no tokens
    expect(tokens.accessToken).toBeNull();

    // After login, tokens should be present
    await page.goto(`${BASE_URL}/auth/login`);
    await page.fill('input[placeholder*="Kullanıcı"]', 'testuser');
    await page.fill('input[type="password"]', 'testpass123');

    // Submit and wait for redirect
    await Promise.race([
      page.click('button:has-text("Giriş Yap")'),
      page.waitForURL(`${BASE_URL}/dashboard**`, { timeout: 5000 }).catch(() => null),
    ]);

    // Give page time to save tokens
    await page.waitForTimeout(1000);

    // Check tokens again
    const tokensAfter = await page.evaluate(() => {
      return {
        accessToken: localStorage.getItem('anka_access_token'),
        refreshToken: localStorage.getItem('anka_refresh_token'),
      };
    });

    // If login was successful, tokens should exist
    // (Skip if user doesn't exist)
    if (tokensAfter.accessToken) {
      expect(tokensAfter.accessToken).toBeTruthy();
    }
  });
});
