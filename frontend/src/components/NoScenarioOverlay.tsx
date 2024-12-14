import React from 'react';
import { Box, Typography, Button, Paper, Grid } from '@mui/material';
import { styled } from '@mui/material/styles';
import { useNavigate } from 'react-router-dom';
import DirectionsCarIcon from '@mui/icons-material/DirectionsCar';
import PersonIcon from '@mui/icons-material/Person';

const PlaceholderCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  height: '200px',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  backgroundColor: 'rgba(255, 255, 255, 0.5)',
  border: '2px dashed rgba(0, 0, 0, 0.12)',
}));

const NoScenarioOverlay = () => {
  const navigate = useNavigate();
  
  return (
    <Box sx={{ width: '100%', height: '100%', position: 'relative' }}>
      {/* Placeholder content */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {[1, 2, 3, 4].map((item) => (
          <Grid item xs={12} sm={6} md={3} key={item}>
            <PlaceholderCard elevation={0}>
              {item % 2 === 0 ? (
                <DirectionsCarIcon sx={{ fontSize: 48, color: 'rgba(0, 0, 0, 0.2)', mb: 2 }} />
              ) : (
                <PersonIcon sx={{ fontSize: 48, color: 'rgba(0, 0, 0, 0.2)', mb: 2 }} />
              )}
              <Typography variant="body1" color="text.disabled">
                Placeholder Item {item}
              </Typography>
            </PlaceholderCard>
          </Grid>
        ))}
      </Grid>

      {/* Overlay content */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: 'rgba(255, 255, 255, 0.92)',
          backdropFilter: 'blur(4px)',
          zIndex: 1000,
        }}
      >
        <Box
          sx={{
            maxWidth: 450,
            textAlign: 'center',
            p: 4,
            borderRadius: 2,
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08)',
          }}
        >
          <Typography variant="h5" component="h2" gutterBottom fontWeight="500">
            No Active Scenario
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Start a new scenario in the Simulation page to see real-time data and manage your fleet.
          </Typography>
          <Button 
            variant="contained" 
            color="primary"
            size="large"
            onClick={() => navigate('/simulation')}
            sx={{
              px: 4,
              py: 1,
              borderRadius: 2,
              textTransform: 'none',
              fontSize: '1.1rem',
            }}
          >
            Start New Scenario
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default NoScenarioOverlay;
