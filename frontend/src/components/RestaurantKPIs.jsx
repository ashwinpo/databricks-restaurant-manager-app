import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, DollarSign, Users, ChefHat, Target } from 'lucide-react';
import { apiService } from '../services/apiService.js';

// Helper functions for KPI transformation
const formatKPIValue = (name, value) => {
  if (name.toLowerCase().includes('revenue')) {
    return `$${(value / 1000).toFixed(0)}K`;
  }
  if (name.toLowerCase().includes('margin') || name.toLowerCase().includes('labor')) {
    return `${value.toFixed(1)}%`;
  }
  if (name.toLowerCase().includes('transaction')) {
    return value.toLocaleString();
  }
  return value.toString();
};

const getKPIIcon = (name) => {
  if (name.toLowerCase().includes('revenue')) return DollarSign;
  if (name.toLowerCase().includes('labor')) return Users;
  if (name.toLowerCase().includes('margin')) return Target;
  if (name.toLowerCase().includes('transaction')) return ChefHat;
  return TrendingUp;
};

const getKPIStatus = (name, change) => {
  // For labor costs, positive change is bad
  if (name.toLowerCase().includes('labor')) {
    return change > 2 ? 'alert' : change > 0 ? 'warning' : 'good';
  }
  // For revenue and margins, positive change is good
  return change > 2 ? 'good' : change > 0 ? 'warning' : 'alert';
};

const getKPIColor = (name, change) => {
  const status = getKPIStatus(name, change);
  switch (status) {
    case 'good': return 'var(--color-success)';
    case 'warning': return 'var(--color-warning)';
    case 'alert': return 'var(--color-error)';
    default: return 'var(--color-gray-500)';
  }
};

const getKPIInsight = (name, change) => {
  if (name.toLowerCase().includes('labor') && change > 2) {
    return 'Consider early releases or task reassignment';
  }
  if (name.toLowerCase().includes('revenue') && change > 5) {
    return 'Strong performance - maintain momentum';
  }
  if (name.toLowerCase().includes('margin') && change < -2) {
    return 'Review food costs and portion control';
  }
  return change > 0 ? 'Trending upward' : 'Needs attention';
};

