import Api from '../Api';

describe('api instance', () => {
  it('adds Authorization header if token exists', async () => {
    localStorage.setItem('token', 'mock-token');
    const request = await Api.interceptors.request.handlers[0].fulfilled({
      headers: {},
    });
    expect(request.headers.Authorization).toBe('Bearer mock-token');
  });

  it('leaves headers unchanged if no token exists', async () => {
    localStorage.removeItem('token');
    const request = await Api.interceptors.request.handlers[0].fulfilled({
      headers: {},
    });
    expect(request.headers.Authorization).toBeUndefined();
  });
});
