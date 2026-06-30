import '@testing-library/jest-dom';
import { TextEncoder, TextDecoder } from 'util';

global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// React Router DOM v7 / Remix relies on Web Fetch APIs.
// JSDOM does not expose fetch/Request/Response globally by default, so we forward them from Node.
if (typeof global.fetch === 'undefined') {
  global.fetch = globalThis.fetch;
  global.Headers = globalThis.Headers;
  global.Request = globalThis.Request;
  global.Response = globalThis.Response;
}
