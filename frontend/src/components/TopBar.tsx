import React from 'react';
import { Box, Toolbar, Typography, useTheme, Divider } from '@mui/material';
import AutorenewIcon from '@mui/icons-material/Autorenew';
import DirectionsCarIcon from '@mui/icons-material/DirectionsCar';
import PercentIcon from '@mui/icons-material/Percent';
import { useScenario } from '../context/ScenarioContext';
import OptimizationModeSwitch from './OptimizationModeSwitch';
import logo from '../assets/logo.png';

interface TopBarProps {
  spacing?: number;
}

const TopBar: React.FC<TopBarProps> = ({ spacing = 2 }) => {
  const theme = useTheme();
  const { utilization, efficiency } = useScenario();

  const formatPercentage = (value: number) => {
    return `${Math.round(value * 100)}%`;
  };

  const metrics = [
    { 
      label: 'Utilization', 
      value: formatPercentage(utilization), 
      color: 'success.main',
      icon: <PercentIcon sx={{ fontSize: 16 }} />
    },
    { 
      label: 'Efficiency', 
      value: formatPercentage(efficiency), 
      color: 'warning.main',
      icon: <PercentIcon sx={{ fontSize: 16 }} />
    }
  ];

  return (
    <Box
      sx={{
        borderRadius: '12px',
        background: 'linear-gradient(45deg, #ffffff 30%, #f8fafc 90%)',
        boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.05), 0px 4px 8px rgba(0, 0, 0, 0.08)',
      }}
    >
      <Toolbar sx={{ height: '72px', display: 'flex', alignItems: 'center', py: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
          <img 
            src={logo} 
            alt="Logo" 
            style={{ 
              height: '40px',
              marginRight: theme.spacing(2)
            }}
          />
        </Box>

        <Box sx={{ 
          display: 'flex', 
          gap: 3,
          height: '48px'
        }}>
          {metrics.map((metric, index) => (
            <React.Fragment key={metric.label}>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                }}
              >
                <Typography
                  variant="body2"
                  sx={{ color: 'text.secondary', fontWeight: 500 }}
                >
                  {metric.label}
                </Typography>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 0.5,
                    color: metric.color,
                    fontWeight: 600,
                  }}
                >
                  <Typography variant="body2" sx={{ fontWeight: 'inherit' }}>
                    {metric.value}
                  </Typography>
                  {metric.icon}
                </Box>
              </Box>
              {index < metrics.length - 1 && (
                <Divider orientation="vertical" flexItem sx={{ my: 2 }} />
              )}
            </React.Fragment>
          ))}
          <Divider orientation="vertical" flexItem sx={{ my: 2 }} />
          <OptimizationModeSwitch />
        </Box>
      </Toolbar>
    </Box>
  );
};

export default TopBar;
