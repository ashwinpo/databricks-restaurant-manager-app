import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Clock, BarChart3, Mic } from 'lucide-react';
import { apiService } from '../services/apiService.js';

const GenieChat = ({ config }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (message = inputValue) => {
    if (!message.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Call the real FastAPI backend with Genie integration
      const response = await apiService.askGenie(message, "I am a restaurant manager looking for operational insights");

      const genieMessage = {
        id: Date.now() + 1,
        type: 'genie',
        content: response.answer,
        sql: response.sql,
        data: response.data,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, genieMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Enhanced error information for debugging
      let errorDetails = error.message;
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        errorDetails = `Network error - unable to connect to backend. Check if the backend is running and CORS is configured correctly. Error: ${error.message}`;
      } else if (error.message.includes('HTTP 500')) {
        errorDetails = `Server error - check backend logs for details. Error: ${error.message}`;
      } else if (error.message.includes('HTTP 404')) {
        errorDetails = `API endpoint not found - check backend configuration. Error: ${error.message}`;
      }
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'genie',
        content: `Sorry, I encountered an error: ${errorDetails}. Please check the browser console for more details.`,
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Simulate restaurant-specific Genie responses
  const simulateRestaurantGenieResponse = async (question) => {
    await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate API delay

    const lowerQuestion = question.toLowerCase();
    
    if (lowerQuestion.includes('labor') && lowerQuestion.includes('sales')) {
      return {
        answer: "Today's labor is running at 34.2% vs your 30% target, while sales are at $2,847 (11% behind forecast). With light dinner traffic expected, I recommend releasing 2 team members at 3 PM to bring labor down to 32.7%. This would save $47 and better align with your sales pace.",
        sql: "SELECT labor_percent, sales_actual, sales_forecast, team_count FROM daily_operations WHERE date = CURRENT_DATE",
        data: {
          columns: ["Metric", "Current", "Target", "Variance"],
          rows: [
            {"Metric": "Labor %", "Current": "34.2%", "Target": "30.0%", "Variance": "+4.2%"},
            {"Metric": "Sales Pace", "Current": "$2,847", "Target": "$3,200", "Variance": "-11.0%"},
            {"Metric": "Team Size", "Current": "6", "Target": "4-5", "Variance": "+1-2"}
          ]
        }
      };
    }
    
    if (lowerQuestion.includes('orange chicken')) {
      return {
        answer: "Orange Chicken inventory shows 42 portions remaining. Based on the last 3 Tuesdays, you typically sell 65 portions by closing. Current sales pace is 8 portions/hour. At this rate, you'll run short by 6 PM. Historical data shows 85% probability of stockout without action.",
        sql: "SELECT item_name, current_inventory, avg_daily_sales, current_pace, predicted_shortfall FROM inventory_analysis WHERE item_name = 'Orange Chicken' AND day_of_week = 'Tuesday'",
        data: {
          columns: ["Time", "Projected Sales", "Remaining", "Status"],
          rows: [
            {"Time": "3:00 PM", "Projected Sales": "16", "Remaining": "26", "Status": "OK"},
            {"Time": "4:00 PM", "Projected Sales": "24", "Remaining": "18", "Status": "Low"},
            {"Time": "5:00 PM", "Projected Sales": "32", "Remaining": "10", "Status": "Critical"},
            {"Time": "6:00 PM", "Projected Sales": "40", "Remaining": "2", "Status": "Empty Soon"}
          ]
        }
      };
    }
    
    if (lowerQuestion.includes('margin') || lowerQuestion.includes('push')) {
      return {
        answer: "To hit your 70% margin target, focus on Mushroom Chicken (72% margin) over Orange Chicken (65% margin). You need 23 more Mushroom Chicken sales today. I recommend updating POS prompts and briefing the team. Beijing Beef is also a good alternative at 68% margin.",
        sql: "SELECT item_name, margin_percent, sales_today, sales_needed FROM menu_analysis WHERE margin_percent > 68 ORDER BY margin_percent DESC",
        data: {
          columns: ["Item", "Margin %", "Sales Today", "Potential Impact"],
          rows: [
            {"Item": "Mushroom Chicken", "Margin %": "72%", "Sales Today": "12", "Potential Impact": "+$156"},
            {"Item": "Beijing Beef", "Margin %": "68%", "Sales Today": "18", "Potential Impact": "+$98"},
            {"Item": "Orange Chicken", "Margin %": "65%", "Sales Today": "45", "Potential Impact": "Current focus"},
            {"Item": "Honey Walnut Shrimp", "Margin %": "75%", "Sales Today": "8", "Potential Impact": "+$187"}
          ]
        }
      };
    }
    
    if (lowerQuestion.includes('food cost') || lowerQuestion.includes('high')) {
      return {
        answer: "This week's food cost spike is primarily due to Chow Mein waste - up 200% vs average. Root cause: Alex has been over-prepping morning batches on Tue-Thu shifts. This pattern costs $340 weekly if continued. Schedule a 15-minute training session on batch sizes and set prep timer alerts.",
        sql: "SELECT item_name, waste_amount, waste_cost, root_cause FROM waste_analysis WHERE week = CURRENT_WEEK ORDER BY waste_cost DESC",
        data: {
          columns: ["Item", "Waste Amount", "Cost Impact", "Pattern"],
          rows: [
            {"Item": "Chow Mein", "Waste Amount": "12 lbs", "Cost Impact": "$68", "Pattern": "Tue-Thu AM"},
            {"Item": "Fried Rice", "Waste Amount": "8 lbs", "Cost Impact": "$32", "Pattern": "Weekend"},
            {"Item": "Orange Chicken", "Waste Amount": "6 lbs", "Cost Impact": "$28", "Pattern": "Monday"},
            {"Item": "Beijing Beef", "Waste Amount": "4 lbs", "Cost Impact": "$22", "Pattern": "Random"}
          ]
        }
      };
    }

    if (lowerQuestion.includes('team') || lowerQuestion.includes('productive')) {
      return {
        answer: "Today's productivity leaders are María (Kitchen, 125% efficiency) and Josh (Front, 118% efficiency). Alex and Sam are at 85% and 88% respectively - good candidates for early release. Lisa is at 110% and crucial for dinner prep. Consider keeping your top performers and releasing lower productivity team members during slow periods.",
        sql: "SELECT employee_name, position, efficiency_score, hours_today FROM team_performance WHERE date = CURRENT_DATE ORDER BY efficiency_score DESC",
        data: {
          columns: ["Employee", "Position", "Efficiency", "Hours Today"],
          rows: [
            {"Employee": "María", "Position": "Kitchen", "Efficiency": "125%", "Hours Today": "6.5"},
            {"Employee": "Josh", "Position": "Front", "Efficiency": "118%", "Hours Today": "5.0"},
            {"Employee": "Lisa", "Position": "Kitchen", "Efficiency": "110%", "Hours Today": "4.5"},
            {"Employee": "Sam", "Position": "Front", "Efficiency": "88%", "Hours Today": "5.5"},
            {"Employee": "Alex", "Position": "Kitchen", "Efficiency": "85%", "Hours Today": "6.0"}
          ]
        }
      };
    }

    // Default response for other questions
    return {
      answer: "I can help you analyze labor costs, food costs, sales performance, inventory levels, team productivity, and menu optimization. Try asking me about specific metrics like 'How are we tracking on labor vs sales today?' or 'What should we push to hit our margin target?'",
      sql: null,
      data: null
    };
  };

  const handleSuggestedQuestion = (question) => {
    handleSendMessage(question);
  };

  const formatTimestamp = (timestamp) => {
    return timestamp.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const cleanResponseText = (text) => {
    if (!text) return '';
    
    // Check if the text is mostly a markdown table (contains | and multiple lines with |)
    const lines = text.split('\n');
    const tableLines = lines.filter(line => line.includes('|'));
    const isMainlyTable = tableLines.length > 2 && tableLines.length / lines.length > 0.6;
    
    if (isMainlyTable) {
      // Extract any non-table text (usually at the beginning or end)
      const nonTableLines = lines.filter(line => 
        !line.includes('|') && 
        !line.match(/^\s*[-:]+\s*$/) && // Remove table separator lines
        line.trim().length > 0
      );
      
      if (nonTableLines.length > 0) {
        return nonTableLines.join(' ').trim();
      } else {
        // If there's no natural language text, return empty string
        // The table will be displayed separately
        return '';
      }
    }
    
    return text.trim();
  };

  const renderTable = (data) => {
    if (!data || !data.rows || data.rows.length === 0) return null;

    // Filter out index columns like "Unnamed: 0", "index", etc.
    const filteredColumns = data.columns.filter(col => 
      !col.toLowerCase().startsWith('unnamed') && 
      !col.toLowerCase().startsWith('index') &&
      col.toLowerCase() !== 'level_0'
    );
    
    if (filteredColumns.length === 0) return null;

    const maxRows = 10;
    const displayRows = data.rows.slice(0, maxRows);

    return (
      <div className="genie-table-container">
        <div className="genie-table">
          <table>
            <thead>
              <tr>
                {filteredColumns.map(col => (
                  <th key={col}>{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {displayRows.map((row, idx) => (
                <tr key={idx}>
                  {filteredColumns.map(col => (
                    <td key={col}>
                      {typeof row[col] === 'number' && !isNaN(row[col]) 
                        ? row[col].toLocaleString() 
                        : String(row[col] || '')
                      }
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {data.rows.length > maxRows && (
          <div className="table-truncated">
            Showing {maxRows} of {data.rows.length} rows
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="genie-chat">
      <div className="chat-header">
        <div className="chat-title">
          <Sparkles size={24} />
          <h3>Ask Genie</h3>
        </div>
        <div className="chat-subtitle">
          Get instant insights about your restaurant's P&L performance
        </div>
      </div>

      {messages.length === 0 && (
        <div className="chat-welcome">
          <div className="welcome-content">
            <div className="suggested-questions">
              <h5>Try asking:</h5>
              {config.dashboard.genie.suggestedQuestions.slice(0, 3).map((question, index) => (
                <button
                  key={index}
                  className="suggested-question"
                  onClick={() => handleSuggestedQuestion(question)}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="chat-messages">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className="message-header">
              <div className="message-sender">
                {message.type === 'user' ? 'You' : 'Genie'}
                {message.type === 'genie' && <Sparkles size={14} />}
              </div>
              <div className="message-time">
                <Clock size={12} />
                {formatTimestamp(message.timestamp)}
              </div>
            </div>
            
            <div className={`message-content ${message.isError ? 'error' : ''}`}>
              {(() => {
                const cleanedText = cleanResponseText(message.content);
                if (cleanedText) {
                  return cleanedText;
                } else if (message.data && message.data.rows && message.data.rows.length > 0) {
                  // If there's no natural language text but there's data, show a generic message
                  return "Here are the results from your query:";
                } else {
                  return message.content || '';
                }
              })()}
            </div>

            {message.sql && (
              <div className="message-sql">
                <div className="sql-header">
                  <BarChart3 size={14} />
                  Generated SQL Query:
                </div>
                <code className="sql-code">{message.sql}</code>
              </div>
            )}

            {message.data && renderTable(message.data)}
          </div>
        ))}
        
        {isLoading && (
          <div className="message genie loading">
            <div className="message-header">
              <div className="message-sender">
                Genie
                <Sparkles size={14} />
              </div>
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
              Analyzing your restaurant data...
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <div className="input-container">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder={config.dashboard.genie.placeholder}
            disabled={isLoading}
          />
          <button className="voice-input-btn" title="Voice input (coming soon)">
            <Mic size={16} />
          </button>
          <button 
            onClick={() => handleSendMessage()}
            disabled={!inputValue.trim() || isLoading}
            className="send-button"
          >
            <Send size={16} />
          </button>
        </div>
        
        {messages.length > 0 && config.dashboard.genie.suggestedQuestions.length > 0 && (
          <div className="quick-questions">
            {config.dashboard.genie.suggestedQuestions.slice(-2).map((question, index) => (
              <button
                key={index}
                className="quick-question"
                onClick={() => handleSuggestedQuestion(question)}
                disabled={isLoading}
              >
                {question}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default GenieChat;