const RestaurantKPIs = ({ config }) => {
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);

  // Load real KPI data from backend API
  useEffect(() => {
    const loadKPIs = async () => {
      try {
        const response = await apiService.getKPIs();
        if (response.status === 'success') {
          // Transform API KPIs to component format
          const transformedKPIs = response.kpis.map(kpi => ({
            id: kpi.name.toLowerCase().replace(/\s+/g, '_'),
            title: kpi.name,
            value: formatKPIValue(kpi.name, kpi.value),
            change: `${kpi.change > 0 ? '+' : ''}${kpi.change.toFixed(1)}%`,
            trend: kpi.change > 0 ? 'up' : 'down',
            status: getKPIStatus(kpi.name, kpi.change),
            icon: getKPIIcon(kpi.name),
            period: kpi.period,
            color: getKPIColor(kpi.name, kpi.change),
            insight: getKPIInsight(kpi.name, kpi.change)
          }));
          setMetrics(transformedKPIs);
        }
      } catch (error) {
        console.error('Failed to load KPIs:', error);
        // Fallback to demo data on error
        setMetrics([
        {
          id: 'labor_cost',
          title: 'Labor Cost %',
          value: '34.2%',
          target: '30.0%',
          change: '+4.2%',
          trend: 'up',
          status: 'warning', // over target
          icon: Users,
          period: 'vs target',
          color: 'var(--color-warning)',
          insight: '4% over target - consider early releases'
        },
        {
          id: 'food_cost',
          title: 'Food Cost %',
          value: '28.5%',
          target: '30.0%',
          change: '-1.5%',
          trend: 'down',
          status: 'good', // under target
          icon: ChefHat,
          period: 'vs target',
          color: 'var(--color-success)',
          insight: 'On track - good portion control'
        },
        {
          id: 'sales_pace',
          title: 'Sales Pace',
          value: '$2,847',
          target: '$3,200',
          change: '-11%',
          trend: 'down',
          status: 'alert', // significantly under
          icon: DollarSign,
          period: 'vs forecast',
          color: 'var(--color-error)',
          insight: 'Behind forecast - weather impact?'
        },
        {
          id: 'margin_target',
          title: 'Margin %',
          value: '68.7%',
          target: '70.0%',
          change: '-1.3%',
          trend: 'down',
          status: 'warning', // slightly under
          icon: Target,
          period: 'vs target',
          color: 'var(--color-warning)',
          insight: 'Push higher margin items'
        }
        ]);
      } finally {
        setLoading(false);
      }
    };

    loadKPIs();
    // Refresh KPIs every 2 minutes
    const interval = setInterval(loadKPIs, 2 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    const statusColors = {
      good: 'var(--color-success)',
      warning: 'var(--color-warning)',
      alert: 'var(--color-error)'
    };
    return statusColors[status] || 'var(--color-gray-500)';
  };

  const getStatusBackground = (status) => {
    const statusBgs = {
      good: 'var(--color-success-light)',
      warning: 'var(--color-warning-light)',
      alert: 'var(--color-error-light)'
    };
    return statusBgs[status] || 'var(--color-gray-100)';
  };

  if (loading) {
    return (
      <div className="restaurant-kpis">
        <div className="section-header">
          <h3>Restaurant Performance</h3>
        </div>
        <div className="kpi-grid">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="kpi-card skeleton">
              <div className="skeleton-line"></div>
              <div className="skeleton-line short"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="restaurant-kpis">
      <div className="section-header">
        <h3>Restaurant Performance</h3>
        <div className="section-header-meta">
          <span className="timestamp">Live • Updated 2 min ago</span>
          <button className="refresh-btn">
            <TrendingUp size={16} />
            Refresh
          </button>
        </div>
      </div>
      
      <div className="kpi-grid">
        {metrics.map((metric) => {
          const IconComponent = metric.icon;
          const TrendIcon = metric.trend === 'up' ? TrendingUp : TrendingDown;
          
          return (
            <div 
              key={metric.id} 
              className="kpi-card"
              style={{ 
                borderColor: getStatusColor(metric.status),
                background: `linear-gradient(135deg, ${getStatusBackground(metric.status)} 0%, var(--color-background) 100%)`
              }}
            >
              <div className="kpi-header">
                <div 
                  className="kpi-icon" 
                  style={{ 
                    color: getStatusColor(metric.status),
                    background: getStatusBackground(metric.status)
                  }}
                >
                  <IconComponent size={24} />
                </div>
                <div className={`kpi-trend ${metric.trend}`}>
                  <TrendIcon size={16} />
                  <span>{metric.change}</span>
                </div>
              </div>
              
              <div className="kpi-content">
                <div className="kpi-value">{metric.value}</div>
                <div className="kpi-title">{metric.title}</div>
                <div className="kpi-target">Target: {metric.target}</div>
                <div className="kpi-period">{metric.period}</div>
              </div>

              <div className="kpi-insight">
                <div 
                  className="insight-indicator"
                  style={{ backgroundColor: getStatusColor(metric.status) }}
                ></div>
                <span className="insight-text">{metric.insight}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Action Suggestions */}
      <div className="kpi-actions">
        <div className="action-header">
          <h4>Quick Actions</h4>
        </div>
        <div className="action-buttons">
          <button className="action-btn primary">
            <Users size={16} />
            Send Team Home Early
          </button>
          <button className="action-btn secondary">
            <ChefHat size={16} />
            Adjust Menu Mix
          </button>
          <button className="action-btn secondary">
            <Target size={16} />
            Update POS Prompts
          </button>
        </div>
      </div>
    </div>
  );
};

export default RestaurantKPIs;
