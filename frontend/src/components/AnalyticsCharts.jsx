import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Clock, DollarSign, Store } from 'lucide-react';
import { apiService } from '../services/apiService.js';

const AnalyticsCharts = ({ config }) => {
  const [chartData, setChartData] = useState({
    monthlyTrends: [],
    storeComparison: [],
    performanceMetrics: [],
    insights: {
      revenueGrowth: '+14% YTD',
      bestMonth: 'June 2024',
      topPerformer: 'Loading...',
      ourRank: '#1 of 5',
      metricsOnTarget: '3 of 3',
      overallScore: 'Excellent'
    }
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadRealData = async () => {
      try {
        console.log('AnalyticsCharts: Loading real data from API...');
        
        // Load real data from API endpoints
        const [monthlyResponse, storeResponse, topStoresResponse] = await Promise.all([
          apiService.getMonthlyData(),
          apiService.getStoreData(), 
          apiService.getTopStores(10)
        ]);

        console.log('AnalyticsCharts: API responses received', {
          monthly: monthlyResponse,
          stores: storeResponse,
          topStores: topStoresResponse
        });

        // Transform monthly data for charts
        let monthlyTrends = [];
        if (monthlyResponse.status === 'success' && monthlyResponse.data.rows.length > 0) {
          // Calculate revenue as percentage of target for better scaling
          const revenueTarget = 350; // Target revenue in K per month
          monthlyTrends = monthlyResponse.data.rows.map(row => {
            const revenueK = (row.total_revenue_sum || 0) / 1000;
            return {
              month: row.month_year || 'Unknown',
              revenue: (revenueK / revenueTarget) * 100, // Convert to percentage of target
              revenue_actual: revenueK, // Keep actual for tooltip
              ebitda_margin: row.ebitda_margin_pct || 0,
              labor_pct: row.labor_pct_of_sales || 0,
              gross_margin: row.gross_margin_pct || 0
            };
          });
        }

        // Transform store data for comparison
        let storeComparison = [];
        if (topStoresResponse.status === 'success' && topStoresResponse.data.rows.length > 0) {
          storeComparison = topStoresResponse.data.rows.slice(0, 5).map(row => ({
            store_name: row.store_name || 'Unknown Store',
            revenue: (row.total_revenue || 0) / 1000, // Convert to K
            labor_pct: row.labor_pct_of_sales || 0,
            ebitda_margin: row.ebitda_margin_pct || 0,
            sales_per_sq_ft: row.sales_per_sq_ft || 0
          }));
        }

        // Calculate performance metrics from real data
        let performanceMetrics = [];
        if (storeComparison.length > 0) {
          const avgLabor = Math.abs(storeComparison.reduce((sum, store) => sum + Math.abs(store.labor_pct), 0) / storeComparison.length);
          const avgEbitda = storeComparison.reduce((sum, store) => sum + store.ebitda_margin, 0) / storeComparison.length;
          const avgRevenue = storeComparison.reduce((sum, store) => sum + store.revenue, 0) / storeComparison.length;
          
          performanceMetrics = [
            { name: 'Avg Labor Cost %', value: avgLabor, target: 30.0, color: '#059669', type: 'percentage' },
            { name: 'Avg EBITDA Margin %', value: avgEbitda, target: 20.0, color: '#d12a2f', type: 'percentage' },
            { name: 'Avg Revenue (K)', value: avgRevenue, target: 900, color: '#2563eb', type: 'currency' }
          ];
        }

        // If no real data, fall back to demo data
        if (monthlyTrends.length === 0) {
          console.log('AnalyticsCharts: No monthly data, using fallback');
          const revenueTarget = 350;
          monthlyTrends = [
            { month: 'Jan 2024', revenue: (285/revenueTarget)*100, revenue_actual: 285, ebitda_margin: 18.2, labor_pct: 32.1, gross_margin: 68.5 },
            { month: 'Feb 2024', revenue: (298/revenueTarget)*100, revenue_actual: 298, ebitda_margin: 19.1, labor_pct: 31.8, gross_margin: 69.2 },
            { month: 'Mar 2024', revenue: (312/revenueTarget)*100, revenue_actual: 312, ebitda_margin: 20.3, labor_pct: 30.9, gross_margin: 70.1 },
          ];
        }

        if (storeComparison.length === 0) {
          console.log('AnalyticsCharts: No store data, using fallback');
          storeComparison = [
            { store_name: 'Demo Store 1', revenue: 325, labor_pct: 29.8, ebitda_margin: 22.1, sales_per_sq_ft: 812 },
            { store_name: 'Demo Store 2', revenue: 298, labor_pct: 31.2, ebitda_margin: 19.3, sales_per_sq_ft: 745 },
          ];
        }

        if (performanceMetrics.length === 0) {
          performanceMetrics = [
            { name: 'Labor Cost %', value: 29.8, target: 30.0, color: '#059669', type: 'percentage' },
            { name: 'EBITDA Margin %', value: 22.1, target: 20.0, color: '#d12a2f', type: 'percentage' },
            { name: 'Revenue (K)', value: 312, target: 300, color: '#2563eb', type: 'currency' }
          ];
        }

        // Calculate dynamic insights
        const calculateInsights = () => {
          let insights = {
            revenueGrowth: '+14% YTD',
            bestMonth: 'June 2024',
            topPerformer: 'Airport Terminal',
            ourRank: '#1 of 5',
            metricsOnTarget: '3 of 3',
            overallScore: 'Excellent'
          };

          // Calculate revenue growth from monthly trends
          if (monthlyTrends.length >= 2) {
            const latest = monthlyTrends[monthlyTrends.length - 1];
            const previous = monthlyTrends[monthlyTrends.length - 2];
            if (latest && previous && previous.revenue > 0) {
              const growth = ((latest.revenue - previous.revenue) / previous.revenue * 100);
              insights.revenueGrowth = `${growth >= 0 ? '+' : ''}${Math.round(growth)}% MoM`;
            }
            
            // Find best performing month
            const bestMonth = monthlyTrends.reduce((best, current) => 
              current.revenue > best.revenue ? current : best
            );
            insights.bestMonth = bestMonth.month;
          }

          // Find top performing store
          if (storeComparison.length > 0) {
            const topStore = storeComparison.reduce((best, current) => 
              current.sales_per_sq_ft > best.sales_per_sq_ft ? current : best
            );
            insights.topPerformer = topStore.store_name;
            insights.ourRank = `#1 of ${storeComparison.length}`;
          }

          // Calculate metrics on target
          const onTarget = performanceMetrics.filter(metric => metric.value >= metric.target).length;
          const total = performanceMetrics.length;
          insights.metricsOnTarget = `${onTarget} of ${total}`;
          
          if (total > 0) {
            const percentage = (onTarget / total) * 100;
            if (percentage >= 80) insights.overallScore = 'Excellent';
            else if (percentage >= 60) insights.overallScore = 'Good';
            else if (percentage >= 40) insights.overallScore = 'Fair';
            else insights.overallScore = 'Needs Improvement';
          }

          return insights;
        };

        const insights = calculateInsights();

        setChartData({
          monthlyTrends,
          storeComparison,
          performanceMetrics,
          insights
        });

        console.log('AnalyticsCharts: Data loaded successfully', {
          monthlyTrends: monthlyTrends.length,
          storeComparison: storeComparison.length,
          performanceMetrics: performanceMetrics.length
        });

      } catch (error) {
        console.error('AnalyticsCharts: Failed to load data:', error);
        // Use fallback data on error
        const revenueTarget = 350;
        const fallbackData = {
          monthlyTrends: [
            { month: 'Jan 2024', revenue: (285/revenueTarget)*100, revenue_actual: 285, ebitda_margin: 18.2, labor_pct: 32.1, gross_margin: 68.5 },
            { month: 'Feb 2024', revenue: (298/revenueTarget)*100, revenue_actual: 298, ebitda_margin: 19.1, labor_pct: 31.8, gross_margin: 69.2 },
            { month: 'Mar 2024', revenue: (312/revenueTarget)*100, revenue_actual: 312, ebitda_margin: 20.3, labor_pct: 30.9, gross_margin: 70.1 },
          ],
          storeComparison: [
            { store_name: 'Demo Store 1', revenue: 325, labor_pct: 29.8, ebitda_margin: 22.1, sales_per_sq_ft: 812 },
            { store_name: 'Demo Store 2', revenue: 298, labor_pct: 31.2, ebitda_margin: 19.3, sales_per_sq_ft: 745 },
          ],
          performanceMetrics: [
            { name: 'Labor Cost %', value: 29.8, target: 30.0, color: '#059669', type: 'percentage' },
            { name: 'EBITDA Margin %', value: 22.1, target: 20.0, color: '#d12a2f', type: 'percentage' },
            { name: 'Revenue (K)', value: 312, target: 900, color: '#2563eb', type: 'currency' }
          ],
          insights: {
            revenueGrowth: '+4.7% MoM',
            bestMonth: 'Mar 2024',
            topPerformer: 'Demo Store 1',
            ourRank: '#1 of 2',
            metricsOnTarget: '3 of 3',
            overallScore: 'Excellent'
          }
        };
        setChartData(fallbackData);
      } finally {
        setLoading(false);
      }
    };

    loadRealData();
  }, []);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="chart-tooltip">
          <p className="tooltip-label">{label}</p>
          {payload.map((entry, index) => {
            let displayValue = entry.value;
            let unit = '';
            
            if (entry.dataKey === 'revenue') {
              // Show actual revenue value from revenue_actual field
              const actualRevenue = entry.payload?.revenue_actual;
              displayValue = actualRevenue ? Math.round(actualRevenue) : Math.round(entry.value);
              unit = 'K';
            } else if (entry.dataKey.includes('pct') || entry.dataKey.includes('margin')) {
              displayValue = Math.round(entry.value * 10) / 10;
              unit = '%';
            }
            
            return (
              <p key={index} style={{ color: entry.color }}>
                {`${entry.name || entry.dataKey}: ${displayValue}${unit}`}
              </p>
            );
          })}
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="analytics-charts">
        <div className="charts-grid">
          {[1, 2, 3].map((i) => (
            <div key={i} className="chart-container skeleton">
              <div className="skeleton-line"></div>
              <div className="skeleton-line short"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-charts">
      <div className="charts-grid">
        {/* Monthly Revenue & Margin Trends */}
        <div className="chart-container">
          <div className="chart-header">
            <div className="chart-title">
              <TrendingUp size={20} />
              Monthly Performance Trends
            </div>
            <div className="chart-period">Last 6 Months</div>
          </div>
          <div className="chart-content">
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={chartData.monthlyTrends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="month" stroke="#6b7280" fontSize={11} />
                <YAxis stroke="#6b7280" fontSize={11} />
                <Tooltip content={<CustomTooltip />} />
                <Line 
                  type="monotone" 
                  dataKey="revenue" 
                  stroke="#d12a2f" 
                  strokeWidth={3}
                  name="Revenue (% of Target)"
                  dot={{ fill: '#d12a2f', strokeWidth: 2, r: 4 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="ebitda_margin" 
                  stroke="#059669" 
                  strokeWidth={2}
                  name="EBITDA Margin (%)"
                  dot={{ fill: '#059669', strokeWidth: 2, r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="chart-insights">
            <div className="insight-item">
              <span className="insight-label">Revenue Growth</span>
              <span className="insight-value">{chartData.insights?.revenueGrowth || '+14% YTD'}</span>
            </div>
            <div className="insight-item">
              <span className="insight-label">Best Month</span>
              <span className="insight-value">{chartData.insights?.bestMonth || 'June 2024'}</span>
            </div>
          </div>
        </div>

        {/* Store Performance Comparison */}
        <div className="chart-container">
          <div className="chart-header">
            <div className="chart-title">
              <Store size={20} />
              District Store Comparison
            </div>
            <div className="chart-period">Current Month</div>
          </div>
          <div className="chart-content">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={chartData.storeComparison} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis 
                  dataKey="store_name" 
                  stroke="#6b7280" 
                  fontSize={10}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis stroke="#6b7280" fontSize={11} />
                <Tooltip content={<CustomTooltip />} />
                <Bar 
                  dataKey="sales_per_sq_ft" 
                  fill="#d12a2f" 
                  name="Sales per Sq Ft ($)"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="chart-insights">
            <div className="insight-item">
              <span className="insight-label">Top Performer</span>
              <span className="insight-value">{chartData.insights?.topPerformer || 'Airport Terminal'}</span>
            </div>
            <div className="insight-item">
              <span className="insight-label">Our Rank</span>
              <span className="insight-value">{chartData.insights?.ourRank || '#1 of 5'}</span>
            </div>
          </div>
        </div>

        {/* Key Performance Metrics */}
        <div className="chart-container">
          <div className="chart-header">
            <div className="chart-title">
              <DollarSign size={20} />
              Key Performance Metrics
            </div>
            <div className="chart-period">Current vs Target</div>
          </div>
          <div className="chart-content">
            <div className="metrics-comparison">
              {chartData.performanceMetrics.map((metric, index) => (
                <div key={index} className="metric-bar-container">
                  <div className="metric-info">
                    <span className="metric-name">{metric.name}</span>
                    <span className="metric-values">
                      {metric.type === 'currency' ? `${Math.round(metric.value)}K` : `${Math.round(metric.value * 10) / 10}%`}
                      <span className="metric-target">
                        (Target: {metric.type === 'currency' ? `${metric.target}K` : `${metric.target}%`})
                      </span>
                    </span>
                  </div>
                  <div className="metric-bar-background">
                    <div 
                      className="metric-bar-fill"
                      style={{ 
                        width: `${Math.min(Math.max((metric.value / metric.target) * 100, 0), 100)}%`,
                        backgroundColor: metric.color
                      }}
                    ></div>
                    <div 
                      className="metric-target-line"
                      style={{ left: '100%' }}
                    ></div>
                  </div>
                  <div className={`metric-status ${metric.value >= metric.target ? 'positive' : 'negative'}`}>
                    {metric.value >= metric.target ? '✓' : '△'} 
                    {metric.value >= metric.target ? 'On Target' : 'Below Target'}
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="chart-insights">
            <div className="insight-item">
              <span className="insight-label">Metrics On Target</span>
              <span className="insight-value">{chartData.insights?.metricsOnTarget || '3 of 3'}</span>
            </div>
            <div className="insight-item">
              <span className="insight-label">Overall Score</span>
              <span className="insight-value">{chartData.insights?.overallScore || 'Excellent'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsCharts;
