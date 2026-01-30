import { AxiosInstance } from 'axios';
import { SignedUrlResponse } from '@/interfaces/models/Resource';

/**
 * Fetches a signed URL for a document download.
 */
export const getDocsSignedUrl = async (
  api: AxiosInstance,
  filename: string
): Promise<SignedUrlResponse> => {
  try {
    const response = await api.get(`/signed-urls/docs?filename=${encodeURIComponent(filename)}`);
    return response.data;
  } catch (error) {
    console.error('Error getting docs signed URL:', error);
    throw error;
  }
};
