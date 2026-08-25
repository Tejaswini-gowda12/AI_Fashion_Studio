import axios from 'axios';
import {
  User, Project, FabricAnalysis, FabricDetectionRecord, FabricRecommendation,
  DyeRecommendation, ImpactAssessment, DesignConcept,
  ChatMessage, GeneratedImage, Fabric, DyeMethod, PriorityWeights,
  VisualSearchResponse, SaveMatchRequest, SavedWebMatch,
} from '../types';
import {
  OutfitGenerateRequest,
  OutfitGenerateResponse,
  OutfitHistoryItem,
  SavedOutfit,
  ProductResult,
  PriceComparisonResponse,
  PriceAlertRequest,
  PriceAlertResponse,
  PriceHistoryResponse,
  RetailerCoupon,
} from '../types/outfit';

const API_BASE_URL = '/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authService = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }
    return response.data;
  },
  register: async (userData: { email: string; password: string; full_name: string }) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
  getMe: async (): Promise<User> => {
    const response = await api.get('/auth/me');
    return response.data;
  },
  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await api.put('/users/profile', data);
    return response.data;
  },
  logout: () => {
    localStorage.removeItem('token');
  }
};

export const projectService = {
  list: async (): Promise<Project[]> => {
    const response = await api.get('/projects/');
    return response.data;
  },
  get: async (id: number): Promise<Project> => {
    const response = await api.get(`/projects/${id}`);
    return response.data;
  },
  create: async (data: Partial<Project>): Promise<Project> => {
    const response = await api.post('/projects/', data);
    return response.data;
  },
  update: async (id: number, data: Partial<Project>): Promise<Project> => {
    const response = await api.put(`/projects/${id}`, data);
    return response.data;
  },
  delete: async (id: number): Promise<void> => {
    await api.delete(`/projects/${id}`);
  },
  duplicate: async (id: number): Promise<Project> => {
    const response = await api.post(`/projects/${id}/duplicate`);
    return response.data;
  }
};

