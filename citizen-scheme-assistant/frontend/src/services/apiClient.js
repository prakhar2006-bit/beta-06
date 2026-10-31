const BASE_URL = import.meta.env?.VITE_API_BASE_URL || 'http://127.0.0.1:8001';
export class ApiError extends Error {
  constructor(code, status = 0, fields = []) { super(code); this.code = code; this.status = status; this.fields = fields; }
}
export class ApiClient {
  constructor(baseUrl = BASE_URL) { this.baseUrl = baseUrl.replace(/\/$/, ''); }
  async request(endpoint, options = {}) {
    const controller = new AbortController();
    const abort = () => controller.abort();
    options.signal?.addEventListener('abort', abort, { once: true });
    const timer = setTimeout(abort, 15000);
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, { ...options, signal: controller.signal,
        cache: 'no-store', headers: { Accept: 'application/json', 'Content-Type': 'application/json', ...options.headers } });
      const data = await response.json().catch(() => { throw new ApiError('INVALID_RESPONSE', response.status); });
      if (!response.ok) throw new ApiError(data?.error?.code || 'HTTP_ERROR', response.status, data?.error?.fields || []);
      return data;
    } catch (error) {
      if (error instanceof ApiError) throw error;
      throw new ApiError(controller.signal.aborted ? 'REQUEST_ABORTED' : 'NETWORK_ERROR');
    } finally { clearTimeout(timer); options.signal?.removeEventListener('abort', abort); }
  }
  get(endpoint, options) { return this.request(endpoint, { ...options, method: 'GET' }); }
  post(endpoint, body, options) { return this.request(endpoint, { ...options, method: 'POST', body: JSON.stringify(body) }); }
  checkHealth() { return this.get('/health'); }
}
export const apiClient = new ApiClient();
