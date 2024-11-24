import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { styled } from '@mui/material/styles';
import { useNavigate } from 'react-router-dom';

const OverlayContainer = styled(Box)(({ theme }) => ({
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  backgroundColor: 'rgba(255, 255, 255, 0.9)',
  zIndex: 1000,
  gap: theme.spacing(2),
}));

const NoScenarioOverlay = () => {
  const navigate = useNavigate();
  
  return (
    <OverlayContainer>
      <Typography variant="h5" component="h2" gutterBottom>
        No Active Scenario
      </Typography>
      <Typography variant="body1" color="text.secondary" align="center" sx={{ maxWidth: 400, mb: 2 }}>
        Start a new scenario in the Simulation page to see the fleet management overview.
      </Typography>
      <Button 
        variant="contained" 
        color="primary"
        size="large"
        onClick={() => navigate('/simulation')}
      >
        Start New Scenario
      </Button>
    </OverlayContainer>
  );
};

export default NoScenarioOverlay;
