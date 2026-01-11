// Polyfill for TextEncoder/TextDecoder in Jest + Node
import { TextEncoder, TextDecoder } from 'util';

if (typeof globalThis.TextEncoder === 'undefined') {
  globalThis.TextEncoder = TextEncoder;
}
if (typeof globalThis.TextDecoder === 'undefined') {
  globalThis.TextDecoder = TextDecoder as any;
}

export {};
