import React, { useState, useEffect } from 'react';
import { AlertTriangle, TrendingDown, TrendingUp, Target, ArrowRight, CheckCircle, X, Clock, DollarSign, BarChart3, AlertCircle, Zap } from 'lucide-react';
import { apiService } from '../services/apiService.js';

const PnLInsightsBrief = ({ config }) => {
  const [activeModal, setActiveModal] = useState(null);
  const [completedActions, setCompletedActions] = useState(new Set());
  const [activeOperations, setActiveOperations] = useState([]);
  const [loading, setLoading] = useState(true);

  // State for dynamic insights data
  const [insightsConfig, setInsightsConfig] = useState(null);
  const [configError, setConfigError] = useState(null);

  // Load P&L insights from config file
  useEffect(() => {
    const loadInsights = async () => {
      try {
        setLoading(true);
        const response = await fetch('/pnl-insights-config.json');
        if (!response.ok) {
          throw new Error(`Failed to load insights config: ${response.statusText}`);
        }
        const config = await response.json();
        setInsightsConfig(config);
        setConfigError(null);
        console.log('✅ Loaded P&L insights config:', config.metadata);
      } catch (error) {
        console.error('❌ Failed to load P&L insights config:', error);
        setConfigError(error.message);
        // Fall back to hardcoded data if config fails to load
        setInsightsConfig(null);
      } finally {
        setLoading(false);
      }
    };

    loadInsights();
    // Refresh insights every 30 minutes (P&L data doesn't change as frequently)
    const interval = setInterval(loadInsights, 30 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);
  
  // P&L Insights Cards based on actual Store 1619 analysis
  const pnlInsightsCards = [
    {
      id: 1,
      type: 'critical',
      priority: 'urgent',
      icon: TrendingDown,
      title: 'Beverage Revenue Crisis',
      description: 'Beverage sales are 18.6% below plan ($15,826 vs $19,442) - a $3,616 shortfall representing the most concerning category performance this period.',
      metric: '-18.6%',
      metricLabel: 'Below Plan',
      actualValue: '$15,826',
      plannedValue: '$19,442',
      variance: '$3,616',
      recommendation: 'Immediate beverage operations audit: check equipment functionality, staff training, and upselling techniques.',
      actions: [
        { label: 'Equipment Audit', type: 'primary', action: 'beverageAudit' },
        { label: 'Staff Training', type: 'secondary', action: 'beverageTraining' }
      ],
      impact: 'Critical - largest revenue gap',
      timeframe: 'Immediate (Week 1)',
      dataSource: 'P&L Analysis - Net Sales Breakdown'
    },
    {
      id: 2,
      type: 'opportunity',
      priority: 'high',
      icon: DollarSign,
      title: 'Promotional ROI Misalignment', 
      description: 'Sales promotions overspend by 37.4% ($19,458 vs $14,164 plan) while overall sales are down 6.1%. Heavy promotional spending is not driving corresponding revenue increases.',
      metric: '+37.4%',
      metricLabel: 'Over Budget',
      actualValue: '$19,458',
      plannedValue: '$14,164',
      variance: '+$5,294',
      recommendation: 'Reduce promotional spend by 20-25% and implement targeted, higher-ROI initiatives.',
      actions: [
        { label: 'Reduce Promotions', type: 'primary', action: 'reducePromotions' },
        { label: 'ROI Analysis', type: 'secondary', action: 'analyzeROI' }
      ],
      impact: 'High - immediate cost savings',
      timeframe: 'This week',
      dataSource: 'P&L Analysis - Sales Discounts & Promotions'
    },
    {
      id: 3,
      type: 'alert',
      priority: 'high',
      icon: BarChart3,
      title: 'Overall Revenue Underperformance',
      description: 'Food sales missing plan by $20,953 (-6.1%) with total revenue at $320,433 vs $341,386 plan. This cascades through all profitability metrics.',
      metric: '-6.1%',
      metricLabel: 'Below Plan',
      actualValue: '$320,433',
      plannedValue: '$341,386',
      variance: '$20,953',
      recommendation: 'Implement traffic analysis to determine if decline is customer count vs. average ticket reduction.',
      actions: [
        { label: 'Traffic Analysis', type: 'primary', action: 'trafficAnalysis' },
        { label: 'Menu Mix Review', type: 'secondary', action: 'menuMixReview' }
      ],
      impact: 'High - affects all profitability',
      timeframe: 'Month 1',
      dataSource: 'P&L Analysis - Food Sales Performance'
    },
    {
      id: 4,
      type: 'insight',
      priority: 'medium',
      icon: Target,
      title: 'Labor Cost Optimization Opportunity',
      description: 'Employee meals variance shows 43.7% reduction ($5,882 vs $10,454 plan), potentially indicating reduced staffing levels or improved meal cost controls.',
      metric: '-43.7%',
      metricLabel: 'Below Plan',
      actualValue: '$5,882',
      plannedValue: '$10,454',
      variance: '$4,572',
      recommendation: 'Review staffing levels to ensure adequate service quality while maintaining cost controls.',
      actions: [
        { label: 'Staffing Review', type: 'primary', action: 'staffingReview' },
        { label: 'Service Quality Check', type: 'secondary', action: 'serviceCheck' }
      ],
      impact: 'Medium - balance cost vs service',
      timeframe: '30-90 days',
      dataSource: 'P&L Analysis - Employee Meals & Labor'
    },
    {
      id: 5,
      type: 'performance',
      priority: 'medium',
      icon: AlertCircle,
      title: 'Profitability Compression',
      description: 'Restaurant Contribution down 6.1% ($562,065 vs $598,443) and Controllable Profit down 6.6% ($539,814 vs $577,730), indicating operational efficiency challenges.',
      metric: '-6.6%',
      metricLabel: 'Controllable Profit',
      actualValue: '$539,814',
      plannedValue: '$577,730',
      variance: '$37,916',
      recommendation: 'Target 3-4% improvement in controllable profit through operational efficiency gains.',
      actions: [
        { label: 'Cost Analysis', type: 'primary', action: 'costAnalysis' },
        { label: 'Efficiency Review', type: 'secondary', action: 'efficiencyReview' }
      ],
      impact: 'Medium - bottom-line focus',
      timeframe: '90+ days',
      dataSource: 'P&L Analysis - Profitability Metrics'
    }
  ];

  const getPriorityColor = (priority) => {
    const colorMap = {
      urgent: '#dc2626', // red-600
      high: '#ea580c',   // orange-600
      medium: '#2563eb', // blue-600
      low: '#6b7280'     // gray-500
    };
    return colorMap[priority] || '#6b7280';
  };

  const getTypeColor = (type) => {
    const colorMap = {
      critical: '#dc2626',
      alert: '#ea580c',
      opportunity: '#16a34a',
      insight: '#2563eb',
      performance: '#7c3aed'
    };
    return colorMap[type] || '#6b7280';
  };

  const getIconComponent = (iconName) => {
    const iconMap = {
      TrendingDown: TrendingDown,
      TrendingUp: TrendingUp,
      DollarSign: DollarSign,
      BarChart3: BarChart3,
      Target: Target,
      AlertCircle: AlertCircle,
      AlertTriangle: AlertTriangle,
      CheckCircle: CheckCircle,
      Clock: Clock,
      Zap: Zap
    };
    return iconMap[iconName] || AlertTriangle;
  };

  const formatCurrency = (value) => {
    if (typeof value === 'string' && value.startsWith('$')) return value;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const handleAction = (action, cardId) => {
    const modalContent = {
      beverageAudit: {
        title: 'Beverage Operations Audit - Immediate Action',
        content: (
          <div>
            <div className="alert-box critical">
              <strong>Critical Issue:</strong> $3,616 revenue shortfall in beverages (18.6% below plan)
            </div>
            <div style={{ marginTop: '1rem' }}>
              <h4>Immediate Checklist:</h4>
              <ul>
                <li><strong>Equipment Check:</strong> Fountain machines, ice machines, beverage dispensers</li>
                <li><strong>Inventory Audit:</strong> Verify beverage supplies and syrup levels</li>
                <li><strong>POS Review:</strong> Ensure all beverage options are active and visible</li>
                <li><strong>Staff Interview:</strong> Ask team about customer beverage requests/complaints</li>
              </ul>
            </div>
            <div style={{ marginTop: '1rem' }}>
              <h4>Expected Findings & Solutions:</h4>
              <ul>
                <li><strong>If Equipment Issues:</strong> Schedule immediate repair/replacement</li>
                <li><strong>If Staff Training:</strong> Implement upselling techniques training</li>
                <li><strong>If Menu Issues:</strong> Review beverage positioning and pricing</li>
              </ul>
            </div>
            <div className="impact-box">
              <strong>Potential Recovery:</strong> Fixing this could recover $2,000-3,000 monthly revenue
            </div>
          </div>
        )
      },
      beverageTraining: {
        title: 'Beverage Upselling Training Program',
        content: (
          <div>
            <div style={{ marginBottom: '1rem' }}>
              <h4>Training Focus Areas:</h4>
              <ul>
                <li><strong>Suggestive Selling:</strong> "Would you like a drink with that?"</li>
                <li><strong>Size Upselling:</strong> Highlight value of larger sizes</li>
                <li><strong>Pairing Recommendations:</strong> Match beverages with food items</li>
                <li><strong>Limited Time Offers:</strong> Promote seasonal/specialty drinks</li>
              </ul>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <h4>Implementation Plan:</h4>
              <ul>
                <li>15-minute team huddle this week</li>
                <li>Role-play scenarios with front counter staff</li>
                <li>Daily reminders for first week</li>
                <li>Track beverage attach rate improvement</li>
              </ul>
            </div>
            <div className="target-box">
              <strong>Target:</strong> Increase beverage attach rate from current to 85%+ within 2 weeks
            </div>
          </div>
        )
      },
      reducePromotions: {
        title: 'Promotional Spend Optimization',
        content: (
          <div>
            <div className="alert-box warning">
              <strong>Current Issue:</strong> $5,294 promotional overspend (37.4% above plan) with declining sales
            </div>
            <div style={{ marginTop: '1rem' }}>
              <h4>Immediate Actions:</h4>
              <ul>
                <li><strong>Pause Low-ROI Promotions:</strong> Identify worst-performing discounts</li>
                <li><strong>Reduce Discount Depth:</strong> Lower discount percentages by 5-10%</li>
                <li><strong>Target Specific Times:</strong> Focus promotions on slow periods only</li>
                <li><strong>Track Performance:</strong> Measure sales lift vs. discount cost</li>
              </ul>
            </div>
            <div style={{ marginTop: '1rem' }}>
              <h4>Recommended Changes:</h4>
              <ul>
                <li>Reduce overall promotional budget by 25% ($4,865 target vs $6,486 current)</li>
                <li>Focus on high-margin items and combo deals</li>
                <li>Implement time-based promotions (happy hour, lunch specials)</li>
              </ul>
            </div>
            <div className="savings-box">
              <strong>Expected Savings:</strong> $1,300-1,600 monthly while maintaining traffic
            </div>
          </div>
        )
      },
      analyzeROI: {
        title: 'Promotional ROI Analysis',
        content: (
          <div>
            <div style={{ marginBottom: '1rem' }}>
              <h4>Analysis Framework:</h4>
              <ul>
                <li><strong>Revenue Impact:</strong> Track sales lift during promotional periods</li>
                <li><strong>Margin Analysis:</strong> Calculate profit after discount costs</li>
                <li><strong>Customer Behavior:</strong> Monitor repeat visits and upselling</li>
                <li><strong>Competitive Response:</strong> Assess market positioning</li>
              </ul>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <h4>Key Metrics to Track:</h4>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #e5e7eb' }}>
                    <th style={{ textAlign: 'left', padding: '0.5rem' }}>Metric</th>
                    <th style={{ textAlign: 'right', padding: '0.5rem' }}>Target</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style={{ padding: '0.5rem' }}>Sales Lift</td>
                    <td style={{ textAlign: 'right', padding: '0.5rem' }}>+15% minimum</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '0.5rem' }}>Profit Margin</td>
                    <td style={{ textAlign: 'right', padding: '0.5rem' }}>Maintain &gt;12%</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '0.5rem' }}>Customer Retention</td>
                    <td style={{ textAlign: 'right', padding: '0.5rem' }}>+5% repeat visits</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div className="action-box">
              <strong>Next Steps:</strong> Weekly ROI review meetings, data-driven promotion decisions
            </div>
          </div>
        )
      },
      trafficAnalysis: {
        title: 'Customer Traffic vs. Ticket Analysis',
        content: (
          <div>
            <div className="insight-box">
              <strong>Key Question:</strong> Is the $20,953 revenue decline due to fewer customers or smaller orders?
            </div>
            <div style={{ marginTop: '1rem' }}>
              <h4>Analysis Components:</h4>
              <ul>
                <li><strong>Transaction Count:</strong> Daily/hourly customer volume trends</li>
                <li><strong>Average Ticket:</strong> Revenue per transaction analysis</li>
                <li><strong>Time-of-Day Patterns:</strong> Identify slow periods</li>
                <li><strong>Day-of-Week Trends:</strong> Compare to historical patterns</li>
              </ul>
            </div>
            <div style={{ marginTop: '1rem' }}>
              <h4>Action Plan Based on Findings:</h4>
              <div style={{ marginLeft: '1rem' }}>
                <p><strong>If Traffic is Down:</strong></p>
                <ul>
                  <li>Marketing campaigns to drive foot traffic</li>
                  <li>Community outreach and local partnerships</li>
                  <li>Review hours of operation and staffing</li>
                </ul>
                <p style={{ marginTop: '1rem' }}><strong>If Ticket Size is Down:</strong></p>
                <ul>
                  <li>Upselling training for staff</li>
                  <li>Menu engineering (highlight high-margin items)</li>
                  <li>Combo deal optimization</li>
                </ul>
              </div>
            </div>
            <div className="timeline-box">
              <strong>Timeline:</strong> Complete analysis within 1 week, implement solutions within 2 weeks
            </div>
          </div>
        )
      },
      menuMixReview: {
        title: 'Menu Mix Performance Review',
        content: (
          <div>
            <div style={{ marginBottom: '1rem' }}>
              <h4>Menu Engineering Analysis:</h4>
              <ul>
                <li><strong>Item Performance:</strong> Rank items by sales volume and profitability</li>
                <li><strong>Margin Analysis:</strong> Identify high and low-margin items</li>
                <li><strong>Customer Preferences:</strong> Track ordering patterns</li>
                <li><strong>Competitive Positioning:</strong> Compare to market offerings</li>
              </ul>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <h4>Focus Areas:</h4>
              <ul>
                <li><strong>Star Items:</strong> High volume, high margin - promote more</li>
                <li><strong>Problem Items:</strong> Low volume, low margin - consider removal</li>
                <li><strong>Opportunity Items:</strong> High margin, low volume - increase visibility</li>
                <li><strong>Workhorses:</strong> High volume, low margin - optimize costs</li>
              </ul>
            </div>
            <div style={{ marginTop: '1rem' }}>
              <h4>Implementation Actions:</h4>
              <ul>
                <li>Reposition high-margin items on menu boards</li>
                <li>Train staff on profitable item recommendations</li>
                <li>Consider limited-time offers for underperforming items</li>
                <li>Optimize portion sizes and pricing</li>
              </ul>
            </div>
            <div className="goal-box">
              <strong>Goal:</strong> Improve overall food margin by 2-3% through better mix
            </div>
          </div>
        )
      },
      staffingReview: {
        title: 'Staffing Level & Service Quality Review',
        content: (
          <div>
            <div className="balance-box">
              <strong>Balance Point:</strong> Employee meals down 43.7% suggests potential understaffing
            </div>
            <div style={{ marginTop: '1rem' }}>
              <h4>Review Areas:</h4>
              <ul>
                <li><strong>Service Speed:</strong> Average order fulfillment time</li>
                <li><strong>Customer Satisfaction:</strong> Complaints and feedback trends</li>
                <li><strong>Staff Workload:</strong> Employee stress and overtime patterns</li>
                <li><strong>Peak Period Coverage:</strong> Adequate staffing during rush hours</li>
              </ul>
            </div>
            <div style={{ marginTop: '1rem' }}>
              <h4>Assessment Methods:</h4>
              <ul>
                <li>Mystery shopper evaluations</li>
                <li>Customer wait time measurements</li>
                <li>Employee feedback sessions</li>
                <li>Comparison to high-performing periods</li>
              </ul>
            </div>
            <div style={{ marginTop: '1rem' }}>
              <h4>Potential Actions:</h4>
              <ul>
                <li><strong>If Understaffed:</strong> Selective hiring for peak periods</li>
                <li><strong>If Efficient:</strong> Document best practices for other periods</li>
                <li><strong>If Quality Issues:</strong> Additional training and support</li>
              </ul>
            </div>
            <div className="caution-box">
              <strong>Caution:</strong> Don't compromise service quality for short-term cost savings
            </div>
          </div>
        )
      },
      serviceCheck: {
        title: 'Service Quality Assessment',
        content: (
          <div>
            <div style={{ marginBottom: '1rem' }}>
              <h4>Quality Metrics to Monitor:</h4>
              <ul>
                <li><strong>Speed of Service:</strong> Order to fulfillment time</li>
                <li><strong>Order Accuracy:</strong> Correct orders vs. errors</li>
                <li><strong>Food Quality:</strong> Temperature, freshness, presentation</li>
                <li><strong>Customer Experience:</strong> Friendliness, helpfulness</li>
              </ul>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <h4>Assessment Tools:</h4>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #e5e7eb' }}>
                    <th style={{ textAlign: 'left', padding: '0.5rem' }}>Method</th>
                    <th style={{ textAlign: 'left', padding: '0.5rem' }}>Frequency</th>
                    <th style={{ textAlign: 'left', padding: '0.5rem' }}>Target</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style={{ padding: '0.5rem' }}>Mystery Shopping</td>
                    <td style={{ padding: '0.5rem' }}>Weekly</td>
                    <td style={{ padding: '0.5rem' }}>85%+ satisfaction</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '0.5rem' }}>Customer Surveys</td>
                    <td style={{ padding: '0.5rem' }}>Ongoing</td>
                    <td style={{ padding: '0.5rem' }}>4.2+ rating</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '0.5rem' }}>Time Studies</td>
                    <td style={{ padding: '0.5rem' }}>Daily</td>
                    <td style={{ padding: '0.5rem' }}>&lt;3 min average</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div className="standard-box">
              <strong>Quality Standards:</strong> Maintain service excellence while optimizing costs
            </div>
          </div>
        )
      },
      costAnalysis: {
        title: 'Comprehensive Cost Analysis',
        content: (
          <div>
            <div className="focus-box">
              <strong>Focus:</strong> Identify specific cost reduction opportunities to improve controllable profit
            </div>
            <div style={{ marginTop: '1rem' }}>
              <h4>Cost Categories to Analyze:</h4>
              <ul>
                <li><strong>Food Costs:</strong> Waste reduction, portion control, supplier negotiations</li>
                <li><strong>Labor Costs:</strong> Scheduling optimization, productivity improvements</li>
                <li><strong>Controllable Expenses:</strong> Utilities, supplies, maintenance</li>
                <li><strong>Promotional Costs:</strong> ROI analysis and optimization</li>
              </ul>
            </div>
            <div style={{ marginTop: '1rem' }}>
              <h4>Analysis Framework:</h4>
              <ul>
                <li>Benchmark against top-performing periods</li>
                <li>Compare to district/company averages</li>
                <li>Identify seasonal and trend patterns</li>
                <li>Calculate cost per transaction metrics</li>
              </ul>
            </div>
            <div style={{ marginTop: '1rem' }}>
              <h4>Target Improvements:</h4>
              <ul>
                <li>Food cost reduction: 1-2% of sales</li>
                <li>Labor optimization: 0.5-1% efficiency gain</li>
                <li>Controllable expense reduction: $500-1000/month</li>
              </ul>
            </div>
            <div className="target-box">
              <strong>Overall Target:</strong> Improve controllable profit by 3-4% ($16,000-21,000 annually)
            </div>
          </div>
        )
      },
      efficiencyReview: {
        title: 'Operational Efficiency Review',
        content: (
          <div>
            <div style={{ marginBottom: '1rem' }}>
              <h4>Efficiency Areas to Review:</h4>
              <ul>
                <li><strong>Kitchen Operations:</strong> Food prep, cooking processes, waste management</li>
                <li><strong>Service Flow:</strong> Order taking, fulfillment, customer flow</li>
                <li><strong>Inventory Management:</strong> Ordering, storage, rotation</li>
                <li><strong>Staff Productivity:</strong> Task allocation, cross-training, teamwork</li>
              </ul>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <h4>Best Practice Implementation:</h4>
              <ul>
                <li>Standardize high-performing procedures</li>
                <li>Eliminate non-value-added activities</li>
                <li>Optimize equipment utilization</li>
                <li>Improve communication and coordination</li>
              </ul>
            </div>
            <div style={{ marginTop: '1rem' }}>
              <h4>Measurement and Tracking:</h4>
              <ul>
                <li>Productivity metrics by position</li>
                <li>Process time measurements</li>
                <li>Quality and accuracy rates</li>
                <li>Customer satisfaction scores</li>
              </ul>
            </div>
            <div className="improvement-box">
              <strong>Expected Outcomes:</strong> 5-10% productivity improvement within 90 days
            </div>
          </div>
        )
      }
    };

    setActiveModal({
      ...modalContent[action],
      action,
      cardId
    });
  };

  const closeModal = () => {
    setActiveModal(null);
  };

  const handleActionComplete = (action, cardId) => {
    const actionKey = `${cardId}-${action}`;
    setCompletedActions(prev => new Set([...prev, actionKey]));

    // Track operations that were initiated
    const operationMap = {
      beverageAudit: {
        name: "Beverage Operations Audit",
        type: "Revenue Recovery",
        impact: "Potential $2,000-3,000 monthly recovery",
        expectedCompletion: "This week"
      },
      reducePromotions: {
        name: "Promotional Spend Optimization",
        type: "Cost Reduction",
        impact: "Save $1,300-1,600 monthly",
        expectedCompletion: "Immediate"
      },
      trafficAnalysis: {
        name: "Customer Traffic Analysis",
        type: "Revenue Analysis",
        impact: "Identify root cause of revenue decline",
        expectedCompletion: "1 week"
      },
      staffingReview: {
        name: "Staffing & Service Quality Review",
        type: "Operations Optimization",
        impact: "Balance cost control with service quality",
        expectedCompletion: "2 weeks"
      },
      costAnalysis: {
        name: "Comprehensive Cost Analysis",
        type: "Profitability Improvement",
        impact: "3-4% controllable profit improvement",
        expectedCompletion: "30 days"
      }
    };

    if (operationMap[action]) {
      const newOperation = {
        id: Date.now(),
        ...operationMap[action],
        status: "In Progress",
        initiated: new Date()
      };
      setActiveOperations(prev => [...prev, newOperation]);
    }

    setActiveModal(null);
  };

  const isActionCompleted = (cardId, action) => {
    return completedActions.has(`${cardId}-${action}`);
  };

  if (loading) {
    return (
      <div className="operations-brief">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading P&L insights...</p>
        </div>
      </div>
    );
  }

  if (configError) {
    return (
      <div className="operations-brief">
        <div className="error-message">
          <AlertTriangle size={24} />
          <h3>Configuration Error</h3>
          <p>Failed to load P&L insights configuration: {configError}</p>
          <p>Using fallback data for demonstration.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="operations-brief">
      {/* Compact KPI Header */}
      <div className="kpi-header">
        {/* <div className="store-info">
          <h2>Store 1619 P&L</h2>
          <span className="period">Period 202507</span>
        </div> */}
        
         <div className="kpi-metrics">
           <div className="kpi-card revenue">
             <div className="kpi-value">
               {insightsConfig?.kpi_header?.revenue?.value || '-6.1%'}
             </div>
             <div className="kpi-label">Revenue vs Plan</div>
             <div className="kpi-amount">
               {insightsConfig?.kpi_header?.revenue?.amount || '$320,433'}
             </div>
           </div>
           <div className="kpi-card profit">
             <div className="kpi-value">
               {insightsConfig?.kpi_header?.profit?.value || '-6.6%'}
             </div>
             <div className="kpi-label">Controllable Profit</div>
             <div className="kpi-amount">
               {insightsConfig?.kpi_header?.profit?.amount || '$539,814'}
             </div>
           </div>
           <div className="kpi-card critical">
             <div className="kpi-value">
               {insightsConfig?.kpi_header?.critical?.value || '-18.6%'}
             </div>
             <div className="kpi-label">
               {insightsConfig?.kpi_header?.critical?.label || 'Beverage Sales'}
             </div>
             <div className="kpi-amount">
               {insightsConfig?.kpi_header?.critical?.amount || '$15,826'}
             </div>
           </div>
         </div>
      </div>

      <div className="insights-grid">
        {(insightsConfig?.insight_cards || pnlInsightsCards).map((card) => {
          const IconComponent = getIconComponent(card.icon);
          
          return (
            <div key={card.id} className={`insight-card ${card.type}`}>
              {/* Priority Indicator */}
              <div className="priority-bar" style={{ backgroundColor: getPriorityColor(card.priority) }}></div>
              
              {/* Main Insight Content */}
              <div className="insight-content">
                <div className="insight-header">
                  <div className="insight-icon" style={{ color: getTypeColor(card.type) }}>
                    <IconComponent size={20} />
                  </div>
                  <div className="insight-metric">
                    <span className="metric-value" style={{ 
                      color: card.metric.startsWith('-') ? '#dc2626' : 
                             card.metric.startsWith('+') ? '#ea580c' : '#2563eb'
                    }}>
                      {card.metric}
                    </span>
                    <span className="metric-variance">{card.variance}</span>
                  </div>
                </div>
                
                <h3 className="insight-title">{card.title}</h3>
                <p className="insight-description">{card.recommendation}</p>
              </div>

              {/* Action Buttons */}
              <div className="insight-actions">
                <button 
                  className="action-btn primary"
                  onClick={() => handleAction(card.actions[0].action, card.id)}
                  disabled={isActionCompleted(card.id, card.actions[0].action)}
                >
                  {isActionCompleted(card.id, card.actions[0].action) ? (
                    <>
                      <CheckCircle size={16} />
                      Completed
                    </>
                  ) : (
                    <>
                      <Zap size={16} />
                      {card.actions[0].label}
                    </>
                  )}
                </button>

                <button 
                  className="action-btn secondary"
                  onClick={() => setActiveModal({
                    title: `${card.title} - Why This Matters`,
                    content: (
                      <div>
                        <div className="detail-section">
                          <h4>The Situation</h4>
                          <p>{card.description}</p>
                        </div>
                        
                        <div className="detail-section">
                          <h4>Financial Impact</h4>
                          <div className="financial-breakdown">
                            <div className="breakdown-item">
                              <span>Actual:</span>
                              <span className="value">{card.actualValue}</span>
                            </div>
                            <div className="breakdown-item">
                              <span>Plan:</span>
                              <span className="value">{card.plannedValue}</span>
                            </div>
                            <div className="breakdown-item variance-item">
                              <span>Gap:</span>
                              <span className={`value ${card.variance.startsWith('-') ? 'negative' : 'positive'}`}>
                                {card.variance}
                              </span>
                            </div>
                          </div>
                        </div>

                        <div className="detail-section">
                          <h4>What We Can Do</h4>
                          <div className="actions-list">
                            {card.actions.map((action, index) => (
                              <div key={index} className="action-item">
                                <strong>{action.label}</strong>
                                <p>Expected impact: {card.impact}</p>
                                <p>Timeline: {card.timeframe}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    ),
                    action: 'view_details',
                    cardId: card.id
                  })}
                >
                  Why?
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Active Operations Tracker */}
      {activeOperations.length > 0 && (
        <div className="active-operations">
          <h3><Zap size={20} /> Active Improvement Initiatives</h3>
          <div className="operations-list">
            {activeOperations.map((operation) => (
              <div key={operation.id} className="operation-item">
                <div className="operation-header">
                  <div className="operation-status">
                    <div className="status-indicator pulsing"></div>
                    <span className="status-badge active">{operation.status}</span>
                  </div>
                  <div className="operation-time">
                    Started {operation.initiated.toLocaleTimeString('en-US', { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </div>
                </div>
                <div className="operation-details">
                  <h4>{operation.name}</h4>
                  <div className="operation-meta">
                    <span className="operation-type">{operation.type}</span>
                    <span className="operation-impact">Expected Impact: {operation.impact}</span>
                    <span className="operation-completion">Target: {operation.expectedCompletion}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Modal */}
      {activeModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content pnl-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{activeModal.title}</h3>
              <button className="modal-close" onClick={closeModal}>
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              {activeModal.content}
            </div>
            <div className="modal-footer">
              <button 
                className="modal-btn primary" 
                onClick={() => handleActionComplete(activeModal.action, activeModal.cardId)}
              >
                Initiate Action Plan
              </button>
              <button className="modal-btn secondary" onClick={closeModal}>
                Review Later
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PnLInsightsBrief;
