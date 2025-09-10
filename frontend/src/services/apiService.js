/**
 * API Service for Panda Restaurant Group P&L Analytics
 * Handles all communication with the FastAPI backend
 */

import { appConfig } from '../config/appConfig.js';

class ApiService {
  constructor() {
    this.baseUrl = appConfig.api.baseUrl;
    this.timeout = appConfig.api.timeout;
  }

  /**
   * Generic API request handler with enhanced error logging
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      timeout: this.timeout,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    const requestId = `req_${Date.now()}`;
    console.log(`[${requestId}] API Request: ${options.method || 'GET'} ${url}`);

    try {
      const response = await fetch(url, config);
      
      console.log(`[${requestId}] Response: ${response.status} ${response.statusText}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`[${requestId}] Error response body:`, errorText);
        throw new Error(`HTTP ${response.status}: ${response.statusText}${errorText ? ` - ${errorText}` : ''}`);
      }
      
      const data = await response.json();
      console.log(`[${requestId}] Success: Response received`);
      return data;
    } catch (error) {
      console.error(`[${requestId}] API Error (${endpoint}):`, {
        message: error.message,
        stack: error.stack,
        url,
        options: config
      });
      throw error;
    }
  }

  /**
   * Health check - verify backend connectivity
   */
  async healthCheck() {
    return this.request(appConfig.api.endpoints.health);
  }

  /**
   * Get operational alerts for store managers
   */
  async getOperationalAlerts() {
    return this.request(appConfig.api.endpoints.alerts);
  }

  /**
   * Get key performance indicators
   */
  async getKPIs() {
    return this.request(appConfig.api.endpoints.kpis);
  }

  /**
   * Get monthly P&L summary data
   */
  async getMonthlyData() {
    return this.request(appConfig.api.endpoints.monthlyData);
  }

  /**
   * Get store performance summary
   */
  async getStoreData() {
    return this.request(appConfig.api.endpoints.storeData);
  }

  /**
   * Get top performing stores
   */
  async getTopStores(limit = 10) {
    return this.request(`${appConfig.api.endpoints.topStores}?limit=${limit}`);
  }

  /**
   * Ask Genie AI a natural language question
   */
  async askGenie(question, context = null) {
    return this.request(appConfig.api.endpoints.genie, {
      method: 'POST',
      body: JSON.stringify({ question, context })
    });
  }

  /**
   * Execute a direct SQL query
   */
  async executeSQLQuery(query, params = null) {
    return this.request(appConfig.api.endpoints.sqlQuery, {
      method: 'POST',
      body: JSON.stringify({ query, params })
    });
  }

  /**
   * Upload data file
   */
  async uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    return this.request(appConfig.api.endpoints.upload, {
      method: 'POST',
      body: formData,
      headers: {} // Let browser set Content-Type for FormData
    });
  }

  /**
   * Test connection with retry logic
   */
  async testConnection(maxRetries = 3) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        const health = await this.healthCheck();
        return { success: true, health, attempt };
      } catch (error) {
        console.warn(`Connection attempt ${attempt} failed:`, error.message);
        
        if (attempt === maxRetries) {
          return { 
            success: false, 
            error: error.message, 
            attempts: maxRetries 
          };
        }
        
        // Wait before retry (exponential backoff)
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
      }
    }
  }
}

// Create singleton instance
export const apiService = new ApiService();

// Export individual methods for convenience
export const {
  healthCheck,
  getOperationalAlerts,
  getKPIs,
  getMonthlyData,
  getStoreData,
  getTopStores,
  askGenie,
  executeSQLQuery,
  uploadFile,
  testConnection
} = apiService;

// Export default
export default apiService;
