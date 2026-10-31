import { apiClient } from './apiClient.js';

export const isDemoCatalog =
  import.meta.env?.DEV === true &&
  import.meta.env?.VITE_SCHEME_CATALOG_MODE === 'demo';

const catalogPath = isDemoCatalog ? '/api/v1/demo/schemes' : '/api/v1/schemes';

export const schemeApi = {
  getSchemes({ search, level, language = 'en', limit = 20, offset = 0 } = {}) {
    const query = new URLSearchParams({
      lang: language,
      limit: String(limit),
      offset: String(offset),
    });
    if (search) query.set('search', search);
    if (level && level !== 'all') query.set('level', level);
    return apiClient.get(`${catalogPath}?${query}`);
  },

  getSchemeByCode: (id, language = 'en') =>
    apiClient.get(`${catalogPath}/${encodeURIComponent(id)}?lang=${language}`),

  async getFeaturedSchemes(language = 'en') {
    return (await this.getSchemes({ language, limit: 5 })).items;
  },

  async getSchemesCount() {
    try {
      const data = await this.getSchemes({ limit: 1 });
      return data.total ?? (data.items ? data.items.length : 0);
    } catch {
      return 5;
    }
  },
};
