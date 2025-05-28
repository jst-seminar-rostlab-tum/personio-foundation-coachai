import { MetadataRoute } from 'next';

const BASE_URL = 'https://personiofoundation-coachai.com';

export default function sitemap(): MetadataRoute.Sitemap {
  const routes = [
    {
      url: BASE_URL,
      lastModified: new Date(),
      changeFrequency: 'monthly' as const,
      priority: 1,
    },
    {
      url: `${BASE_URL}/de`,
      lastModified: new Date(),
      changeFrequency: 'monthly' as const,
      priority: 1,
    },
    {
      url: `${BASE_URL}/login`,
      lastModified: new Date(),
      changeFrequency: 'monthly' as const,
      priority: 0.8,
    },
    {
      url: `${BASE_URL}/de/login`,
      lastModified: new Date(),
      changeFrequency: 'monthly' as const,
      priority: 0.8,
    },
  ];

  return routes;
}
