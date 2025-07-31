import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Card from '../../components/Card';
import Button from '../../components/Button';
import LineChart from '../../components/charts/LineChart';
import PieChart from '../../components/charts/PieChart';
import BarChart from '../../components/charts/BarChart';
import StatsCard from '../../components/Dashboard/StatsCard';
import { useAnalytics } from '../../hooks/useAnalytics';
import { useWebsites } from '../../hooks/useWebsites';
import { MessageSquare, Link as LinkIcon, AlertCircle, Check, ThumbsUp } from 'lucide-react';

const WebsiteAnalytics: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const websiteId = parseInt(id || '0');
  const navigate = useNavigate();
  const { getWebsite } = useWebsites();
  const website = getWebsite(websiteId);

  const {
    websiteAnalytics,
    contentCoverage,
    topQueries,
    isLoading,
    fetchWebsiteAnalytics,
    fetchContentCoverage,
    fetchTopQueries
  } = useAnalytics();

  const [timeRange, setTimeRange] = useState<number>(30);

  useEffect(() => {
    if (websiteId) {
      fetchWebsiteAnalytics(websiteId, timeRange);
      fetchContentCoverage(websiteId);
      fetchTopQueries(websiteId, 10);
    }
  }, [websiteId, timeRange]);

  // Get the data for this website
  const analytics = websiteAnalytics[websiteId];
  const coverage = contentCoverage[websiteId];
  const queries = topQueries[websiteId] || [];

  // Prepare data for message distribution pie chart
  const messageDistributionData = analytics ? [
    {
      name: 'User Messages',
      value: analytics.messages.user,
      color: '#60A5FA' // blue-400
    },
    {
      name: 'System Messages',
      value: analytics.messages.system,
      color: '#4ADE80' // green-400
    }
  ] : [];

  // Prepare data for content type distribution
  const contentTypeData = coverage?.by_content_type.map(item => ({
    name: item.type.charAt(0).toUpperCase() + item.type.slice(1),
    value: item.count,
    color: item.type === 'blog' ? '#60A5FA' :
           item.type === 'documentation' ? '#4ADE80' :
           item.type === 'product' ? '#F59E0B' : '#8B5CF6'
  })) || [];

  return (
    <div>
      <div className="flex items-center mb-6">
        <Button
          variant="outline"
          onClick={() => navigate(`/websites/${websiteId}`)}
          className="mr-4"
        >
          Back
        </Button>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Analytics for {website?.name || 'Website'}
        </h1>
      </div>

      {/* Time range selector */}
      <div className="flex justify-end mb-6">
        <div className="flex items-center space-x-2">
          <Button
            variant={timeRange === 7 ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setTimeRange(7)}
          >
            7 days
          </Button>
          <Button
            variant={timeRange === 30 ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setTimeRange(30)}
          >
            30 days
          </Button>
          <Button
            variant={timeRange === 90 ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setTimeRange(90)}
          >
            90 days
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              fetchWebsiteAnalytics(websiteId, timeRange);
              fetchContentCoverage(websiteId);
              fetchTopQueries(websiteId, 10);
            }}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-6">
        <StatsCard
          title="Total Conversations"
          value={analytics?.conversations.total || 0}
          icon={<MessageSquare className="h-6 w-6 text-blue-500" />}
        />
        <StatsCard
          title="Total Messages"
          value={analytics?.messages.total || 0}
          icon={<MessageSquare className="h-6 w-6 text-green-500" />}
        />
        <StatsCard
          title="Content Coverage"
          value={`${coverage?.pages.coverage_percentage || 0}%`}
          description={`${coverage?.pages.crawled || 0} of ${coverage?.pages.total || 0} pages`}
          icon={<Check className="h-6 w-6 text-purple-500" />}
        />
        <StatsCard
          title="Indexed Content"
          value={coverage?.pages.indexed || 0}
          description="Pages indexed for Q&A"
          icon={<LinkIcon className="h-6 w-6 text-orange-500" />}
        />
      </div>

      {/* Activity Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card title="Conversation Activity">
          {isLoading.website[websiteId] ? (
            <div className="flex items-center justify-center h-64">
              <div className="loader"></div>
            </div>
          ) : analytics?.conversations.daily ? (
            <LineChart
              data={analytics.conversations.daily}
              xKey="date"
              lines={[
                { key: 'conversations', name: 'Conversations', color: '#60A5FA' },
                { key: 'messages', name: 'Messages', color: '#4ADE80' }
              ]}
              height={300}
            />
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
              No data available
            </div>
          )}
        </Card>

        <Card title="Message Distribution">
          <PieChart
            data={messageDistributionData}
            height={300}
          />
        </Card>
      </div>

      {/* Content Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card title="Content Type Distribution">
          <PieChart
            data={contentTypeData}
            height={300}
          />
        </Card>

        <Card title="Coverage by Section">
          {isLoading.content[websiteId] ? (
            <div className="flex items-center justify-center h-64">
              <div className="loader"></div>
            </div>
          ) : coverage?.by_section ? (
            <BarChart
              data={coverage.by_section}
              xKey="section"
              bars={[
                { key: 'coverage', name: 'Coverage %', color: '#60A5FA' }
              ]}
              height={300}
            />
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
              No data available
            </div>
          )}
        </Card>
      </div>

      {/* Top Queries */}
      <Card title="Top Queries">
        {isLoading.queries[websiteId] ? (
          <div className="flex items-center justify-center h-20">
            <div className="loader"></div>
          </div>
        ) : queries.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Query
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Count
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Avg. Rating
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-800 dark:divide-gray-700">
                {queries.map((query, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4">
                      {query.query}
                    </td>
                    <td className="px-6 py-4 text-center">
                      {query.count}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex items-center justify-center">
                        <ThumbsUp className="h-4 w-4 text-green-500 mr-1" />
                        {query.avg_rating.toFixed(1)}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-4 text-center text-gray-500 dark:text-gray-400">
            No query data available
          </div>
        )}
      </Card>
    </div>
  );
};

export default WebsiteAnalytics;