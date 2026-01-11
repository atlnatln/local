import './auth/test-helpers/polyfill';
import '@testing-library/jest-dom';
// MSW setup
import { server } from './auth/test-helpers/mswServer';

// Mock Leaflet images globally
jest.mock('leaflet/dist/images/marker-icon-2x.png', () => 'test-icon-2x.png');
jest.mock('leaflet/dist/images/marker-icon.png', () => 'test-icon.png');
jest.mock('leaflet/dist/images/marker-shadow.png', () => 'test-shadow.png');

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Enhanced localStorage mock with proper isolation
const localStorageMock = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { 
      store[key] = value.toString(); 
    },
    removeItem: (key: string) => { 
      delete store[key]; 
    },
    clear: () => { 
      store = {}; 
    },
    get length() {
      return Object.keys(store).length;
    },
    key: (index: number) => {
      const keys = Object.keys(store);
      return keys[index] || null;
    }
  };
})();

// Define localStorage as non-configurable to prevent JSDOM override issues
Object.defineProperty(global, 'localStorage', {
  value: localStorageMock,
  writable: true,
  configurable: false
});

// Also define it on window for compatibility
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
  writable: true,
  configurable: false
});

// Console mocking helpers for cleaner test output
export const suppressConsoleErrors = () => {
  const originalError = console.error;
  const originalLog = console.log;
  const originalWarn = console.warn;
  
  beforeAll(() => {
    console.error = jest.fn();
    console.log = jest.fn();
    console.warn = jest.fn();
  });
  
  afterAll(() => {
    console.error = originalError;
    console.log = originalLog;
    console.warn = originalWarn;
  });
};

// Global test environment setup
beforeEach(() => {
  // Clear all timers to prevent test interference
  jest.clearAllTimers();
  // Use fake timers only when needed (don't use globally)
  // jest.useFakeTimers();
});

afterEach(() => {
  // Restore real timers if fake timers were used
  if (jest.isMockFunction(setTimeout)) {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  }
});

// Establish API mocking before all tests.
beforeAll(() => {
  server.listen();
  // Ensure clean environment
  localStorageMock.clear();
});

// Reset any request handlers and clean up after each test
afterEach(() => {
  server.resetHandlers();
  // Clear localStorage after each test for isolation
  localStorageMock.clear();
  // Clean up any remaining timers
  jest.clearAllTimers();
  // Clear all mocks
  jest.clearAllMocks();
});

// Clean up after the tests are finished.
afterAll(() => {
  server.close();
  localStorageMock.clear();
});
