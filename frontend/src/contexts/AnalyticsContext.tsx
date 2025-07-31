import React, { createContext, useState, useContext, ReactNode, useEffect } from 'react';
import analyticsService, {
  DashboardStats,
  WebsiteAnalytics,
  CrawlingStats,
  ContentCoverage,
  PerformanceMetrics,
  TopQuery
} from '../services/analytics';
import { useNotification } from './NotificationContext';

// Define the context type
interface AnalyticsContextType {
  dashboardStats: DashboardStats | null;
  websiteAnalytics: Record<number, WebsiteAnalytics>;
  crawlingStats: CrawlingStats | null;
  contentCoverage: Record<number, ContentCoverage>;
  performanceMetrics: PerformanceMetrics | null;
  topQueries: Record<number, TopQuery[]>;
  isLoading: {
    dashboard: boolean;
    website: Record<number, boolean>;
    crawling: boolean;
    content: Record<number, boolean>;
    performance: boolean;
    queries: Record<number, boolean>;
  };
  error: {
    dashboard: string | null;
    website: Record<number, string | null>;
    crawling: string | null;
    content: Record<number, string | null>;
    performance: string | null;
    queries: Record<number, string | null>;
  };
  fetchDashboardStats: () => Promise<void>;
  fetchWebsiteAnalytics: (websiteId: number, days?: number) => Promise<void>;
  fetchCrawlingStats: () => Promise<void>;
  fetchContentCoverage: (websiteId: number) => Promise<void>;
  fetchPerformanceMetrics: (days?: number) => Promise<void>;
  fetchTopQueries: (websiteId: number, limit?: number) => Promise<void>;
}

// Create the context with a default value
const AnalyticsContext = createContext<AnalyticsContextType | undefined>(undefined);

