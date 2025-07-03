import type { AxiosInstance } from 'axios';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const setupAuthInterceptor = (api: AxiosInstance, getSupabaseClient: any) => {
  api.interceptors.request.use(
    async (config) => {
      if (config.url?.includes('/auth') && !config.url?.includes('/auth/confirm')) {
        return config;
      }

      const supabase = await getSupabaseClient();
      const { data, error } = await supabase.auth.getSession();
      if (error || !data.session) {
        return Promise.reject(error || new Error('No session found'));
      }

      const accessToken = data.session.access_token;
      config.headers.set('Authorization', `Bearer ${accessToken}`);

      return config;
    },
    (error) => Promise.reject(error)
  );

  api.interceptors.response.use(
    (response) => response,
    (error) => {
      console.warn(error?.response);
      return Promise.reject(error);
    }
  );
};
