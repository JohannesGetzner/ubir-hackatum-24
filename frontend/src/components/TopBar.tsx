import React from 'react';
import { AppBar, Toolbar, Typography, Box, useTheme } from '@mui/material';
import AutorenewIcon from '@mui/icons-material/Autorenew';
import DirectionsCarIcon from '@mui/icons-material/DirectionsCar';

const TopBar = () => {
  const theme = useTheme();
  const metrics = [
    { 
      label: 'Active Fleet', 
      value: '42', 
      color: 'success.main',
      icon: <DirectionsCarIcon sx={{ fontSize: 16 }} />
    },
    { 
      label: 'In Service', 
      value: '15', 
      color: 'warning.main',
      icon: <AutorenewIcon sx={{ fontSize: 16 }} />
    },
    { 
      label: 'Critical', 
      value: '3', 
      color: 'error.main',
      icon: <DirectionsCarIcon sx={{ fontSize: 16 }} />
    },
  ];

  return (
    <AppBar 
      position="fixed" 
      sx={{ 
        zIndex: (theme) => theme.zIndex.drawer + 1,
        background: 'linear-gradient(45deg, #ffffff 30%, #f8fafc 90%)',
      }}
    >
      <Toolbar sx={{ minHeight: { xs: '72px' } }}>
        {/* Logo */}
        <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
          <Typography 
            variant="h6" 
            noWrap 
            component="div"
            sx={{ 
              color: theme.palette.primary.main,
              fontWeight: 600,
              letterSpacing: '0.5px',
              display: 'flex',
              alignItems: 'center',
              gap: 1
            }}
          >
            <DirectionsCarIcon sx={{ fontSize: 28 }} />
            AutoFleet AI
          </Typography>
        </Box>

        {/* Metrics */}
        <Box sx={{ 
          display: 'flex', 
          gap: 2,
          my: -2,
          '& > div': {
            transition: 'transform 0.2s',
            '&:hover': {
              transform: 'translateY(-2px)',
            }
          }
        }}>
          {metrics.map((metric, index) => (
            <Box
              key={index}
              sx={{
                background: theme.palette.background.paper,
                borderRadius: 2,
                padding: '12px 20px',
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)',
                minWidth: 120,
                my: 2,
              }}
            >
              <Typography 
                variant="caption" 
                display="block" 
                sx={{ 
                  color: theme.palette.text.secondary,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 0.5,
                  mb: 0.5
                }}
              >
                {metric.icon}
                {metric.label}
              </Typography>
              <Typography 
                variant="h6" 
                sx={{ 
                  color: metric.color,
                  fontWeight: 600,
                  fontSize: '1.1rem'
                }}
              >
                {metric.value}
              </Typography>
            </Box>
          ))}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default TopBar;
