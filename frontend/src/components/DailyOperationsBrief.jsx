import React, { useState, useEffect } from 'react';
import { AlertTriangle, TrendingUp, Target, ArrowRight, CheckCircle, X, Clock, Users, ChefHat, DollarSign } from 'lucide-react';
import { apiService } from '../services/apiService.js';

const DailyOperationsBrief = ({ config }) => {
  const [activeModal, setActiveModal] = useState(null);
  const [completedActions, setCompletedActions] = useState(new Set());
  const [activeOperations, setActiveOperations] = useState([]);
  const [apiAlerts, setApiAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Load operational alerts from API
  useEffect(() => {
    const loadAlerts = async () => {
      try {
        const response = await apiService.getOperationalAlerts();
        if (response.status === 'success') {
          setApiAlerts(response.alerts);
        }
      } catch (error) {
        console.error('Failed to load operational alerts:', error);
      } finally {
        setLoading(false);
      }
    };

    loadAlerts();
    // Refresh alerts every 5 minutes
    const interval = setInterval(loadAlerts, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);
  
  // Realistic Panda Express operations cards based on actual operational practices
  const operationsCards = [
    {
      id: 1,
      type: 'alert',
      priority: 'high',
      icon: ChefHat,
      title: 'Batch Cooking Waste Alert',
      description: 'Orange Chicken waste is 40% higher on Tuesdays between 2-4 PM. Current 8-pound batch will expire in 12 minutes with only 3 portions sold.',
      metric: '40%',
      metricLabel: 'Higher Waste',
      recommendation: 'Switch to half batches (4 lbs) during slow periods. Each batch takes 15-20 minutes to cook.',
      actions: [
        { label: 'Reduce Batch Size', type: 'primary', action: 'reduceBatch' },
        { label: 'Stagger Cooking', type: 'secondary', action: 'staggerCooking' }
      ],
      timestamp: new Date(Date.now() - 12 * 60 * 1000), // 12 minutes ago
      dataSource: 'Wok Station Timing + Steam Table Monitoring'
    },
    {
      id: 2,
      type: 'opportunity',
      priority: 'urgent',
      icon: Users,
      title: 'Labor Optimization Alert',
      description: 'Overstaffed by 2.5 people for next 3 hours based on transaction patterns. Labor currently at 34.2% vs 30-35% target range.',
      metric: '2.5',
      metricLabel: 'Excess Staff',
      recommendation: 'Send hourly workers home early with 30-min notice per policy. Save $67 in labor costs.',
      actions: [
        { label: 'Early Release', type: 'primary', action: 'earlyRelease' },
        { label: 'Reassign Tasks', type: 'secondary', action: 'reassignTasks' }
      ],
      timestamp: new Date(Date.now() - 8 * 60 * 1000), // 8 minutes ago
      dataSource: 'POS Transaction Patterns + Labor Scheduling'
    },
    {
      id: 3,
      type: 'alert',
      priority: 'urgent',
      icon: Target,
      title: 'Critical Inventory Shortage',
      description: 'Beijing Beef will run out in 4 hours - insufficient for dinner rush. Commissary delivery not until tomorrow 8 AM.',
      metric: '4 hours',
      metricLabel: 'Until Stockout',
      recommendation: 'Emergency transfer from nearby store or 86 the item at 5 PM instead of running out at 7 PM',
      actions: [
        { label: 'Request Transfer', type: 'primary', action: 'requestTransfer' },
        { label: '86 Item Early', type: 'secondary', action: 'removeItem' }
      ],
      timestamp: new Date(Date.now() - 5 * 60 * 1000), // 5 minutes ago
      dataSource: 'ArrowStream Supply Chain + Inventory Thresholds'
    }
  ];

  const getPriorityColor = (priority) => {
    const colorMap = {
      urgent: 'var(--color-error)',
      high: 'var(--color-warning)',
      medium: 'var(--color-primary)',
      low: 'var(--color-gray-500)'
    };
    return colorMap[priority] || 'var(--color-gray-500)';
  };

  const formatTimestamp = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 0) {
      return `${hours}h ago`;
    } else if (minutes > 0) {
      return `${minutes}m ago`;
    } else {
      return 'Just now';
    }
  };

  const handleAction = (action, cardId) => {
    const modalContent = {
      reduceBatch: {
        title: 'Reduce Orange Chicken Batch Size',
        content: (
          <div>
            <p><strong>Current Situation:</strong></p>
            <ul>
              <li>8-pound batch cooking now, expires in 12 minutes</li>
              <li>Only 3 portions sold from current batch</li>
              <li>Tuesday 2-4 PM historically slow period</li>
            </ul>
            <div style={{ marginTop: '1rem' }}>
              <h4>Recommended Action:</h4>
              <ul>
                <li>Switch to 4-pound half batches immediately</li>
                <li>Reduces waste by ~$23 per batch during slow periods</li>
                <li>Cook time remains 15-20 minutes</li>
                <li>Alert wok station chef now</li>
              </ul>
            </div>
            <p><strong>Impact:</strong> Reduce daily food waste by 15-20% during off-peak hours</p>
          </div>
        )
      },
      staggerCooking: {
        title: 'Stagger Orange Chicken Cooking Times',
        content: (
          <div>
            <p><strong>Smart Cooking Schedule:</strong></p>
            <ul>
              <li>Start next 4-pound batch 10 minutes before current expires</li>
              <li>Prevents gaps in availability during slow periods</li>
              <li>Maintains food quality with fresh rotation</li>
            </ul>
            <div style={{ marginTop: '1rem' }}>
              <h4>Implementation:</h4>
              <ul>
                <li>Set kitchen timer for 10-minute prep warning</li>
                <li>Prep ingredients in advance during slow time</li>
                <li>Auto-adjust batch sizes based on hourly patterns</li>
              </ul>
            </div>
            <p><strong>Result:</strong> Eliminate waste while ensuring fresh food availability</p>
          </div>
        )
      },
      earlyRelease: {
        title: 'Early Release - Labor Optimization',
        content: (
          <div>
            <div style={{ marginBottom: '1rem' }}>
              <h4>Recommended early releases (30-min notice):</h4>
              <div style={{ marginTop: '0.5rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>
                  <input type="checkbox" defaultChecked style={{ marginRight: '0.5rem' }} />
                  Alex (Kitchen) - Release at 3:00 PM
                </label>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>
                  <input type="checkbox" defaultChecked style={{ marginRight: '0.5rem' }} />
                  Sam (Front Counter) - Release at 3:00 PM  
                </label>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>
                  <input type="checkbox" style={{ marginRight: '0.5rem' }} />
                  Lisa (Kitchen) - Optional release at 4:00 PM
                </label>
              </div>
            </div>
            <p><strong>Impact:</strong></p>
            <ul>
              <li>Labor cost reduction: $67 over 3 hours</li>
              <li>Brings labor % from 34.2% to 31.8%</li>
              <li>Maintains service quality with adequate coverage</li>
            </ul>
          </div>
        )
      },
      reassignTasks: {
        title: 'Reassign Staff to Productive Tasks',
        content: (
          <div>
            <div style={{ marginBottom: '1rem' }}>
              <h4>Alternative to early release:</h4>
              <ul>
                <li>Deep cleaning: Prep area sanitization</li>
                <li>Inventory prep: Tomorrow's mise en place</li>
                <li>Cross-training: Learn new station skills</li>
                <li>Maintenance: Equipment cleaning and checks</li>
              </ul>
            </div>
            <p><strong>Productivity assignments:</strong></p>
            <ul>
              <li>Alex → Deep clean wok stations (1 hour task)</li>
              <li>Sam → Prep vegetables for tomorrow morning</li>
              <li>Lisa → Train on expediting station</li>
            </ul>
            <p><strong>Value:</strong> Maintain labor hours while maximizing productivity</p>
          </div>
        )
      },
      requestTransfer: {
        title: 'Emergency Store Transfer Request',
        content: (
          <div>
            <div style={{ marginBottom: '1rem' }}>
              <h4>Nearby stores with Beijing Beef availability:</h4>
              <ul>
                <li>Store #1248 (Westfield Mall - East): 47 portions available</li>
                <li>Store #1251 (Downtown Plaza): 23 portions available</li>
                <li>Store #1244 (Valley Center): 31 portions available</li>
              </ul>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label><strong>Request from:</strong></label>
              <select style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}>
                <option>Store #1248 - 15 portions (10 min drive)</option>
                <option>Store #1251 - 20 portions (15 min drive)</option>
                <option>Store #1244 - 25 portions (20 min drive)</option>
              </select>
            </div>
            <p><strong>Process:</strong> Driver dispatched immediately, ETA 25 minutes</p>
            <p><strong>Cost:</strong> $12 transfer fee vs $180 lost sales</p>
          </div>
        )
      },
      removeItem: {
        title: '86 Beijing Beef Early',
        content: (
          <div>
            <div style={{ marginBottom: '1rem' }}>
              <h4>Proactive menu management:</h4>
              <ul>
                <li>Remove Beijing Beef from POS at 5:00 PM</li>
                <li>Update menu boards to show "Limited Time"</li>
                <li>Train staff on alternative suggestions</li>
              </ul>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <h4>Suggested alternatives to offer:</h4>
              <ul>
                <li>Mushroom Chicken (similar flavor profile)</li>
                <li>Orange Chicken (most popular backup)</li>
                <li>Honey Walnut Shrimp (premium upgrade)</li>
              </ul>
            </div>
            <p><strong>Customer impact:</strong> Prevents disappointment, maintains service quality</p>
            <p><strong>Revenue protection:</strong> Redirect sales to available items</p>
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
    if (action === 'reduceBatch') {
      const newOperation = {
        id: Date.now(),
        name: "Reduced Orange Chicken Batch Size",
        status: "In Progress",
        initiated: new Date(),
        type: "Batch Optimization",
        impact: "Reduce waste by 15-20%",
        expectedCompletion: "Next batch"
      };
      setActiveOperations(prev => [...prev, newOperation]);
    }

    if (action === 'earlyRelease') {
      const newOperation = {
        id: Date.now(),
        name: "Early Release - Alex & Sam",
        status: "In Progress",
        initiated: new Date(),
        type: "Labor Adjustment",
        impact: "Save $67 in labor costs",
        expectedCompletion: "3:00 PM"
      };
      setActiveOperations(prev => [...prev, newOperation]);
    }

    setActiveModal(null);
  };

  const isActionCompleted = (cardId, action) => {
    return completedActions.has(`${cardId}-${action}`);
  };

  return (
    <div className="operations-brief">
      <div className="section-header">
        <h2>Daily Operations Brief</h2>
        <div className="section-header-meta">
          <span className="timestamp">
            <Clock size={16} />
            Live updates
          </span>
          <button className="refresh-btn">
            <TrendingUp size={16} />
            Refresh
          </button>
        </div>
      </div>

      <div className="intelligence-grid">
        {operationsCards.map((card) => {
          const IconComponent = card.icon;
          
          return (
            <div key={card.id} className={`intelligence-card ${card.type} priority-${card.priority}`}>
              <div className="card-header">
                <div className="card-icon" style={{ color: getPriorityColor(card.priority) }}>
                  <IconComponent size={24} />
                </div>
                <div className="card-meta">
                  <span className="card-type">{card.type.toUpperCase()}</span>
                  <span className="card-timestamp">{formatTimestamp(card.timestamp)}</span>
                </div>
              </div>

              <div className="card-content">
                <h3 className="card-title">{card.title}</h3>
                <p className="card-description">{card.description}</p>
                
                <div className="card-metric">
                  <span className="metric-value">{card.metric}</span>
                  <span className="metric-label">{card.metricLabel}</span>
                </div>

                <div className="card-recommendation">
                  <strong>Action:</strong> {card.recommendation}
                </div>
                
                <div className="card-source">
                  <strong>Data Source:</strong> {card.dataSource}
                </div>
              </div>

              <div className="card-actions">
                {card.actions.map((action, index) => {
                  const isCompleted = isActionCompleted(card.id, action.action);
                  return (
                    <button 
                      key={index}
                      className={`action-btn ${action.type} ${isCompleted ? 'completed' : ''}`}
                      onClick={() => handleAction(action.action, card.id)}
                      disabled={isCompleted}
                    >
                      {isCompleted ? <CheckCircle size={14} /> : <ArrowRight size={14} />}
                      {isCompleted ? 'Completed' : action.label}
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {/* Active Operations Tracker */}
      {activeOperations.length > 0 && (
        <div className="active-operations">
          <h3>🔄 Active Operations</h3>
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
                    <span className="operation-impact">Impact: {operation.impact}</span>
                    <span className="operation-completion">Complete by: {operation.expectedCompletion}</span>
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
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
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
                Execute Action
              </button>
              <button className="modal-btn secondary" onClick={closeModal}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DailyOperationsBrief;