export const fabricDetectionService = {
  analyze: async (file: File, projectId?: number): Promise<FabricDetectionRecord> => {
    const formData = new FormData();
    formData.append('file', file);
    if (projectId) {
      formData.append('project_id', projectId.toString());
    }
    const response = await api.post('/fabric-detection/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },
  get: async (analysisId: number): Promise<FabricDetectionRecord> => {
    const response = await api.get(`/fabric-detection/${analysisId}`);
    return response.data;
  },
  correct: async (analysisId: number, payload: { user_corrected_fabric: string; garment_type?: string; material_properties?: any }): Promise<FabricDetectionRecord> => {
    const response = await api.patch(`/fabric-detection/${analysisId}`, payload);
    return response.data;
  },
  delete: async (analysisId: number): Promise<void> => {
    await api.delete(`/fabric-detection/${analysisId}`);
  },
  getHistory: async (): Promise<FabricDetectionRecord[]> => {
    const response = await api.get('/fabric-detection/history');
    return response.data;
  }
};

export const analysisService = {
  uploadAndAnalyze: async (projectId: number, file: File): Promise<FabricAnalysis> => {
    const formData = new FormData();
    formData.append('project_id', projectId.toString());
    formData.append('file', file);
    const response = await api.post('/analysis/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },
  get: async (analysisId: number): Promise<FabricAnalysis> => {
    const response = await api.get(`/analysis/${analysisId}`);
    return response.data;
  },
  update: async (analysisId: number, data: Partial<FabricAnalysis>): Promise<FabricAnalysis> => {
    const response = await api.put(`/analysis/${analysisId}`, data);
    return response.data;
  }
};

export const recommendationService = {
  getFabricRecommendations: async (analysisId: number, weights: PriorityWeights): Promise<FabricRecommendation[]> => {
    const response = await api.post('/recommendations/', { analysis_id: analysisId, weights });
    return response.data;
  },
  getDyeRecommendations: async (analysisId: number, fabricId: number): Promise<DyeRecommendation[]> => {
    const response = await api.get('/dyeing/', { params: { analysis_id: analysisId, fabric_id: fabricId } });
    return response.data;
  }
};

export const impactService = {
  calculate: async (payload: {
    analysis_id: number;
    conventional_fabric_name?: string;
    selected_fabric_id: number;
    conventional_dye_name?: string;
    selected_dye_id: number;
    garment_weight_kg?: number;
  }): Promise<ImpactAssessment> => {
    const response = await api.post('/impact/calculate', payload);
    return response.data;
  },
  downloadPdfReport: async (analysisId: number, fabricId: number, dyeId: number) => {
    const response = await api.get('/reports/download', {
      params: { analysis_id: analysisId, fabric_id: fabricId, dye_id: dyeId },
      responseType: 'blob'
    });
    return response.data;
  }
};

export const assistantService = {
  getChatHistory: async (projectId: number): Promise<ChatMessage[]> => {
    const response = await api.get(`/chat/project/${projectId}`);
    return response.data;
  },
  sendMessage: async (projectId: number, content: string): Promise<ChatMessage> => {
    const response = await api.post('/chat/send', { project_id: projectId, content });
    return response.data;
  },
  getConcepts: async (projectId: number): Promise<DesignConcept[]> => {
    const response = await api.get(`/concepts/project/${projectId}`);
    return response.data;
  },
  createConcept: async (data: Partial<DesignConcept>): Promise<DesignConcept> => {
    const response = await api.post('/concepts/', data);
    return response.data;
  },
  getGeneratedImages: async (projectId: number): Promise<GeneratedImage[]> => {
    const response = await api.get(`/generated-images/project/${projectId}`);
    return response.data;
  },
  generateConceptImage: async (projectId: number, conceptId?: number, customPromptSuffix?: string): Promise<GeneratedImage> => {
    const response = await api.post('/generated-images/generate', {
      project_id: projectId,
      concept_id: conceptId,
      custom_prompt_suffix: customPromptSuffix || ''
    });
    return response.data;
  }
};

export const adminService = {
  listFabrics: async (): Promise<Fabric[]> => {
    const response = await api.get('/admin/fabrics');
    return response.data;
  },
  createFabric: async (data: Partial<Fabric>): Promise<Fabric> => {
    const response = await api.post('/admin/fabrics', data);
    return response.data;
  },
  updateFabric: async (id: number, data: Partial<Fabric>): Promise<Fabric> => {
    const response = await api.put(`/admin/fabrics/${id}`, data);
    return response.data;
  },
  toggleFabric: async (id: number): Promise<Fabric> => {
    const response = await api.patch(`/admin/fabrics/${id}/toggle-active`);
    return response.data;
  },
  listDyeMethods: async (): Promise<DyeMethod[]> => {
    const response = await api.get('/admin/dye-methods');
    return response.data;
  },
  createDyeMethod: async (data: Partial<DyeMethod>): Promise<DyeMethod> => {
    const response = await api.post('/admin/dye-methods', data);
    return response.data;
  },
  updateDyeMethod: async (id: number, data: Partial<DyeMethod>): Promise<DyeMethod> => {
    const response = await api.put(`/admin/dye-methods/${id}`, data);
    return response.data;
  },
  toggleDyeMethod: async (id: number): Promise<DyeMethod> => {
    const response = await api.patch(`/admin/dye-methods/${id}/toggle-active`);
    return response.data;
  },
  getModelMetrics: async (): Promise<any> => {
    const response = await axios.get('/api/admin/model-metrics');
    return response.data;
  },
  trainModel: async (params?: { model_name?: string; epochs?: number }): Promise<any> => {
    const token = localStorage.getItem('token');
    const response = await axios.post('/api/admin/train-model', params || {}, {
      headers: { Authorization: token ? `Bearer ${token}` : '' }
    });
    return response.data;
  }
};

export const fabricService = {
  analyze: async (file: File, projectId?: number) => {
    const formData = new FormData();
    formData.append('file', file);
    if (projectId) formData.append('project_id', projectId.toString());

    const response = await axios.post('/api/fabric/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },
  getAnalyses: async (): Promise<any[]> => {
    const response = await axios.get('/api/fabric/analyses');
    return response.data;
  },
  getAnalysis: async (id: number): Promise<any> => {
    const response = await axios.get(`/api/fabric/analyses/${id}`);
    return response.data;
  },
  correct: async (id: number, payload: { user_corrected_fabric: string }): Promise<any> => {
    const response = await axios.patch(`/api/fabric/analyses/${id}/correction`, payload);
    return response.data;
  },
  submitFeedback: async (payload: {
    analysis_id?: number;
    predicted_fabric: string;
    corrected_fabric: string;
    verified_composition?: string;
    physical_test_method?: string;
    feedback_notes?: string;
  }): Promise<any> => {
    const response = await axios.post('/api/fabric/feedback', payload);
    return response.data;
  }
};

export const visualSearchService = {
  search: async (
    file: File,
    aiPredictedFabric?: string,
    garmentCategory?: string,
    resultLimit?: number
  ): Promise<VisualSearchResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    if (aiPredictedFabric) formData.append('ai_predicted_fabric', aiPredictedFabric);
    if (garmentCategory) formData.append('garment_category', garmentCategory);
    if (resultLimit) formData.append('result_limit', resultLimit.toString());

    const response = await axios.post<VisualSearchResponse>('/api/visual-search/search', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  saveMatch: async (payload: SaveMatchRequest): Promise<SavedWebMatch> => {
    const token = localStorage.getItem('token');
    const response = await axios.post<SavedWebMatch>('/api/visual-search/save-match', payload, {
      headers: {
        Authorization: token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json'
      }
    });
    return response.data;
  },

  getSavedMatches: async (): Promise<SavedWebMatch[]> => {
    const token = localStorage.getItem('token');
    const response = await axios.get<SavedWebMatch[]>('/api/visual-search/saved', {
      headers: {
        Authorization: token ? `Bearer ${token}` : ''
      }
    });
    return response.data;
  }
};

export const outfitStudioService = {
  /**
   * Generate an AI outfit concept from a scenario description.
   * Works for anonymous users; saving requires auth.
   */
  generate: async (request: OutfitGenerateRequest): Promise<OutfitGenerateResponse> => {
    const response = await axios.post<OutfitGenerateResponse>('/api/outfit/generate', request);
    return response.data;
  },

  /** Regenerate the outfit visualization image or specific variation for an existing generation. */
  regenerateImage: async (
    generationId: number,
    variationIndex?: number
  ): Promise<{
    image_url: string;
    image_id: number;
    variation_index?: number;
    variation_title?: string;
    status?: string;
    label: string;
    prompt?: string;
  }> => {
    const params = variationIndex ? { variation_index: variationIndex } : undefined;
    const response = await axios.post(`/api/outfit/${generationId}/regenerate-image`, null, { params });
    return response.data;
  },

  /** Get a specific generation by ID. */
  getGeneration: async (generationId: number): Promise<OutfitGenerateResponse> => {
    const response = await axios.get<OutfitGenerateResponse>(`/api/outfit/${generationId}`);
    return response.data;
  },

  /** Get the authenticated user's generation history. */
  getHistory: async (): Promise<OutfitHistoryItem[]> => {
    const token = localStorage.getItem('token');
    const response = await axios.get<OutfitHistoryItem[]>('/api/outfit/history', {
      headers: { Authorization: token ? `Bearer ${token}` : '' }
    });
    return response.data;
  },

  /** Save an outfit generation to user profile. */
  saveOutfit: async (
    generationId: number,
    projectId?: number,
    notes?: string,
  ): Promise<SavedOutfit> => {
    const token = localStorage.getItem('token');
    const response = await axios.post<SavedOutfit>(
      `/api/outfit/${generationId}/save`,
      { project_id: projectId, notes },
      { headers: { Authorization: token ? `Bearer ${token}` : '' } }
    );
    return response.data;
  },

  /** Get the authenticated user's saved outfits. */
  getSavedOutfits: async (): Promise<OutfitHistoryItem[]> => {
    const token = localStorage.getItem('token');
    const response = await axios.get<OutfitHistoryItem[]>('/api/outfit/saved', {
      headers: { Authorization: token ? `Bearer ${token}` : '' }
    });
    return response.data;
  },

  /** Remove an outfit from the user's saved list. */
  unsaveOutfit: async (savedId: number): Promise<void> => {
    const token = localStorage.getItem('token');
    await axios.delete(`/api/outfit/saved/${savedId}`, {
      headers: { Authorization: token ? `Bearer ${token}` : '' }
    });
  },

  /** Search products and compare prices across Indian retailers */
  searchProducts: async (payload: {
    items?: any[];
    outfit_item_name?: string;
    category?: string;
    gender?: string;
    style?: string;
    color?: string;
    fabric?: string;
    occasion?: string;
    budget_inr?: number;
    is_budget_friendly?: boolean;
    budget_tier?: string;
    retailer_filter?: string;
    limit?: number;
  }): Promise<PriceComparisonResponse> => {
    const response = await axios.post<PriceComparisonResponse>('/api/outfit-studio/products/search', payload);
    return response.data;
  },

  /** Compare products across stores with query params */
  compareProducts: async (params: {
    outfit_item_name?: string;
    category?: string;
    gender?: string;
    style?: string;
    color?: string;
    fabric?: string;
    occasion?: string;
    budget_inr?: number;
    is_budget_friendly?: boolean;
    budget_tier?: string;
    retailer_filter?: string;
    limit?: number;
  }): Promise<PriceComparisonResponse> => {
    const response = await axios.get<PriceComparisonResponse>('/api/outfit-studio/products/compare', { params });
    return response.data;
  },

  /** Save a verified product to user profile / wishlist */
  saveProduct: async (product: ProductResult, notes?: string): Promise<{ id: number; message: string }> => {
    const token = localStorage.getItem('token');
    const response = await axios.post(
      '/api/outfit-studio/products/save',
      { product, notes },
      { headers: { Authorization: token ? `Bearer ${token}` : '' } }
    );
    return response.data;
  },

  /** Configure a price drop alert for a product */
  createPriceAlert: async (payload: PriceAlertRequest): Promise<PriceAlertResponse> => {
    const token = localStorage.getItem('token');
    const response = await axios.post<PriceAlertResponse>(
      '/api/outfit-studio/price-alerts',
      payload,
      { headers: { Authorization: token ? `Bearer ${token}` : '' } }
    );
    return response.data;
  },

  /** Get price history snapshots for a product */
  getPriceHistory: async (
    productId: string,
    currentPriceInr?: number | null,
    retailer?: string
  ): Promise<PriceHistoryResponse> => {
    const params: Record<string, any> = {};
    if (currentPriceInr) params.current_price_inr = currentPriceInr;
    if (retailer) params.retailer = retailer;
    const response = await axios.get<PriceHistoryResponse>(
      `/api/outfit-studio/products/${productId}/price-history`,
      { params }
    );
    return response.data;
  },

  /** Get verified promotional coupons */
  getCoupons: async (retailer?: string): Promise<RetailerCoupon[]> => {
    const params = retailer ? { retailer } : undefined;
    const response = await axios.get<RetailerCoupon[]>('/api/outfit-studio/coupons', { params });
    return response.data;
  },
};


