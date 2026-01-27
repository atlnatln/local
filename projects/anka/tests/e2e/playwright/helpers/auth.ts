import type { Page } from '@playwright/test';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

type TestLoginResponse = {
  access: string;
  refresh: string;
};

export async function seedJwtAuth(page: Page, user?: { username?: string; email?: string }) {
  const res = await page.request.post(`${BACKEND_URL}/api/auth/test-login/`, {
    data: {
      username: user?.username || 'testuser',
      email: user?.email || 'testuser@example.com',
    },
  });

  if (!res.ok()) {
    throw new Error(`test-login failed: ${res.status()} ${await res.text()}`);
  }

  const data = (await res.json()) as TestLoginResponse;

  await page.addInitScript(
    ({ access, refresh }) => {
      const now = new Date();
      const expiresAt = new Date(now.getTime() + 10 * 60 * 1000);
      localStorage.setItem('anka_access_token', access);
      localStorage.setItem('anka_refresh_token', refresh);
      localStorage.setItem('anka_token_expires', expiresAt.toISOString());
    },
    { access: data.access, refresh: data.refresh }
  );
}
