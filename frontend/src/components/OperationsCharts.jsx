import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Clock, DollarSign, ChefHat } from 'lucide-react';

const OperationsCharts = ({ config }) => {
  const [chartData, setChartData] = useState({
    hourlyPerformance: [],
    itemVelocity: [],
    costBreakdown: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading restaurant operations data
    setTimeout(() => {
      setChartData({
        hourlyPerformance: [
          { hour: '10 AM', sales: 180, labor: 85, efficiency: 2.1 },
          { hour: '11 AM', sales: 420, labor: 95, efficiency: 4.4 },
          { hour: '12 PM', sales: 680, labor: 110, efficiency: 6.2 },
          { hour: '1 PM', sales: 750, labor: 120, efficiency: 6.3 },
          { hour: '2 PM', sales: 520, labor: 115, efficiency: 4.5 },
          { hour: '3 PM', sales: 290, labor: 100, efficiency: 2.9 },
          { hour: '4 PM', sales: 340, labor: 85, efficiency: 4.0 },
          { hour: '5 PM', sales: 580, labor: 100, efficiency: 5.8 },
          { hour: '6 PM', sales: 720, labor: 125, efficiency: 5.8 }
        ],
        itemVelocity: [
          { item: 'Orange Chicken', sold: 45, margin: 65 },
          { item: 'Chow Mein', sold: 38, margin: 58 },
          { item: 'Fried Rice', sold: 32, margin: 62 },
          { item: 'Beijing Beef', sold: 18, margin: 68 },
          { item: 'Mushroom Chicken', sold: 12, margin: 72 },
          { item: 'Honey Walnut Shrimp', sold: 8, margin: 75 }
        ],
        costBreakdown: [
          { name: 'Food Cost', value: 28.5, color: '#059669' },
          { name: 'Labor Cost', value: 34.2, color: '#d97706' },
          { name: 'Operating Cost', value: 15.3, color: '#6b7280' },
          { name: 'Profit Margin', value: 22.0, color: '#d12a2f' }
        ]
      });
      setLoading(false);
    }, 1000);
  }, []);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="chart-tooltip">
          <p className="tooltip-label">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }}>
              {`${entry.dataKey}: ${entry.value}${entry.dataKey === 'efficiency' ? 'x' : entry.dataKey.includes('sales') ? '$' : '$'}`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="operations-charts">
        <div className="section-header">
          <h3>Operations Performance</h3>
        </div>
        <div className="charts-grid">
          <div className="chart-container skeleton">
            <div className="skeleton-line"></div>
            <div className="skeleton-line short"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="operations-charts">
      <div className="section-header">
        <h3>Operations Performance</h3>
        <div className="section-header-meta">
          <span className="timestamp">
            <Clock size={16} />
            Real-time
          </span>
          <button className="refresh-btn">
            <TrendingUp size={16} />
            Refresh
          </button>
        </div>
      </div>

      <div className="charts-grid">
        {/* Hourly Sales vs Labor */}
        <div className="chart-container">
          <div className="chart-header">
            <div className="chart-title">
              <DollarSign size={20} />
              Hourly Sales vs Labor Efficiency
            </div>
          </div>
          <div className="chart-content">
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={chartData.hourlyPerformance}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="hour" stroke="#6b7280" fontSize={12} />
                <YAxis stroke="#6b7280" fontSize={12} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="sales" fill="#d12a2f" name="Sales ($)" />
                <Bar dataKey="labor" fill="#059669" name="Labor Cost ($)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Item Velocity & Margin */}
        <div className="chart-container">
          <div className="chart-header">
            <div className="chart-title">
              <ChefHat size={20} />
              Menu Item Performance
            </div>
          </div>
          <div className="chart-content">
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={chartData.itemVelocity} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis type="number" stroke="#6b7280" fontSize={12} />
                <YAxis dataKey="item" type="category" stroke="#6b7280" fontSize={11} width={100} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="sold" fill="#2563eb" name="Units Sold" />
                <Bar dataKey="margin" fill="#d12a2f" name="Margin %" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Cost Breakdown Pie Chart */}
        <div className="chart-container">
          <div className="chart-header">
            <div className="chart-title">
              <TrendingUp size={20} />
              Cost Breakdown
            </div>
          </div>
          <div className="chart-content">
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={chartData.costBreakdown}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}%`}
                  labelLine={false}
                  fontSize={11}
                >
                  {chartData.costBreakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `${value}%`} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Chart Insights */}
      <div className="chart-insights">
        <div className="insight-item">
          <span className="insight-label">Peak Hour</span>
          <span className="insight-value">1:00 PM</span>
        </div>
        <div className="insight-item">
          <span className="insight-label">Top Item</span>
          <span className="insight-value">Orange Chicken</span>
        </div>
        <div className="insight-item">
          <span className="insight-label">Best Margin</span>
          <span className="insight-value">Honey Walnut Shrimp</span>
        </div>
        <div className="insight-item">
          <span className="insight-label">Efficiency</span>
          <span className="insight-value">6.3x at lunch</span>
        </div>
      </div>
    </div>
  );
};

export default OperationsCharts;