// Provider component
export const AnalyticsProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { addToast } = useNotification();

  // State for analytics data
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const [websiteAnalytics, setWebsiteAnalytics] = useState<Record<number, WebsiteAnalytics>>({});
  const [crawlingStats, setCrawlingStats] = useState<CrawlingStats | null>(null);
  const [contentCoverage, setContentCoverage] = useState<Record<number, ContentCoverage>>({});
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetrics | null>(null);
  const [topQueries, setTopQueries] = useState<Record<number, TopQuery[]>>({});

  // State for loading status
  const [isLoading, setIsLoading] = useState({
    dashboard: false,
    website: {} as Record<number, boolean>,
    crawling: false,
    content: {} as Record<number, boolean>,
    performance: false,
    queries: {} as Record<number, boolean>
  });

  // State for error messages
  const [error, setError] = useState({
    dashboard: null as string | null,
    website: {} as Record<number, string | null>,
    crawling: null as string | null,
    content: {} as Record<number, string | null>,
    performance: null as string | null,
    queries: {} as Record<number, string | null>
  });

  // Fetch dashboard stats
  const fetchDashboardStats = async (): Promise<void> => {
    try {
      setIsLoading(prev => ({ ...prev, dashboard: true }));
      setError(prev => ({ ...prev, dashboard: null }));

      const data = await analyticsService.getDashboardStats();
      setDashboardStats(data);
    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
      setError(prev => ({ ...prev, dashboard: 'Failed to fetch dashboard statistics' }));
      addToast({
        type: 'error',
        title: 'Error',
        message: 'Failed to fetch dashboard statistics'
      });
    } finally {
      setIsLoading(prev => ({ ...prev, dashboard: false }));
    }
  };

  // Fetch website analytics
  const fetchWebsiteAnalytics = async (websiteId: number, days: number = 30): Promise<void> => {
    try {
      setIsLoading(prev => ({ ...prev, website: { ...prev.website, [websiteId]: true } }));
      setError(prev => ({ ...prev, website: { ...prev.website, [websiteId]: null } }));

      const data = await analyticsService.getWebsiteAnalytics(websiteId, days);
      setWebsiteAnalytics(prev => ({ ...prev, [websiteId]: data }));
    } catch (err) {
      console.error(`Error fetching analytics for website ${websiteId}:`, err);
      setError(prev => ({
        ...prev,
        website: {
          ...prev.website,
          [websiteId]: `Failed to fetch analytics for website ${websiteId}`
        }
      }));
      addToast({
        type: 'error',
        title: 'Error',
        message: `Failed to fetch analytics for website ${websiteId}`
      });
    } finally {
      setIsLoading(prev => ({ ...prev, website: { ...prev.website, [websiteId]: false } }));
    }
  };

  // Fetch crawling stats
  const fetchCrawlingStats = async (): Promise<void> => {
    try {
      setIsLoading(prev => ({ ...prev, crawling: true }));
      setError(prev => ({ ...prev, crawling: null }));

      const data = await analyticsService.getCrawlingStats();
      setCrawlingStats(data);
    } catch (err) {
      console.error('Error fetching crawling stats:', err);
      setError(prev => ({ ...prev, crawling: 'Failed to fetch crawling statistics' }));
      addToast({
        type: 'error',
        title: 'Error',
        message: 'Failed to fetch crawling statistics'
      });
    } finally {
      setIsLoading(prev => ({ ...prev, crawling: false }));
    }
  };

  // Fetch content coverage
  const fetchContentCoverage = async (websiteId: number): Promise<void> => {
    try {
      setIsLoading(prev => ({ ...prev, content: { ...prev.content, [websiteId]: true } }));
      setError(prev => ({ ...prev, content: { ...prev.content, [websiteId]: null } }));

      const data = await analyticsService.getContentCoverage(websiteId);
      setContentCoverage(prev => ({ ...prev, [websiteId]: data }));
    } catch (err) {
      console.error(`Error fetching content coverage for website ${websiteId}:`, err);
      setError(prev => ({
        ...prev,
        content: {
          ...prev.content,
          [websiteId]: `Failed to fetch content coverage for website ${websiteId}`
        }
      }));
      addToast({
        type: 'error',
        title: 'Error',
        message: `Failed to fetch content coverage for website ${websiteId}`
      });
    } finally {
      setIsLoading(prev => ({ ...prev, content: { ...prev.content, [websiteId]: false } }));
    }
  };

  // Fetch performance metrics
  const fetchPerformanceMetrics = async (days: number = 7): Promise<void> => {
    try {
      setIsLoading(prev => ({ ...prev, performance: true }));
      setError(prev => ({ ...prev, performance: null }));

      const data = await analyticsService.getPerformanceMetrics(days);
      setPerformanceMetrics(data);
    } catch (err) {
      console.error('Error fetching performance metrics:', err);
      setError(prev => ({ ...prev, performance: 'Failed to fetch performance metrics' }));
      addToast({
        type: 'error',
        title: 'Error',
        message: 'Failed to fetch performance metrics'
      });
    } finally {
      setIsLoading(prev => ({ ...prev, performance: false }));
    }
  };

  // Fetch top queries
  const fetchTopQueries = async (websiteId: number, limit: number = 10): Promise<void> => {
    try {
      setIsLoading(prev => ({ ...prev, queries: { ...prev.queries, [websiteId]: true } }));
      setError(prev => ({ ...prev, queries: { ...prev.queries, [websiteId]: null } }));

      const data = await analyticsService.getTopQueries(websiteId, limit);
      setTopQueries(prev => ({ ...prev, [websiteId]: data }));
    } catch (err) {
      console.error(`Error fetching top queries for website ${websiteId}:`, err);
      setError(prev => ({
        ...prev,
        queries: {
          ...prev.queries,
          [websiteId]: `Failed to fetch top queries for website ${websiteId}`
        }
      }));
      addToast({
        type: 'error',
        title: 'Error',
        message: `Failed to fetch top queries for website ${websiteId}`
      });
    } finally {
      setIsLoading(prev => ({ ...prev, queries: { ...prev.queries, [websiteId]: false } }));
    }
  };

  // Context value
  const value = {
    dashboardStats,
    websiteAnalytics,
    crawlingStats,
    contentCoverage,
    performanceMetrics,
    topQueries,
    isLoading,
    error,
    fetchDashboardStats,
    fetchWebsiteAnalytics,
    fetchCrawlingStats,
    fetchContentCoverage,
    fetchPerformanceMetrics,
    fetchTopQueries
  };

  return <AnalyticsContext.Provider value={value}>{children}</AnalyticsContext.Provider>;
};

// Custom hook for using the context
export const useAnalytics = (): AnalyticsContextType => {
  const context = useContext(AnalyticsContext);
  if (context === undefined) {
    throw new Error('useAnalytics must be used within an AnalyticsProvider');
  }
  return context;
};