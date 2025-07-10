import { AxiosInstance } from 'axios';

export interface SignedUrlResponse {
  url: string;
}

export const getDocsSignedUrl = async (
  api: AxiosInstance,
  filename: string
): Promise<SignedUrlResponse> => {
  try {
    const response = await api.get(`/signed-url/docs?filename=${encodeURIComponent(filename)}`);
    return response.data;
  } catch (error) {
    console.error('Error getting docs signed URL:', error);
    throw error;
  }
};
