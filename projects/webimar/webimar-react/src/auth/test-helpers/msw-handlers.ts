import { rest } from 'msw';
import { mockUser } from './mockUser';

const apiBase = 'http://localhost:8000';

// Environment-specific configurations for realistic testing
export const testScenarios = {
  SUCCESS: 'success',
  CORS_ERROR: 'cors_error',
  NETWORK_ERROR: 'network_error',
  SERVER_ERROR: 'server_error',
  SLOW_RESPONSE: 'slow_response',
  TIMEOUT: 'timeout',
  RATE_LIMIT: 'rate_limit'
};

// Current test scenario (can be changed in tests)
let currentScenario = testScenarios.SUCCESS;

export const setTestScenario = (scenario: string) => {
  currentScenario = scenario;
  console.log(`🧪 Test scenario set to: ${scenario}`);
};

export const resetTestScenario = () => {
  currentScenario = testScenarios.SUCCESS;
};

// Enhanced handlers with realistic error simulations
function createRealisticHandler(successHandler: Function) {
  return (req: any, res: any, ctx: any) => {
    // Simulate different network conditions based on scenario
    switch (currentScenario) {
      case testScenarios.CORS_ERROR:
        console.log('🚨 Simulating CORS error');
        // Simulate CORS error using network error (MSW v1.x compatible)
        return res.networkError('CORS error - Network request failed');
        
      case testScenarios.NETWORK_ERROR:
        console.log('🚨 Simulating network error');
        return res.networkError('Network request failed');
        
      case testScenarios.SERVER_ERROR:
        console.log('🚨 Simulating server error');
        return res(
          ctx.status(500),
          ctx.json({ 
            detail: 'Internal server error',
            code: 'SERVER_ERROR' 
          })
        );
        
      case testScenarios.SLOW_RESPONSE:
        console.log('🐌 Simulating slow response');
        // MSW v1.x için delay kullanımı
        return res(
          ctx.delay(2000), // 2 second delay
          ctx.status(200),
          ctx.json({ 
            access: 'mock-access-token', 
            refresh: 'mock-refresh-token' 
          })
        );
        
      case testScenarios.TIMEOUT:
        console.log('⏰ Simulating timeout');
        // Very long delay to simulate timeout
        return res(
          ctx.delay(8000), // 8 second delay
          ctx.status(200),
          ctx.json({ 
            access: 'mock-access-token', 
            refresh: 'mock-refresh-token' 
          })
        );
        
      case testScenarios.RATE_LIMIT:
        console.log('🚫 Simulating rate limit');
        return res(
          ctx.status(429),
          ctx.json({ 
            detail: 'Too many requests. Please try again later.',
            code: 'RATE_LIMIT_ERROR' 
          })
        );
        
      default:
        return successHandler(req, res, ctx);
    }
  };
}

function loginHandler(req: any, res: any, ctx: any) {
  const { username, password } = req.body as any;
  // Django'da test@example.com kullanıcısının username'i test@example.com, şifresi TestPass123!
  if (username === mockUser.email && password === 'TestPass123!') {
    return res(
      ctx.status(200),
      ctx.json({ 
        access: 'mock-access-token', 
        refresh: 'mock-refresh-token' 
      })
    );
  }
  return res(
    ctx.status(401),
    ctx.json({ detail: 'Kullanıcı adı veya şifre hatalı. Lütfen tekrar deneyin.' })
  );
}

function registerHandler(req: any, res: any, ctx: any) {
  const { email } = req.body as any;
  if (email === mockUser.email) {
    return res(
      ctx.status(409),
      ctx.json({ detail: 'Bu e-posta adresi zaten kullanımda.' })
    );
  }
  return res(
    ctx.status(201),
    ctx.json({ 
      access: 'mock-access-token', 
      refresh: 'mock-refresh-token' 
    })
  );
}

function profileHandler(req: any, res: any, ctx: any) {
  return res(
    ctx.status(200),
    ctx.json(mockUser)
  );
}

function logoutHandler(req: any, res: any, ctx: any) {
  return res(ctx.status(200));
}

// Enhanced handlers with realistic error scenarios
const enhancedLoginHandler = createRealisticHandler(loginHandler);
const enhancedRegisterHandler = createRealisticHandler(registerHandler);
const enhancedProfileHandler = createRealisticHandler(profileHandler);
const enhancedLogoutHandler = createRealisticHandler(logoutHandler);

export const handlers = [
  // JWT token endpoints
  rest.post('/api/token', createRealisticHandler(loginHandler)),
  rest.post(apiBase + '/api/token/', createRealisticHandler(loginHandler)),
  // Register endpoints 
  rest.post('/api/accounts/register', createRealisticHandler(registerHandler)),
  rest.post(apiBase + '/api/accounts/register/', createRealisticHandler(registerHandler)),
  // Profile endpoints
  rest.get('/api/accounts/me', createRealisticHandler(profileHandler)),
  rest.get(apiBase + '/api/accounts/me/', createRealisticHandler(profileHandler)),
  // Logout endpoints
  rest.post('/api/accounts/me/logout', createRealisticHandler(logoutHandler)),
  rest.post(apiBase + '/api/accounts/me/logout/', createRealisticHandler(logoutHandler)),
  // Enhanced CORS preflight handling with error simulation
  rest.options(apiBase + '/api/token/', (req, res, ctx) => {
    if (currentScenario === testScenarios.CORS_ERROR) {
      console.log('🚨 Simulating CORS preflight failure');
      return res(ctx.status(0)); // Simulate CORS failure
    }
    return res(
      ctx.status(200),
      ctx.set('Access-Control-Allow-Origin', req.headers.get('origin') || '*'),
      ctx.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
      ctx.set('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
      ctx.set('Access-Control-Allow-Credentials', 'true')
    );
  }),
  
  rest.options(apiBase + '/api/accounts/me/', (req, res, ctx) => {
    if (currentScenario === testScenarios.CORS_ERROR) {
      return res(ctx.status(0));
    }
    return res(
      ctx.status(200),
      ctx.set('Access-Control-Allow-Origin', req.headers.get('origin') || '*'),
      ctx.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
      ctx.set('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
      ctx.set('Access-Control-Allow-Credentials', 'true')
    );
  }),
  
  rest.options(apiBase + '/api/accounts/register/', (req, res, ctx) => {
    if (currentScenario === testScenarios.CORS_ERROR) {
      return res(ctx.status(0));
    }
    return res(
      ctx.status(200),
      ctx.set('Access-Control-Allow-Origin', req.headers.get('origin') || '*'),
      ctx.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
      ctx.set('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
      ctx.set('Access-Control-Allow-Credentials', 'true')
    );
  }),
];
