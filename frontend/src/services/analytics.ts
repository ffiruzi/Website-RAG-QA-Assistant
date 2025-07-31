import api from './api';

// Types for analytics data
export interface DashboardStats {
  websites: {
    total: number;
    active: number;
  };
  conversations: {
    total: number;
    last_24h: number;
  };
  messages: {
    total: number;
    last_24h: number;
  };
  jobs: {
    active: number;
    by_status: {
      completed: number;
      failed: number;
      pending: number;
      running: number;
    };
    success_rate: number;
    recent: any[];
  };
}

export interface WebsiteAnalytics {
  website: {
    id: number;
    name: string;
    url: string;
  };
  conversations: {
    total: number;
    daily: Array<{
      date: string;
      conversations: number;
      messages: number;
    }>;
  };
  messages: {
    total: number;
    user: number;
    system: number;
  };
}

export interface CrawlingStats {
  active_jobs: Array<{
    id: string;
    website_id: number;
    website_name: string;
    status: string;
    progress: number;
    urls_processed: number;
    urls_total: number;
    start_time: string;
  }>;
  recent_jobs: Array<{
    id: string;
    website_id: number;
    website_name: string;
    status: string;
    urls_processed: number;
    urls_total: number;
    start_time: string;
    end_time: string;
    error?: string;
  }>;
  stats: {
    success_rate: number;
    average_duration_minutes: number;
    average_pages_per_minute: number;
  };
}

export interface ContentCoverage {
  pages: {
    total: number;
    crawled: number;
    indexed: number;
    coverage_percentage: number;
  };
  by_content_type: Array<{
    type: string;
    count: number;
    percentage: number;
  }>;
  by_section: Array<{
    section: string;
    pages: number;
    coverage: number;
  }>;
}

export interface PerformanceMetrics {
  response_times: {
    current_avg_ms: number;
    history: Array<{
      date: string;
      avg_time_ms: number;
    }>;
  };
  embedding_times: {
    current_avg_s: number;
    history: Array<{
      date: string;
      avg_time_s: number;
    }>;
  };
  crawling_speeds: {
    current_avg_pages_per_minute: number;
    history: Array<{
      date: string;
      pages_per_minute: number;
    }>;
  };
  system_health: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    status: string;
  };
}

export interface TopQuery {
  query: string;
  count: number;
  avg_rating: number;
}

// Analytics API service
const analyticsService = {
  getDashboardStats: async (): Promise<DashboardStats> => {
    try {
      const response = await api.get('/analytics/dashboard');
      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      throw error;
    }
  },

  getWebsiteAnalytics: async (websiteId: number, days: number = 30): Promise<WebsiteAnalytics> => {
    try {
      const response = await api.get(`/analytics/websites/${websiteId}?days=${days}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching analytics for website ${websiteId}:`, error);
      throw error;
    }
  },

  getCrawlingStats: async (): Promise<CrawlingStats> => {
    try {
      const response = await api.get('/analytics/crawling');
      return response.data;
    } catch (error) {
      console.error('Error fetching crawling stats:', error);
      throw error;
    }
  },

  getContentCoverage: async (websiteId: number): Promise<ContentCoverage> => {
    try {
      const response = await api.get(`/analytics/content-coverage/${websiteId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching content coverage for website ${websiteId}:`, error);
      throw error;
    }
  },

  getPerformanceMetrics: async (days: number = 7): Promise<PerformanceMetrics> => {
    try {
      const response = await api.get(`/analytics/performance?days=${days}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching performance metrics:', error);
      throw error;
    }
  },

  getTopQueries: async (websiteId: number, limit: number = 10): Promise<TopQuery[]> => {
    try {
      const response = await api.get(`/analytics/top-queries/${websiteId}?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching top queries for website ${websiteId}:`, error);
      throw error;
    }
  }
};

export default analyticsService;