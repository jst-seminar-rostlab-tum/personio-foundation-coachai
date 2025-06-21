import { api } from './Api';

const getAnswerSdp = async (offerSdp: string): Promise<string> => {
  const response = await api.post(`/webrtc/offer`, offerSdp, {
    headers: {
      'Content-Type': 'application/sdp',
    },
    responseType: 'text',
  });
  return response.data;
};

export const webRTCService = {
  getAnswerSdp,
};
