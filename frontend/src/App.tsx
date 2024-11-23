import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { Box, CssBaseline, ThemeProvider } from '@mui/material';
import { theme } from './theme';
import TopBar from './components/TopBar';
import SideNav from './components/SideNav';
import Overview from './pages/Overview';
import Map from './pages/Map';
import Fleet from './pages/Fleet';
import Customers from './pages/Customers';
import Simulation from './pages/Simulation';
import { ScenarioProvider } from './context/ScenarioContext';
import { OptimizationModeProvider } from './context/OptimizationModeContext';

const SPACING = 2; // 16px in MUI spacing units
const SIDEBAR_WIDTH = 240;

const AppContent = () => {
  return (
    <Box sx={{ 
      display: 'flex',
      flexDirection: 'column',
      bgcolor: '#f0f2f5',
      minHeight: '100vh',
      p: SPACING
    }}>
      {/* Top Bar Container */}
      <Box sx={{ width: '100%', mb: SPACING }}>
        <TopBar spacing={SPACING} />
      </Box>

      {/* Main Content Area */}
      <Box sx={{ 
        display: 'flex',
        flex: 1,
        gap: SPACING
      }}>
        {/* Sidebar */}
        <Box sx={{ 
          width: SIDEBAR_WIDTH,
          flexShrink: 0
        }}>
          <SideNav spacing={SPACING} />
        </Box>

        {/* Page Content */}
        <Box sx={{ 
          flex: 1,
          overflow: 'hidden',
          borderRadius: 2
        }}>
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/map" element={<Map />} />
            <Route path="/fleet" element={<Fleet />} />
            <Route path="/customers" element={<Customers />} />
            <Route path="/simulation" element={<Simulation />} />
          </Routes>
        </Box>
      </Box>
    </Box>
  );
};

const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <OptimizationModeProvider>
        <ScenarioProvider>
          <Router>
            <AppContent />
          </Router>
        </ScenarioProvider>
      </OptimizationModeProvider>
    </ThemeProvider>
  );
};

export default App;
