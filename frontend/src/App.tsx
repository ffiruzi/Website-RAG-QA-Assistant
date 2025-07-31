import React from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './lib/react-query';
import { ThemeProvider } from './contexts/ThemeContext';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { NotificationProvider } from './contexts/NotificationContext';
import { WebsitesProvider } from './contexts/WebsitesContext';
import { AnalyticsProvider } from './contexts/AnalyticsContext';
import ErrorBoundary from './components/ErrorBoundary';
import Router from './router';
import { ChatWidget } from './components/ChatWidget';

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ThemeProvider>
            <NotificationProvider>
              <AuthProvider>
                <WebsitesProvider>
                  <AnalyticsProvider>
                    <Router />
                    <ChatWidget />
                  </AnalyticsProvider>
                </WebsitesProvider>
              </AuthProvider>
            </NotificationProvider>
          </ThemeProvider>
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  );
};

export default App;