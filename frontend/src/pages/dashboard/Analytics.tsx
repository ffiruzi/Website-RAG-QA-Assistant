import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/Card';
import Button from '../../components/Button';
import LineChart from '../../components/charts/LineChart';
import PieChart from '../../components/charts/PieChart';
import BarChart from '../../components/charts/BarChart';
import StatsCard from '../../components/Dashboard/StatsCard';
import StatusBadge from '../../components/Dashboard/StatusBadge';
import { useAnalytics } from '../../hooks/useAnalytics';
import { useWebsites } from '../../hooks/useWebsites';
import { Activity, Server, Users, MessageSquare, Clock } from 'lucide-react';
import { formatDate } from '../../utils/formatters';

const Analytics: React.FC = () => {
  const navigate = useNavigate();
  const { websites } = useWebsites();
  const {
    dashboardStats,
    performanceMetrics,
    crawlingStats,
    isLoading,
    fetchDashboardStats,
    fetchPerformanceMetrics,
    fetchCrawlingStats
  } = useAnalytics();

  const [selectedTimeRange, setSelectedTimeRange] = useState<number>(7);

  useEffect(() => {
    fetchDashboardStats();
    fetchPerformanceMetrics(selectedTimeRange);
    fetchCrawlingStats();

    // Set up auto-refresh
    const refreshInterval = setInterval(() => {
      fetchCrawlingStats();
    }, 30000); // Refresh crawling stats every 30 seconds

    return () => clearInterval(refreshInterval);
  }, [selectedTimeRange]);

  // Prepare data for website status pie chart
  const websiteStatusData = websites.length > 0
    ? [
        {
          name: 'Active',
          value: websites.filter(w => w.is_active).length,
          color: '#4ADE80' // green-400
        },
        {
          name: 'Inactive',
          value: websites.filter(w => !w.is_active).length,
          color: '#F87171' // red-400
        }
      ]
    : [];

  // Prepare data for job status pie chart
  const jobStatusData = dashboardStats?.jobs.by_status
    ? [
        {
          name: 'Completed',
          value: dashboardStats.jobs.by_status.completed,
          color: '#4ADE80' // green-400
        },
        {
          name: 'Failed',
          value: dashboardStats.jobs.by_status.failed,
          color: '#F87171' // red-400
        },
        {
          name: 'Pending',
          value: dashboardStats.jobs.by_status.pending,
          color: '#FBBF24' // yellow-400
        },
        {
          name: 'Running',
          value: dashboardStats.jobs.by_status.running,
          color: '#60A5FA' // blue-400
        }
      ]
    : [];

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics Dashboard</h1>
        <div className="flex items-center space-x-2">
          <Button
            variant={selectedTimeRange === 7 ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setSelectedTimeRange(7)}
          >
            7 days
          </Button>
          <Button
            variant={selectedTimeRange === 30 ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setSelectedTimeRange(30)}
          >
            30 days
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              fetchDashboardStats();
              fetchPerformanceMetrics(selectedTimeRange);
              fetchCrawlingStats();
            }}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* System Stats */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-4 mb-6">
        <StatsCard
          title="Total Websites"
          value={dashboardStats?.websites.total || 0}
          description={`${dashboardStats?.websites.active || 0} active`}
          icon={<Server className="h-6 w-6 text-blue-500" />}
        />
        <StatsCard
          title="Total Conversations"
          value={dashboardStats?.conversations.total || 0}
          description={`${dashboardStats?.conversations.last_24h || 0} in last 24h`}
          icon={<MessageSquare className="h-6 w-6 text-green-500" />}
        />
        <StatsCard
          title="Total Messages"
          value={dashboardStats?.messages.total || 0}
          description={`${dashboardStats?.messages.last_24h || 0} in last 24h`}
          icon={<Activity className="h-6 w-6 text-purple-500" />}
        />
        <StatsCard
          title="Active Jobs"
          value={dashboardStats?.jobs.active || 0}
          description={`${dashboardStats?.jobs.success_rate.toFixed(1) || 0}% success rate`}
          icon={<Clock className="h-6 w-6 text-yellow-500" />}
        />
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card title="Response Time Trends">
          {isLoading.performance ? (
            <div className="flex items-center justify-center h-64">
              <div className="loader"></div>
            </div>
          ) : performanceMetrics?.response_times.history ? (
            <LineChart
              data={performanceMetrics.response_times.history}
              xKey="date"
              lines={[
                { key: 'avg_time_ms', name: 'Avg Response Time (ms)', color: '#60A5FA' }
              ]}
              height={300}
            />
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
              No data available
            </div>
          )}
        </Card>

        <Card title="Processing Speed Trends">
          {isLoading.performance ? (
            <div className="flex items-center justify-center h-64">
              <div className="loader"></div>
            </div>
          ) : (performanceMetrics?.crawling_speeds.history && performanceMetrics?.embedding_times.history) ? (
            <LineChart
              data={performanceMetrics.crawling_speeds.history}
              xKey="date"
              lines={[
                { key: 'pages_per_minute', name: 'Pages Per Minute', color: '#4ADE80' }
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

      {/* Status Distribution */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <Card title="Website Status Distribution">
          <PieChart
            data={websiteStatusData}
            height={250}
          />
        </Card>

        <Card title="Job Status Distribution">
          <PieChart
            data={jobStatusData}
            height={250}
          />
        </Card>
      </div>

      {/* Active Jobs */}
      <Card title="Active Crawling Jobs" className="mb-6">
        {isLoading.crawling ? (
          <div className="flex items-center justify-center h-20">
            <div className="loader"></div>
          </div>
        ) : crawlingStats?.active_jobs && crawlingStats.active_jobs.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Website
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Progress
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Started
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-800 dark:divide-gray-700">
                {crawlingStats.active_jobs.map((job) => (
                  <tr key={job.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {job.website_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <StatusBadge status="running" />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                        <div
                          className="bg-blue-600 h-2.5 rounded-full dark:bg-blue-500"
                          style={{ width: `${job.progress}%` }}
                        ></div>
                      </div>
                      <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {job.urls_processed} / {job.urls_total} URLs
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {formatDate(job.start_time)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Button variant="outline" size="sm">
                        View Details
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-4 text-center text-gray-500 dark:text-gray-400">
            No active crawling jobs
          </div>
        )}
      </Card>

      {/* Recent Jobs */}
      <Card title="Recent Jobs">
        {isLoading.crawling ? (
          <div className="flex items-center justify-center h-20">
            <div className="loader"></div>
          </div>
        ) : crawlingStats?.recent_jobs && crawlingStats.recent_jobs.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Website
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Pages
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Started
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Completed
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-800 dark:divide-gray-700">
                {crawlingStats.recent_jobs.map((job) => (
                  <tr key={job.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {job.website_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <StatusBadge status={job.status} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {job.urls_processed} / {job.urls_total}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {formatDate(job.start_time)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {job.end_time ? formatDate(job.end_time) : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-4 text-center text-gray-500 dark:text-gray-400">
            No recent jobs found
          </div>
        )}
      </Card>
    </div>
  );
};

export default Analytics;