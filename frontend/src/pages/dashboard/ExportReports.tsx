import React, { useState } from 'react';
import Card from '../../components/Card';
import Button from '../../components/Button';
import { useWebsites } from '../../hooks/useWebsites';
import { useAnalytics } from '../../hooks/useAnalytics';
import { useNotification } from '../../hooks/useNotification';
import { FileDown, Calendar, FileText, BarChart2 } from 'lucide-react';

type ReportType = 'usage' | 'performance' | 'content_coverage' | 'queries';
type ReportFormat = 'csv' | 'pdf' | 'json';
type TimePeriod = '7d' | '30d' | '90d' | 'all';

const ExportReports: React.FC = () => {
  const { websites } = useWebsites();
  const { addToast } = useNotification();

  const [selectedWebsite, setSelectedWebsite] = useState<number | 'all'>('all');
  const [reportType, setReportType] = useState<ReportType>('usage');
  const [reportFormat, setReportFormat] = useState<ReportFormat>('csv');
  const [timePeriod, setTimePeriod] = useState<TimePeriod>('30d');
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerateReport = () => {
    setIsGenerating(true);

    // In a real implementation, this would call an API to generate the report
    setTimeout(() => {
      setIsGenerating(false);

      // Show success notification
      addToast({
        type: 'success',
        title: 'Report Generated',
        message: 'Your report has been successfully generated and is ready for download.'
      });
    }, 2000);
  };

  const getReportTypeLabel = (type: ReportType): string => {
    switch (type) {
      case 'usage':
        return 'Usage Analytics';
      case 'performance':
        return 'System Performance';
      case 'content_coverage':
        return 'Content Coverage';
      case 'queries':
        return 'Query Analysis';
      default:
        return type;
    }
  };

  const getTimePeriodLabel = (period: TimePeriod): string => {
    switch (period) {
      case '7d':
        return 'Last 7 days';
      case '30d':
        return 'Last 30 days';
      case '90d':
        return 'Last 90 days';
      case 'all':
        return 'All time';
      default:
        return period;
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Export Reports</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Report Configuration</h2>

          <div className="space-y-6">
            {/* Website Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Website
              </label>
              <select
                value={selectedWebsite.toString()}
                onChange={(e) => setSelectedWebsite(e.target.value === 'all' ? 'all' : parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="all">All Websites</option>
                {websites.map((website) => (
                  <option key={website.id} value={website.id}>
                    {website.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Report Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Report Type
              </label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {(['usage', 'performance', 'content_coverage', 'queries'] as ReportType[]).map((type) => (
                  <button
                    key={type}
                    onClick={() => setReportType(type)}
                    className={`flex flex-col items-center p-4 border rounded-lg transition-colors
                      ${reportType === type
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                        : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800'
                      }`}
                  >
                    {type === 'usage' && <BarChart2 className="h-6 w-6 mb-2" />}
                    {type === 'performance' && <Calendar className="h-6 w-6 mb-2" />}
                    {type === 'content_coverage' && <FileText className="h-6 w-6 mb-2" />}
                    {type === 'queries' && <BarChart2 className="h-6 w-6 mb-2" />}
                    <span className="text-sm">{getReportTypeLabel(type)}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Time Period */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Time Period
              </label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {(['7d', '30d', '90d', 'all'] as TimePeriod[]).map((period) => (
                  <button
                    key={period}
                    onClick={() => setTimePeriod(period)}
                    className={`py-2 px-4 border rounded-lg transition-colors
                      ${timePeriod === period
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                        : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800'
                      }`}
                  >
                    {getTimePeriodLabel(period)}
                  </button>
                ))}
              </div>
            </div>

            {/* Report Format */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Report Format
              </label>
              <div className="grid grid-cols-3 gap-4">
                {(['csv', 'pdf', 'json'] as ReportFormat[]).map((format) => (
                  <button
                    key={format}
                    onClick={() => setReportFormat(format)}
                    className={`py-2 px-4 border rounded-lg uppercase font-semibold text-sm transition-colors
                      ${reportFormat === format
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                        : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800'
                      }`}
                  >
                    {format}
                  </button>
                ))}
              </div>
            </div>

            {/* Generate Button */}
            <div className="pt-4">
              <Button
                variant="primary"
                onClick={handleGenerateReport}
                isLoading={isGenerating}
                leftIcon={<FileDown className="h-5 w-5" />}
                className="w-full md:w-auto"
              >
                Generate Report
              </Button>
            </div>
          </div>
        </Card>

        <Card>
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Recent Reports</h2>

          <div className="space-y-4">
            <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-gray-900 dark:text-white">Usage Analytics</h3>
                <span className="text-xs text-gray-500 dark:text-gray-400">2 hrs ago</span>
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                All Websites • Last 30 days
              </p>
              <Button variant="outline" size="sm" leftIcon={<FileDown className="h-4 w-4" />}>
                Download CSV
              </Button>
            </div>

            <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-gray-900 dark:text-white">Performance Report</h3>
                <span className="text-xs text-gray-500 dark:text-gray-400">Yesterday</span>
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                System • Last 7 days
              </p>
              <Button variant="outline" size="sm" leftIcon={<FileDown className="h-4 w-4" />}>
                Download PDF
              </Button>
            </div>

            <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-gray-900 dark:text-white">Content Coverage</h3>
                <span className="text-xs text-gray-500 dark:text-gray-400">3 days ago</span>
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                Example Website • All time
              </p>
              <Button variant="outline" size="sm" leftIcon={<FileDown className="h-4 w-4" />}>
                Download JSON
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default ExportReports;