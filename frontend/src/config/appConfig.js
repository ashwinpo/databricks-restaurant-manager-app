// Panda Restaurant Group Application Configuration
export const appConfig = {
  // API Configuration
  api: {
    // In production (Databricks Apps), use relative URLs since frontend and backend are served from same domain
    // In development, proxy to localhost backend
    baseUrl: import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? "http://localhost:8000" : ""),
    endpoints: {
      health: "/api/health",
      genie: "/api/genie/ask",
      monthlyData: "/api/data/monthly-summary",
      storeData: "/api/data/store-summary", 
      topStores: "/api/data/top-stores",
      kpis: "/api/analytics/kpis",
      alerts: "/api/operations/alerts",
      sqlQuery: "/api/db/query",
      upload: "/api/data/upload"
    },
    timeout: 30000 // 30 seconds for restaurant operations
  },
  
  // Company branding
  company: {
    name: "Panda Restaurant Group",
    logo: "/logos/panda-logo.png",
    favicon: "/vite.svg"
  },
  
  // Store manager persona
  persona: {
    name: "Sarah Chen", 
    title: "General Manager",
    store: "Panda Express #1619",
    location: "Westfield Mall"
  },
  
  // Panda brand theme colors
  theme: {
    // Primary Panda colors
    primary: "#d12a2f", // Panda Red
    primaryHover: "#b8242a",
    primaryLight: "#fef2f2",
    
    // Secondary colors
    secondary: "#0A1B22", // Panda Black
    secondaryLight: "#f8fafc",
    
    // Success/positive (for good metrics)
    success: "#059669", // Green
    successLight: "#d1fae5",
    
    // Warning/attention (for alerts)
    warning: "#d97706", // Orange
    warningLight: "#fed7aa",
    
    // Error/urgent (for critical issues)
    error: "#dc2626", // Red
    errorLight: "#fee2e2",
    
    // Neutral colors
    gray50: "#f9fafb",
    gray100: "#f3f4f6",
    gray200: "#e5e7eb",
    gray300: "#d1d5db",
    gray400: "#9ca3af",
    gray500: "#6b7280",
    gray600: "#4b5563",
    gray700: "#374151",
    gray800: "#1f2937",
    gray900: "#111827",
    
    // Background and surfaces (iPad-friendly)
    background: "#ffffff",
    surface: "#ffffff",
    surfaceHover: "#f9fafb",
    
    // iPad-specific colors
    ipadBorder: "#e5e7eb",
    ipadShadow: "rgba(0, 0, 0, 0.1)"
  },
  
  // Restaurant dashboard configuration
  dashboard: {
    // Daily operations brief settings
    operationsBrief: {
      maxCards: 3,
      refreshInterval: 60000, // 1 minute for restaurant operations
      showTimestamp: true
    },
    
    // Chart settings optimized for restaurant data
    charts: {
      animationDuration: 300,
      showGridLines: true,
      defaultHeight: 280, // Shorter for iPad landscape
      colors: {
        labor: "#d12a2f",
        food: "#059669", 
        sales: "#2563eb",
        margin: "#7c3aed"
      }
    },
    
    // Genie chat settings for Store 1619 P&L analysis
    genie: {
      maxHistory: 30, // Shorter for restaurant context
      placeholder: "Ask about Store 1619 P&L performance, cost analysis, or operational insights...",
      suggestedQuestions: [
        "Show me Store 1619's COGS breakdown by food category for period 202507",
        "What are the biggest expense variances for Store 1619 in the current period?",
        "Analyze Store 1619's labor cost structure - management vs hourly vs benefits",
        "Which line items had variance greater than 15% from plan for Store 1619?",
        "Show me Store 1619's digital vs traditional sales performance",
        "What's driving Store 1619's controllable profit variance from plan?"
      ]
    },
    
    // iPad-specific settings
    ipad: {
      cornerRadius: "12px",
      shadowDepth: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
      touchTargetSize: "44px", // Apple's recommended minimum
      fontSize: {
        large: "18px",
        medium: "16px", 
        small: "14px"
      }
    }
  }
};

// Function to apply theme colors as CSS custom properties
export const applyTheme = (theme) => {
  const root = document.documentElement;
  Object.entries(theme).forEach(([key, value]) => {
    root.style.setProperty(`--color-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`, value);
  });
};

// Function to get current config
export const getCurrentConfig = () => {
  return appConfig;
};

// Function to get current shift information (Panda Express mall hours: 10am-8pm)
export const getCurrentShift = () => {
  const hour = new Date().getHours();
  if (hour < 10) return { name: "Pre-Opening", period: "Prep Time" };
  if (hour >= 10 && hour < 12) return { name: "Morning", period: "10AM - 12PM" };
  if (hour >= 12 && hour < 14) return { name: "Lunch Rush", period: "12PM - 2PM" };
  if (hour >= 14 && hour < 17) return { name: "Afternoon", period: "2PM - 5PM" };
  if (hour >= 17 && hour < 20) return { name: "Dinner Rush", period: "5PM - 8PM" };
  return { name: "Closing", period: "8PM - Close" };
};
