import React, { useState, useEffect } from 'react';
import { getCurrentConfig, applyTheme, getCurrentShift } from '../config/appConfig';
import DailyOperationsBrief from './DailyOperationsBrief';
import PnLInsightsBrief from './PnLInsightsBrief';
import RestaurantKPIs from './RestaurantKPIs';
import AnalyticsCharts from './AnalyticsCharts';
import GenieChat from './GenieChat';
import { Settings, Bell, Clock, Upload, BarChart3, AlertTriangle, DollarSign, TrendingUp } from 'lucide-react';
import DataUpload from './DataUpload';

const Dashboard = () => {
  const [config] = useState(getCurrentConfig());
  const [currentShift, setCurrentShift] = useState(getCurrentShift());
  const [notifications] = useState(2); // Mock notification count
  const [currentTime, setCurrentTime] = useState(new Date());
  const [showDataUpload, setShowDataUpload] = useState(false);
  const [activeTab, setActiveTab] = useState('pnl'); // 'operations', 'pnl', or 'analytics'

  useEffect(() => {
    // Apply Panda theme colors
    applyTheme(config.theme);
    
    // Update page title
    document.title = `${config.persona.store} - Restaurant Operations`;
    
    // Update favicon if available
    const favicon = document.querySelector('link[rel="icon"]');
    if (favicon && config.company.favicon) {
      favicon.href = config.company.favicon;
    }

    // Update time and shift every minute
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date());
      setCurrentShift(getCurrentShift());
    }, 60000);

    return () => clearInterval(timeInterval);
  }, [config]);

  const formatCurrentTime = () => {
    return currentTime.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true
    });
  };

  return (
    <div className="dashboard">
      {/* Header with Panda branding and restaurant context */}
      <header className="dashboard-header">
        <div className="header-left">
          <img 
            src={config.company.logo} 
            alt={`${config.company.name} Logo`}
            className="panda-logo"
            onError={(e) => { e.target.style.display = 'none'; }}
          />
          <div className="header-text">
            <h1>{config.persona.store}</h1>
            <p className="store-info">{config.persona.location} • {formatCurrentTime()}</p>
          </div>
        </div>
        
        <div className="header-right">
          <div className="shift-indicator">
            <span className="shift-name">{currentShift.name}</span>
            <span className="shift-time">{currentShift.period}</span>
          </div>
          
          <button className="refresh-btn">
            <Bell size={20} />
            {notifications > 0 && <span className="notification-badge">{notifications}</span>}
          </button>
          
          <div className="manager-info">
            <span className="manager-name">{config.persona.name}</span>
            <span className="manager-title">{config.persona.title}</span>
          </div>
          
          <button className="refresh-btn" onClick={() => setShowDataUpload(true)}>
            <Upload size={20} />
          </button>
          
          <button className="refresh-btn">
            <Settings size={20} />
          </button>
        </div>
      </header>

      {/* Tab Navigation */}
      <nav className="tab-navigation">
        <button 
          className={`tab-button ${activeTab === 'pnl' ? 'active' : ''}`}
          onClick={() => setActiveTab('pnl')}
        >
          <DollarSign size={20} />
          P&L Insights
        </button>
        <button 
          className={`tab-button ${activeTab === 'operations' ? 'active' : ''}`}
          onClick={() => setActiveTab('operations')}
        >
          <AlertTriangle size={20} />
          Live Operations
        </button>
        <button 
          className={`tab-button ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
        >
          <BarChart3 size={20} />
          Analytics
        </button>
      </nav>

      {/* Main Content - iPad Landscape Layout */}
      <main className="dashboard-main">
        {activeTab === 'pnl' && (
          <>
            {/* Left Column - P&L Insights */}
            <div className="dashboard-left">
              <section className="dashboard-section full-height">
                <PnLInsightsBrief config={config} />
              </section>
            </div>

            {/* Right Column - Genie Chat */}
            <div className="dashboard-right">
              <section className="dashboard-section genie-section">
                <GenieChat config={config} />
              </section>
            </div>
          </>
        )}

        {activeTab === 'operations' && (
          <>
            {/* Left Column - Full Operations Brief */}
            <div className="dashboard-left">
              <section className="dashboard-section full-height">
                <DailyOperationsBrief config={config} />
              </section>
            </div>

            {/* Right Column - Genie Chat */}
            <div className="dashboard-right">
              <section className="dashboard-section genie-section">
                <GenieChat config={config} />
              </section>
            </div>
          </>
        )}

        {activeTab === 'analytics' && (
          <>
            {/* Left Column - Analytics Charts */}
            <div className="dashboard-left">
              <section className="dashboard-section full-height">
                <AnalyticsCharts config={config} />
              </section>
            </div>

            {/* Right Column - Genie Chat */}
            <div className="dashboard-right">
              <section className="dashboard-section genie-section">
                <GenieChat config={config} />
              </section>
            </div>
          </>
        )}
      </main>

      {/* Data Upload Modal */}
      {showDataUpload && (
        <DataUpload 
          config={config}
          onClose={() => setShowDataUpload(false)}
        />
      )}
    </div>
  );
};

export default Dashboard;
