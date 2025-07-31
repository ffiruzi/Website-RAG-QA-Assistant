import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface DataPoint {
  [key: string]: any;
}

interface LineChartProps {
  data: DataPoint[];
  xKey: string;
  lines: {
    key: string;
    name: string;
    color: string;
  }[];
  height?: number | string;
  className?: string;
}

const CustomLineChart: React.FC<LineChartProps> = ({
  data,
  xKey,
  lines,
  height = 300,
  className = ''
}) => {
  if (!data || data.length === 0) {
    return (
      <div className={`flex items-center justify-center bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md ${className}`} style={{ height }}>
        <p className="text-gray-500 dark:text-gray-400">No data available</p>
      </div>
    );
  }

  return (
    <div className={className} style={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#d1d5db" />
          <XAxis
            dataKey={xKey}
            stroke="#6b7280"
            style={{
              fontSize: '12px',
              fontFamily: 'sans-serif',
              fill: 'currentColor',
            }}
            tick={{ fill: '#6b7280' }}
          />
          <YAxis
            stroke="#6b7280"
            style={{
              fontSize: '12px',
              fontFamily: 'sans-serif',
              fill: 'currentColor',
            }}
            tick={{ fill: '#6b7280' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #d1d5db',
              borderRadius: '0.375rem',
              fontSize: '0.875rem',
              color: '#1f2937'
            }}
          />
          <Legend />
          {lines.map((line, index) => (
            <Line
              key={index}
              type="monotone"
              dataKey={line.key}
              name={line.name}
              stroke={line.color}
              activeDot={{ r: 8 }}
              strokeWidth={2}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CustomLineChart;