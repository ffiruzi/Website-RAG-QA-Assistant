import React, { useEffect, useState } from 'react';
import Card from '../../components/Card';
import Button from '../../components/Button';
import LineChart from '../../components/charts/LineChart';
import ProgressBar from '../../components/Dashboard/ProgressBar';
import { useAnalytics } from '../../hooks/useAnalytics';
import { RefreshCcw, AlertCircle, Server, Database, Cpu } from 'lucide-react';

const PerformanceMonitor: React.FC = () => {
  const { performanceMetrics, isLoading, fetchPerformanceMetrics } = useAnalytics();
  const [timeRange, setTimeRange] = useState<number>(7);

  useEffect(() => {
    fetchPerformanceMetrics(timeRange);

    // Set up auto-refresh
    const refreshInterval = setInterval(() => {
      fetchPerformanceMetrics(timeRange);
    }, 60000); // Refresh every minute

    return () => clearInterval(refreshInterval);
  }, [timeRange]);

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Performance Monitor</h1>
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
            variant="outline"
            onClick={() => fetchPerformanceMetrics(timeRange)}
            leftIcon={<RefreshCcw className="h-4 w-4" />}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* System Health */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <Card>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <Cpu className="h-6 w-6 text-blue-500 mr-3" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">CPU Usage</h3>
            </div>
            <span className="text-lg font-semibold text-blue-600 dark:text-blue-400">
              {performanceMetrics?.system_health.cpu_usage || 0}%
            </span>
          </div>
          <ProgressBar
            progress={performanceMetrics?.system_health.cpu_usage || 0}
            showPercentage={false}
            color="blue"
            height="h-4"
          />
        </Card>

        <Card>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <Server className="h-6 w-6 text-green-500 mr-3" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Memory Usage</h3>
            </div>
            <span className="text-lg font-semibold text-green-600 dark:text-green-400">
              {performanceMetrics?.system_health.memory_usage || 0}%
            </span>
          </div>
          <ProgressBar
            progress={performanceMetrics?.system_health.memory_usage || 0}
            showPercentage={false}
            color="green"
            height="h-4"
          />
        </Card>

        <Card>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <Database className="h-6 w-6 text-purple-500 mr-3" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Disk Usage</h3>
            </div>
            <span className="text-lg font-semibold text-purple-600 dark:text-purple-400">
              {performanceMetrics?.system_health.disk_usage || 0}%
            </span>
          </div>
          <ProgressBar
            progress={performanceMetrics?.system_health.disk_usage || 0}
            showPercentage={false}
            color="yellow"
            height="h-4"
          />
        </Card>
      </div>

      {/* Response Time Trends */}
      <Card title="Response Time Trends" className="mb-6">
        {isLoading.performance ? (
          <div className="flex items-center justify-center h-64">
            <div className="loader"></div>
          </div>
        ) : performanceMetrics?.response_times.history ? (
          <div>
            <div className="flex items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                Current Average Response Time:
              </h3>
              <span className="ml-2 text-lg font-semibold text-blue-600 dark:text-blue-400">
                {performanceMetrics.response_times.current_avg_ms} ms
              </span>
            </div>
            <LineChart
              data={performanceMetrics.response_times.history}
              xKey="date"
              lines={[
                { key: 'avg_time_ms', name: 'Average Response Time (ms)', color: '#60A5FA' }
              ]}
              height={300}
            />
          </div>
        ) : (
          <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
            No data available
          </div>
        )}
      </Card>

      {/* Embedding Performance */}
      <Card title="Embedding Processing Time" className="mb-6">
        {isLoading.performance ? (
          <div className="flex items-center justify-center h-64">
            <div className="loader"></div>
          </div>
        ) : performanceMetrics?.embedding_times.history ? (
          <div>
            <div className="flex items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                Current Average Embedding Time:
              </h3>
              <span className="ml-2 text-lg font-semibold text-green-600 dark:text-green-400">
                {performanceMetrics.embedding_times.current_avg_s} seconds
              </span>
            </div>
            <LineChart
              data={performanceMetrics.embedding_times.history}
              xKey="date"
              lines={[
                { key: 'avg_time_s', name: 'Average Embedding Time (s)', color: '#4ADE80' }
              ]}
              height={300}
            />
          </div>
        ) : (
          <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
            No data available
          </div>
        )}
      </Card>

      {/* Crawling Performance */}
      <Card title="Crawling Speed">
        {isLoading.performance ? (
          <div className="flex items-center justify-center h-64">
            <div className="loader"></div>
          </div>
        ) : performanceMetrics?.crawling_speeds.history ? (
          <div>
            <div className="flex items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                Current Average Crawling Speed:
              </h3>
              <span className="ml-2 text-lg font-semibold text-yellow-600 dark:text-yellow-400">
                {performanceMetrics.crawling_speeds.current_avg_pages_per_minute} pages/minute
              </span>
            </div>
            <LineChart
              data={performanceMetrics.crawling_speeds.history}
              xKey="date"
              lines={[
                { key: 'pages_per_minute', name: 'Pages Per Minute', color: '#FBBF24' }
              ]}
              height={300}
            />
          </div>
        ) : (
          <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
            No data available
          </div>
        )}
      </Card>
    </div>
  );
};

export default PerformanceMonitor;