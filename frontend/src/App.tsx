import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Box, CssBaseline, ThemeProvider } from '@mui/material';
import { theme } from './theme';
import TopBar from './components/TopBar';
import SideNav from './components/SideNav';
import Overview from './pages/Overview';
import Map from './pages/Map';
import Fleet from './pages/Fleet';
import Customers from './pages/Customers';
import Predictions from './pages/Predictions';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Router>
        <Box sx={{ display: 'flex', bgcolor: 'background.default', minHeight: '100vh' }}>
          <CssBaseline />
          <TopBar />
          <SideNav />
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              p: 3,
              width: { sm: `calc(100% - 240px)` },
              mt: 8,
              overflow: 'hidden',
            }}
          >
            <Routes>
              <Route path="/" element={<Overview />} />
              <Route path="/map" element={<Map />} />
              <Route path="/fleet" element={<Fleet />} />
              <Route path="/customers" element={<Customers />} />
              <Route path="/predictions" element={<Predictions />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
