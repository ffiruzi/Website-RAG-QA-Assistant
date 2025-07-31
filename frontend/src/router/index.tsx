import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

// Layouts
import DashboardLayout from '../layouts/DashboardLayout';
import AuthLayout from '../layouts/AuthLayout';

// Pages
import Login from '../pages/auth/Login';
import Register from '../pages/auth/Register';
import Dashboard from '../pages/dashboard/Dashboard';
import Analytics from '../pages/dashboard/Analytics'; // Add this import
import ExportReports from '../pages/dashboard/ExportReports'; // Add this import
import Websites from '../pages/websites/Websites';
import WebsiteDetail from '../pages/websites/WebsiteDetail';
import WebsiteForm from '../pages/websites/WebsiteForm';
import WebsiteAnalytics from '../pages/websites/WebsiteAnalytics'; // Add this import
import CrawlingMonitor from '../pages/monitoring/CrawlingMonitor'; // Add this import
import PerformanceMonitor from '../pages/monitoring/PerformanceMonitor'; // Add this import
import ContentCoverageDetails from '../pages/monitoring/ContentCoverageDetails'; // Add this import
import NotFound from '../pages/NotFound';

const Router: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  // If auth is loading, show a spinner
  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <Routes>
      {/* Auth routes - redirect to dashboard if already authenticated */}
      {!isAuthenticated ? (
        <Route path="/auth" element={<AuthLayout />}>
          <Route path="login" element={<Login />} />
          <Route path="register" element={<Register />} />
          <Route path="" element={<Navigate to="/auth/login" replace />} />
        </Route>
      ) : null}

      {/* Dashboard routes - only accessible when authenticated */}
      <Route
        path="/"
        element={isAuthenticated ? <DashboardLayout /> : <Navigate to="/auth/login" replace />}
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />

        {/* Analytics Routes */}
        <Route path="analytics" element={<Analytics />} />
        <Route path="reports" element={<ExportReports />} />

        {/* Monitoring Routes */}
        <Route path="monitoring/crawling" element={<CrawlingMonitor />} />
        <Route path="monitoring/performance" element={<PerformanceMonitor />} />
        <Route path="monitoring/content/:id" element={<ContentCoverageDetails />} />

        {/* Website Routes */}
        <Route path="websites" element={<Websites />} />
        <Route path="websites/new" element={<WebsiteForm />} />
        <Route path="websites/:id" element={<WebsiteDetail />} />
        <Route path="websites/:id/edit" element={<WebsiteForm />} />
        <Route path="websites/:id/analytics" element={<WebsiteAnalytics />} />
      </Route>

      {/* Redirect root to login or dashboard based on auth state */}
      <Route
        path="/"
        element={<Navigate to={isAuthenticated ? "/dashboard" : "/auth/login"} replace />}
      />

      {/* Catch-all route */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

export default Router;