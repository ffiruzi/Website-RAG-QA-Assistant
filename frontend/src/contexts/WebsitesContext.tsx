import React, { createContext, useState, useContext, ReactNode, useEffect } from 'react';
import api from '../services/api';
import { useNotification } from '../hooks/useNotification';

// Define Website type
export interface Website {
  id: number;
  url: string;
  name: string;
  description: string | null;
  is_active: boolean;
  sitemap_url: string | null;
  created_at: string;
  updated_at: string;
}

// Define the context type
interface WebsitesContextType {
  websites: Website[];
  isLoading: boolean;
  error: string | null;
  fetchWebsites: () => Promise<void>;
  createWebsite: (websiteData: Partial<Website>) => Promise<Website>;
  updateWebsite: (id: number, websiteData: Partial<Website>) => Promise<Website>;
  deleteWebsite: (id: number) => Promise<boolean>;
  getWebsite: (id: number) => Website | undefined;
}

// Create the context with a default value
const WebsitesContext = createContext<WebsitesContextType | undefined>(undefined);

// Provider component
export const WebsitesProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [websites, setWebsites] = useState<Website[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { addToast } = useNotification();

  // Fetch websites on component mount
  useEffect(() => {
    fetchWebsites();
  }, []);

  // Fetch all websites
  const fetchWebsites = async (): Promise<void> => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await api.get('/websites/');

      // Extract websites from response
      const fetchedWebsites = response.data.items || [];

      // If we received websites, use them
      if (Array.isArray(fetchedWebsites)) {
        setWebsites(fetchedWebsites);
      } else {
        console.error('Invalid websites data:', fetchedWebsites);
        setError('Invalid data format received from server');
      }
    } catch (err) {
      console.error('Error fetching websites:', err);
      setError('Failed to fetch websites');
      // Don't show error toast here as it would show on every component mount
    } finally {
      setIsLoading(false);
    }
  };

  // Create a new website
  const createWebsite = async (websiteData: Partial<Website>): Promise<Website> => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await api.post('/websites/', websiteData);
      const newWebsite = response.data;

      // Update the websites state
      setWebsites(prevWebsites => [...prevWebsites, newWebsite]);

      return newWebsite;
    } catch (err) {
      console.error('Error creating website:', err);
      setError('Failed to create website');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Update an existing website
  const updateWebsite = async (id: number, websiteData: Partial<Website>): Promise<Website> => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await api.put(`/websites/${id}`, websiteData);
      const updatedWebsite = response.data;

      // Update the websites state
      setWebsites(prevWebsites =>
        prevWebsites.map(website =>
          website.id === id ? { ...website, ...updatedWebsite } : website
        )
      );

      return updatedWebsite;
    } catch (err) {
      console.error(`Error updating website ${id}:`, err);
      setError('Failed to update website');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Delete a website
  const deleteWebsite = async (id: number): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      await api.delete(`/websites/${id}`);

      // Update the websites state
      setWebsites(prevWebsites =>
        prevWebsites.filter(website => website.id !== id)
      );

      addToast({
        type: 'success',
        title: 'Website Deleted',
        message: 'The website was successfully deleted.'
      });

      return true;
    } catch (err) {
      console.error(`Error deleting website ${id}:`, err);
      setError('Failed to delete website');
      addToast({
        type: 'error',
        title: 'Error',
        message: 'Failed to delete the website.'
      });
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Get a single website by ID
  const getWebsite = (id: number): Website | undefined => {
    return websites.find(website => website.id === id);
  };

  // Context value
  const value = {
    websites,
    isLoading,
    error,
    fetchWebsites,
    createWebsite,
    updateWebsite,
    deleteWebsite,
    getWebsite,
  };

  return <WebsitesContext.Provider value={value}>{children}</WebsitesContext.Provider>;
};

// Custom hook for using the context
export const useWebsites = (): WebsitesContextType => {
  const context = useContext(WebsitesContext);
  if (context === undefined) {
    throw new Error('useWebsites must be used within a WebsitesProvider');
  }
  return context;
};