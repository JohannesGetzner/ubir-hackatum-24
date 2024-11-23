import React, { useEffect, useState } from 'react';
import { Grid, Card, Container, styled, Typography, Box, keyframes } from '@mui/material';
import { Vehicle, MapState, mapService } from '../services/mapService';
import carImage from '../assets/car_a.png';

const StyledContainer = styled(Container)(({ theme }) => ({
  backgroundColor: 'white',
  height: '100%',
  borderRadius: '15px',
  overflow: 'auto',
  padding: theme.spacing(2),
  boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.1), 0px 8px 16px rgba(0, 0, 0, 0.1)',
}));

const pulse = keyframes`
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(0, 0, 0, 0.3);
  }
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 6px rgba(0, 0, 0, 0);
  }
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(0, 0, 0, 0);
  }
`;

const StyledCard = styled(Card)(({ theme }) => ({
  height: '200px',
  margin: theme.spacing(1),
  padding: theme.spacing(2),
  boxShadow: '0 3px 5px rgba(0, 0, 0, 0.1)',
  position: 'relative',
  display: 'flex',
  flexDirection: 'column',
}));

const CarImage = styled('img')({
  width: '80px',
  height: 'auto',
  objectFit: 'contain',
});

const StatusDot = styled('div')<{ status: 'idle' | 'cust' | 'dest' }>(({ status, theme }) => ({
  width: '12px',
  height: '12px',
  borderRadius: '50%',
  position: 'absolute',
  top: '16px',
  right: '16px',
  animation: `${pulse} 2s infinite`,
  backgroundColor: status === 'idle' 
    ? '#4CAF50' // green for idle
    : status === 'cust' 
    ? '#FFC107' // yellow for customer pickup
    : '#2196F3', // blue for destination
}));

const getStatusText = (status: 'idle' | 'cust' | 'dest'): string => {
  switch (status) {
    case 'idle': return 'Available';
    case 'cust': return 'Picking up customer';
    case 'dest': return 'En route to destination';
  }
};

const Fleet = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [errorCount, setErrorCount] = useState(0);

  useEffect(() => {
    const fetchVehicles = async () => {
      try {
        const state = await mapService.getMapState();
        if (state.status === 'error') {
          setErrorCount(prev => prev + 1);
          console.warn('Vehicle state update failed:', state.message);
        } else {
          setErrorCount(0);
          if (state.vehicles.length > 0) {
            setVehicles(state.vehicles);
          }
        }
      } catch (error) {
        console.error('Failed to fetch vehicles:', error);
        setErrorCount(prev => prev + 1);
      }
    };

    fetchVehicles();
    const interval = setInterval(fetchVehicles, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <StyledContainer maxWidth={false}>
      {errorCount > 0 && (
        <Box
          sx={{
            position: 'absolute',
            top: 16,
            right: 16,
            backgroundColor: 'rgba(255, 0, 0, 0.1)',
            color: 'red',
            padding: '8px 16px',
            borderRadius: '4px',
            zIndex: 1000,
            pointerEvents: 'none'
          }}
        >
          Connection issues. Using cached data...
        </Box>
      )}
      <Grid container spacing={2}>
        {vehicles.map((vehicle) => (
          <Grid item xs={12} sm={6} md={3} key={vehicle.id}>
            <StyledCard>
              <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                <CarImage src={carImage} alt="Vehicle" />
                <Typography variant="h6" sx={{ position: 'absolute', left: '100px', top: '16px' }}>
                  #{vehicle.id}
                </Typography>
              </Box>
              
              <Typography variant="body1" sx={{ mt: 2 }}>
                Model: Tesla Model S
              </Typography>

              <Box sx={{ mt: 'auto' }}>
                <Typography variant="body2" color="text.secondary">
                  Status: {getStatusText(vehicle.enroute)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Speed: {vehicle.vehicle_speed.toFixed(1)} km/h
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Trips: {vehicle.number_of_trips}
                </Typography>
              </Box>

              <StatusDot status={vehicle.enroute} />
            </StyledCard>
          </Grid>
        ))}
      </Grid>
    </StyledContainer>
  );
};

export default Fleet;
