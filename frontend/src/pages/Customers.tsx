import React, { useEffect, useState } from 'react';
import { Grid, Card, Container, styled, Typography, Box } from '@mui/material';
import { keyframes } from '@mui/material/styles';
import { Customer, MapState, mapService } from '../services/mapService';
import { useScenario } from '../context/ScenarioContext';
import NoScenarioOverlay from '../components/NoScenarioOverlay';

// Import default customer images
const defaultCustomerImages = {
  'Alice': require('../assets/Alice.webp'),
  'Bob': require('../assets/Bob.webp'),
  'Carol': require('../assets/Carol.webp'),
  'David': require('../assets/David.webp'),
  'Eve': require('../assets/Eve.webp'),
};

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
    box-shadow: 0 0 0 10px rgba(0, 0, 0, 0);
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

const CustomerImage = styled('img')({
  width: '80px',
  height: '80px',
  objectFit: 'cover',
  borderRadius: '50%',
});

const StatusDot = styled('div')<{ status: boolean }>(({ status, theme }) => ({
  width: '12px',
  height: '12px',
  borderRadius: '50%',
  position: 'absolute',
  top: '16px',
  right: '16px',
  animation: `${pulse} 2s infinite`,
  backgroundColor: status ? '#2196F3' : '#4CAF50',
}));

const Customers = () => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [errorCount, setErrorCount] = useState(0);
  const { scenarioId } = useScenario();

  useEffect(() => {
    if (!scenarioId) return;

    const fetchCustomers = async () => {
      try {
        const state = await mapService.getMapState(scenarioId);
        if (state.status === 'error') {
          setErrorCount(prev => prev + 1);
          console.warn('Customer state update failed:', state.message);
        } else {
          setErrorCount(0);
          setCustomers(state.customers);
        }
      } catch (error) {
        console.error('Failed to fetch customers:', error);
        setErrorCount(prev => prev + 1);
      }
    };

    fetchCustomers();
    const interval = setInterval(fetchCustomers, 2000);
    return () => clearInterval(interval);
  }, [scenarioId]);

  const getCustomerImage = (fakeName: string) => {
    try {
      // First try to get from predefined images
      const image = defaultCustomerImages[fakeName as keyof typeof defaultCustomerImages];
      if (image) return image;

      // If not found, try to load dynamically
      return require(`../assets/${fakeName}.webp`);
    } catch (error) {
      console.warn(`Could not load image for customer ${fakeName}`, error);
      return defaultCustomerImages.Alice; // Use Alice as fallback
    }
  };

  return (
    <Container maxWidth="xl" sx={{ position: 'relative' }}>
      {!scenarioId && <NoScenarioOverlay />}
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
        {customers && customers.length > 0 ? customers.map((customer) => (
          <Grid item xs={12} sm={6} md={3} key={customer.id}>
            <StyledCard>
              <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                <CustomerImage 
                  src={getCustomerImage(customer.fake_name)} 
                  alt={customer.fake_name}
                  onError={(e: React.SyntheticEvent<HTMLImageElement, Event>) => {
                    const img = e.target as HTMLImageElement;
                    img.src = defaultCustomerImages.Alice;
                  }}
                />
                <Typography variant="h6" sx={{ position: 'absolute', left: '100px', top: '16px', maxWidth: '200px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {customer.fake_name}
                </Typography>
              </Box>

              <Box sx={{ mt: 'auto' }}>
                <Typography variant="body2" color="text.secondary">
                  Status: {customer.awaiting_service && !customer.picked_up ? 'Waiting for pickup' : customer.picked_up ? 'In transit' : 'Delivered'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Pickup: ({customer.latitude.toFixed(2)}, {customer.longitude.toFixed(2)})
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Destination: ({customer.destination_latitude.toFixed(2)}, {customer.destination_longitude.toFixed(2)})
                </Typography>
              </Box>

              <StatusDot status={customer.awaiting_service && !customer.picked_up} />
            </StyledCard>
          </Grid>
        )) : (
          <Grid item xs={12}>
            <Typography variant="h6" align="center">
              No customers available
            </Typography>
          </Grid>
        )}
      </Grid>
    </Container>
  );
};

export default Customers;
