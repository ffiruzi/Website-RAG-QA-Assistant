import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import Card from '../../components/Card';
import Button from '../../components/Button';
import { useWebsites } from '../../hooks/useWebsites';
import { useNotification } from '../../hooks/useNotification';
import api from '../../services/api';
import { Activity, PieChart, BarChart2, AlertCircle, RefreshCcw } from 'lucide-react';

// Define interface for website status
interface WebsiteStatus {
  crawling_status: string;
  embedding_status: string;
  document_count: number;
  embedding_count: number;
  last_crawled_at: string | null;
  last_embedded_at: string | null;
}

const WebsiteDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const websiteId = parseInt(id || '0');
  const navigate = useNavigate();
  const { getWebsite } = useWebsites();
  const { addToast } = useNotification();
  const website = getWebsite(websiteId);

  // State for website status
  const [websiteStatus, setWebsiteStatus] = useState<WebsiteStatus>({
    crawling_status: 'Not crawled',
    embedding_status: 'Not generated',
    document_count: 0,
    embedding_count: 0,
    last_crawled_at: null,
    last_embedded_at: null
  });

  // State for loading status
  const [isLoadingStatus, setIsLoadingStatus] = useState<boolean>(true);

  // Function to fetch website status
  const fetchWebsiteStatus = async () => {
    try {
      setIsLoadingStatus(true);
      const response = await api.get(`/websites/${websiteId}/status`);
      setWebsiteStatus(response.data);
    } catch (error) {
      console.error('Error fetching website status:', error);
      addToast({
        type: 'error',
        title: 'Error',
        message: 'Failed to fetch website status'
      });
    } finally {
      setIsLoadingStatus(false);
    }
  };

  // Fetch website status on mount and set up polling
  useEffect(() => {
    if (websiteId) {
      fetchWebsiteStatus();

      // Set up polling interval (every 5 seconds)
      const intervalId = setInterval(() => {
        fetchWebsiteStatus();
      }, 5000);

      // Clean up interval on unmount
      return () => clearInterval(intervalId);
    }
  }, [websiteId]);

  // Function to handle starting a crawling job
  const handleStartCrawling = async () => {
    try {
      addToast({
        type: 'info',
        title: 'Starting Crawling Job',
        message: 'Initiating website crawling...'
      });

      await api.post(`/crawler/crawl/${websiteId}`);

      addToast({
        type: 'success',
        title: 'Success',
        message: 'Crawling job started'
      });

      // Immediately fetch status to show job is running
      fetchWebsiteStatus();

      // Navigate to crawling monitor
      navigate('/monitoring/crawling');
    } catch (error) {
      console.error(error);
      addToast({
        type: 'error',
        title: 'Error',
        message: 'Failed to start crawling'
      });
    }
  };

  // Function to handle generating embeddings
  const handleGenerateEmbeddings = async () => {
    try {
      addToast({
        type: 'info',
        title: 'Generating Embeddings',
        message: 'Processing...'
      });

      await api.post(`/embeddings/${websiteId}/process`);

      addToast({
        type: 'success',
        title: 'Success',
        message: 'Embedding generation started'
      });

      // Immediately fetch status to show job is running
      fetchWebsiteStatus();
    } catch (error) {
      console.error(error);
      addToast({
        type: 'error',
        title: 'Error',
        message: 'Failed to generate embeddings'
      });
    }
  };

  // Function to get status badge class
  const getStatusBadgeClass = (status: string): string => {
    switch (status.toLowerCase()) {
      case 'completed':
      case 'indexed':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      case 'in progress':
      case 'running':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300';
      case 'failed':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300';
      case 'not crawled':
      case 'not generated':
      default:
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300';
    }
  };

  // Format date for display
  const formatDate = (dateString: string | null): string => {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  if (!website) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold">Website Not Found</h2>
          <Button
            variant="primary"
            onClick={() => navigate('/websites')}
            className="mt-4"
          >
            Back to Websites
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center mb-6">
        <Button
          variant="outline"
          onClick={() => navigate('/websites')}
          className="mr-4"
        >
          Back
        </Button>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{website.name}</h1>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 mb-6">
        <Card title="Website Information">
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">URL</h3>
              <div className="mt-1 text-sm text-gray-900 dark:text-white">
                <a
                  href={website.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline dark:text-blue-400"
                >
                  {website.url}
                </a>
              </div>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Status</h3>
              <div className="mt-1 text-sm">
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  website.is_active
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                    : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                }`}>
                  {website.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
            {website.sitemap_url && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Sitemap URL</h3>
                <div className="mt-1 text-sm text-gray-900 dark:text-white">
                  <a
                    href={website.sitemap_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline dark:text-blue-400"
                  >
                    {website.sitemap_url}
                  </a>
                </div>
              </div>
            )}
            {website.description && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Description</h3>
                <div className="mt-1 text-sm text-gray-900 dark:text-white">{website.description}</div>
              </div>
            )}
            <div className="pt-4 flex space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate(`/websites/${websiteId}/edit`)}
              >
                Edit
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  if (window.confirm("Are you sure you want to delete this website?")) {
                    // Delete website
                  }
                }}
              >
                Delete
              </Button>
            </div>
          </div>
        </Card>

        <Card
          title="Content Status"
          actions={
            <Button
              variant="ghost"
              size="sm"
              onClick={fetchWebsiteStatus}
              disabled={isLoadingStatus}
              aria-label="Refresh status"
            >
              <RefreshCcw className="h-4 w-4" />
            </Button>
          }
        >
          {isLoadingStatus ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Crawling Status</h3>
                <div className="mt-1 text-sm">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadgeClass(websiteStatus.crawling_status)}`}>
                    {websiteStatus.crawling_status}
                  </span>
                </div>
                {websiteStatus.last_crawled_at && (
                  <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    Last crawled: {formatDate(websiteStatus.last_crawled_at)}
                  </div>
                )}
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Embedding Status</h3>
                <div className="mt-1 text-sm">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadgeClass(websiteStatus.embedding_status)}`}>
                    {websiteStatus.embedding_status}
                  </span>
                </div>
                {websiteStatus.last_embedded_at && (
                  <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    Last embedded: {formatDate(websiteStatus.last_embedded_at)}
                  </div>
                )}
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Document Count</h3>
                <div className="mt-1 text-sm text-gray-900 dark:text-white">{websiteStatus.document_count}</div>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Embedding Count</h3>
                <div className="mt-1 text-sm text-gray-900 dark:text-white">{websiteStatus.embedding_count}</div>
              </div>
              <div className="pt-4 flex space-x-2">
                <Link to={`/monitoring/content/${websiteId}`}>
                  <Button
                    variant="outline"
                    size="sm"
                    leftIcon={<PieChart className="h-4 w-4" />}
                    disabled={websiteStatus.document_count === 0}
                  >
                    View Content Coverage
                  </Button>
                </Link>
                <Link to={`/websites/${websiteId}/analytics`}>
                  <Button
                    variant="outline"
                    size="sm"
                    leftIcon={<BarChart2 className="h-4 w-4" />}
                  >
                    Analytics
                  </Button>
                </Link>
              </div>
            </div>
          )}
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <Card>
          <div className="text-center p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Crawl Website Content
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              Start a new crawling job to extract content from this website.
            </p>
            <Button
              variant="primary"
              leftIcon={<Activity className="h-4 w-4" />}
              onClick={handleStartCrawling}
              isLoading={websiteStatus.crawling_status === 'Running'}
              disabled={websiteStatus.crawling_status === 'Running'}
            >
              {websiteStatus.crawling_status === 'Running' ? 'Crawling in Progress' : 'Start Crawling'}
            </Button>
          </div>
        </Card>

        <Card>
          <div className="text-center p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Generate Embeddings
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              Process crawled content and generate embeddings for Q&A.
            </p>
            <Button
              variant="primary"
              onClick={handleGenerateEmbeddings}
              isLoading={websiteStatus.embedding_status === 'Running'}
              disabled={
                websiteStatus.embedding_status === 'Running' ||
                (websiteStatus.crawling_status !== 'Completed' && websiteStatus.document_count === 0)
              }
            >
              {websiteStatus.embedding_status === 'Running' ? 'Generation in Progress' : 'Generate Embeddings'}
            </Button>
            {websiteStatus.crawling_status !== 'Completed' && websiteStatus.document_count === 0 && (
              <p className="mt-2 text-xs text-amber-600 dark:text-amber-400">
                You need to crawl the website before generating embeddings
              </p>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default WebsiteDetail;