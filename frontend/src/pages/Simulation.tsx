import React, { useState, useEffect } from 'react';
import { Grid, Paper, TextField, Button, Box, Container, CircularProgress, Typography, TableContainer, Table, TableHead, TableBody, TableRow, TableCell, TableSortLabel } from '@mui/material';
import { styled, keyframes, alpha } from '@mui/material/styles';
import { TimePicker } from '@mui/x-date-pickers/TimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs from 'dayjs';
import sceneImage from '../assets/scene.png';
import { useScenario } from '../context/ScenarioContext';
import { ScenarioResponse, runScenario, getAllScenarios } from '../services/scenarioService';

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  alignItems: 'center',
}));

const pulse = keyframes`
  0% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(25, 118, 210, 0.7);
  }
  
  70% {
    transform: scale(1.05);
    box-shadow: 0 0 0 10px rgba(25, 118, 210, 0);
  }
  
  100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(25, 118, 210, 0);
  }
`;

const lightning = keyframes`
  0% {
    box-shadow: 0 0 5px #2196F3,
                0 0 10px #2196F3,
                0 0 20px #2196F3;
  }
  50% {
    box-shadow: 0 0 10px #21CBF3,
                0 0 20px #21CBF3,
                0 0 40px #21CBF3,
                0 0 80px #21CBF3;
  }
  100% {
    box-shadow: 0 0 5px #2196F3,
                0 0 10px #2196F3,
                0 0 20px #2196F3;
  }
`;

const electricPulse = keyframes`
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
`;

const rotatingLightning = keyframes`
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
`;

const lightningFlash = keyframes`
  0%, 100% {
    opacity: 0.3;
  }
  50% {
    opacity: 1;
  }
`;

const AnimatedButton = styled(Button)(({ theme }) => ({
  position: 'relative',
  '&.pulsing': {
    animation: `${pulse} 2s infinite`,
  },
  '&.loading': {
    '&::before, &::after': {
      content: '""',
      position: 'absolute',
      top: -2,
      left: -2,
      right: -2,
      bottom: -2,
      borderRadius: '50%',
      background: 'conic-gradient(from 0deg, transparent, transparent 45deg, #21CBF3 45deg, #21CBF3 90deg, transparent 90deg)',
      animation: `${rotatingLightning} 1s linear infinite, ${lightningFlash} 0.5s ease-in-out infinite`,
    },
    '&::after': {
      animation: `${rotatingLightning} 1s linear infinite reverse, ${lightningFlash} 0.5s ease-in-out infinite 0.25s`,
      background: 'conic-gradient(from 180deg, transparent, transparent 45deg, #2196F3 45deg, #2196F3 90deg, transparent 90deg)',
    },
    '& .lightning-arc': {
      position: 'absolute',
      top: -1,
      left: -1,
      right: -1,
      bottom: -1,
      borderRadius: '50%',
      border: '2px solid transparent',
      borderTopColor: '#21CBF3',
      borderRightColor: '#2196F3',
      animation: `${rotatingLightning} 2s linear infinite`,
      '&::before': {
        content: '""',
        position: 'absolute',
        top: '10%',
        left: '10%',
        right: '10%',
        bottom: '10%',
        borderRadius: '50%',
        border: '2px solid transparent',
        borderTopColor: '#2196F3',
        borderLeftColor: '#21CBF3',
        animation: `${rotatingLightning} 1.5s linear infinite reverse`,
      }
    }
  },
  '&:hover': {
    transform: 'scale(1.05)',
    transition: 'transform 0.2s ease-in-out',
  },
}));

interface KPIProps {
  label: string;
  value: number | null;
}

const KPIDisplay = ({ label, value }: KPIProps) => {
  if (value === null) {
    return (
      <Box sx={{ textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          {label}
        </Typography>
        <Typography 
          variant="h3" 
          sx={{ 
            color: 'text.secondary',
            fontWeight: 'bold',
          }}
        >
          -
        </Typography>
        <Typography 
          variant="subtitle1" 
          sx={{ 
            color: 'text.secondary',
            mt: 1
          }}
        >
          No data
        </Typography>
      </Box>
    );
  }

  const displayValue = `-${(Math.abs(value) * 100).toFixed(1)}%`;
  
  return (
    <Box sx={{ textAlign: 'center' }}>
      <Typography variant="h6" color="text.secondary" gutterBottom>
        {label}
      </Typography>
      <Typography 
        variant="h3" 
        sx={{ 
          color: 'success.main',
          fontWeight: 'bold',
        }}
      >
        {displayValue}
      </Typography>
      <Typography 
        variant="subtitle1" 
        sx={{ 
          color: 'success.main',
          mt: 1
        }}
      >
        Reduction
      </Typography>
    </Box>
  );
};

interface SimulationResult {
  id: number;
  fleetSize: number;
  customers: number;
  timeOfDay: string;
  breakdownRate: number;
  kmChange: number;
  waitingTimeChange: number;
}

const StyledTableRow = styled(TableRow)(({ theme }) => ({
  '&:nth-of-type(odd)': {
    backgroundColor: alpha(theme.palette.primary.main, 0.05),
  },
  '&:hover': {
    backgroundColor: alpha(theme.palette.primary.main, 0.1),
  },
  // hide last border
  '&:last-child td, &:last-child th': {
    border: 0,
  },
}));

const Simulation = () => {
  const [scenarios, setScenarios] = useState<ScenarioResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedTime, setSelectedTime] = useState(dayjs());
  const [numVehicles, setNumVehicles] = useState(5);
  const [numCustomers, setNumCustomers] = useState(10);
  const { setScenarioId } = useScenario();

  // Initial fetch of scenarios
  useEffect(() => {
    const fetchScenarios = async () => {
      try {
        const data = await getAllScenarios();
        // Sort scenarios by start_time in descending order (newest first)
        const sortedData = [...data].sort((a, b) => 
          new Date(b.start_time || 0).getTime() - new Date(a.start_time || 0).getTime()
        );
        setScenarios(sortedData);
        
        // Update KPIs based on the most recent scenario
        if (sortedData.length > 0) {
          const latestScenario = sortedData[0]; // First scenario is the most recent
          setKmChange(latestScenario.savings_km_genetic || null);
          setWaitingTimeChange(latestScenario.savings_time_genetic || null);
        }
      } catch (err) {
        setError('Failed to fetch scenarios');
        console.error('Error fetching scenarios:', err);
      }
    };

    fetchScenarios();
  }, []); // Empty dependency array means this runs once on mount

  // Poll for updates every 5 seconds
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const data = await getAllScenarios();
        // Sort scenarios by start_time in descending order (newest first)
        const sortedData = [...data].sort((a, b) => 
          new Date(b.start_time || 0).getTime() - new Date(a.start_time || 0).getTime()
        );
        setScenarios(sortedData);
        
        // Update KPIs based on the most recent scenario
        if (sortedData.length > 0) {
          const latestScenario = sortedData[0]; // First scenario is the most recent
          setKmChange(latestScenario.savings_km_genetic || null);
          setWaitingTimeChange(latestScenario.savings_time_genetic || null);
        }
      } catch (err) {
        console.error('Error polling scenarios:', err);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const result = await runScenario(numCustomers, numVehicles, 0.1);
      setScenarioId(result.scenario_id);
      
      // Immediately fetch updated scenarios after running
      const updatedScenarios = await getAllScenarios();
      setScenarios(updatedScenarios);
    } catch (err) {
      setError('Failed to run scenario');
      console.error('Error running scenario:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClick = () => {
    if (loading) return;
    handleSubmit({ preventDefault: () => {} } as React.FormEvent);
  };

  // Initial KPI values set to null
  const [kmChange, setKmChange] = useState<number | null>(null);
  const [waitingTimeChange, setWaitingTimeChange] = useState<number | null>(null);

  return (
    <Container maxWidth="xl">
      {/* First row with two equal columns */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={6}>
          <Paper elevation={3} sx={{ height: '100%' }}>
            <Box p={2}>
              <h2 style={{ marginTop: 0, marginBottom: '16px' }}>Parameters</h2>
              <form onSubmit={handleSubmit}>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      label="Fleet Size"
                      variant="outlined"
                      margin="normal"
                      type="number"
                      value={numVehicles}
                      onChange={(e) => setNumVehicles(parseInt(e.target.value) || 5)}
                      InputProps={{ inputProps: { min: 1 } }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      label="Number of Customers"
                      variant="outlined"
                      margin="normal"
                      type="number"
                      value={numCustomers}
                      onChange={(e) => setNumCustomers(parseInt(e.target.value) || 10)}
                      InputProps={{ inputProps: { min: 1 } }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <LocalizationProvider dateAdapter={AdapterDayjs}>
                      <TimePicker
                        label="Time of Day"
                        value={selectedTime}
                        onChange={(newValue) => setSelectedTime(newValue || dayjs())}
                        sx={{ width: '100%', mt: 2, mb: 1 }}
                      />
                    </LocalizationProvider>
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      label="Vehicle Breakdown Rate"
                      variant="outlined"
                      margin="normal"
                      type="number"
                      InputProps={{
                        inputProps: { 
                          min: 0,
                          max: 100,
                          step: 0.1
                        },
                        endAdornment: '%'
                      }}
                    />
                  </Grid>
                </Grid>
              </form>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={6}>
          <Paper elevation={3} sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Box sx={{ position: 'relative', display: 'inline-flex' }}>
              <CircularProgress
                variant="determinate"
                value={0}
                size={140}
                thickness={4}
                sx={{
                  position: 'absolute',
                  top: -10,
                  left: -10,
                  zIndex: 1,
                }}
              />
              <AnimatedButton 
                variant="contained" 
                size="large"
                onClick={handleClick}
                disabled={loading}
                className={loading ? 'loading' : 'pulsing'}
                sx={{
                  borderRadius: '50%',
                  width: 120,
                  height: 120,
                  minWidth: 120,
                  padding: 0,
                  fontSize: '1.5rem',
                  textTransform: 'none',
                  zIndex: 2,
                  background: loading ? 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)' : 'linear-gradient(45deg, #1976d2 30%, #42a5f5 90%)',
                  transition: 'all 0.3s ease',
                  overflow: 'visible',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #1976d2 30%, #42a5f5 90%)',
                    transform: loading ? 'none' : 'scale(1.05)',
                  },
                  '&:active': {
                    transform: loading ? 'none' : 'scale(0.95)',
                  }
                }}
              >
                <div className="lightning-arc" />
                {loading ? (
                  <Typography 
                    variant="h4" 
                    sx={{ 
                      color: 'white',
                      textShadow: '0 0 10px rgba(255,255,255,0.8)',
                    }}
                  >
                    {`${0}%`}
                  </Typography>
                ) : (
                  <Box
                    component="img"
                    src={sceneImage}
                    alt="Run Simulation"
                    sx={{
                      width: '80%',
                      height: '80%',
                      objectFit: 'contain',
                      filter: 'brightness(0) invert(1)', // Makes the image white
                    }}
                  />
                )}
              </AnimatedButton>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Results section */}
      <Box sx={{ mt: 3 }}>
        <Paper elevation={3} sx={{ p: 2 }}>
          <h2 style={{ marginTop: 0, marginBottom: '16px' }}>Simulation Results</h2>
          
          {/* Latest result section */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 1.5, display: 'flex', alignItems: 'center' }}>
              Last Run • <Typography component="span" color="text.primary" sx={{ ml: 1, fontWeight: 'medium' }}>
                {dayjs().format('MMM D, YYYY HH:mm')}
              </Typography>
            </Typography>
            
            <Grid container justifyContent="center" spacing={2}>
              <Grid item xs={3}>
                <Paper elevation={2} sx={{ 
                  height: '100%',
                  background: (theme) => theme.palette.background.default,
                }}>
                  <Box p={1.5}>
                    <KPIDisplay 
                      label="Total Distance" 
                      value={kmChange}
                    />
                  </Box>
                </Paper>
              </Grid>
              <Grid item xs={3}>
                <Paper elevation={2} sx={{ 
                  height: '100%',
                  background: (theme) => theme.palette.background.default,
                }}>
                  <Box p={1.5}>
                    <KPIDisplay 
                      label="Waiting Time" 
                      value={waitingTimeChange}
                    />
                  </Box>
                </Paper>
              </Grid>
            </Grid>
          </Box>

          {/* Historical results section */}
          <Box>
            <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 1.5 }}>
              Historical Results
            </Typography>
            <TableContainer sx={{ maxHeight: 280 }}>
              <Table stickyHeader size="small" sx={{ minWidth: 650 }} aria-label="simulation results table">
                <TableHead>
                  <TableRow>
                    <TableCell>Scenario ID</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Start Time</TableCell>
                    <TableCell>End Time</TableCell>
                    <TableCell>Customers</TableCell>
                    <TableCell>Vehicles</TableCell>
                    <TableCell align="right">Distance Savings</TableCell>
                    <TableCell align="right">Time Savings</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {scenarios.map((scenario) => (
                    <StyledTableRow key={scenario.scenario_id}>
                      <TableCell>{scenario.scenario_id}</TableCell>
                      <TableCell>{scenario.status}</TableCell>
                      <TableCell>{scenario.start_time || '-'}</TableCell>
                      <TableCell>{scenario.end_time || '-'}</TableCell>
                      <TableCell>{scenario.num_customers || 'NaN'}</TableCell>
                      <TableCell>{scenario.num_vehicles || 'NaN'}</TableCell>
                      <TableCell 
                        align="right"
                        sx={{ 
                          color: 'success.main',
                          fontWeight: 'bold'
                        }}
                      >
                        {scenario.savings_km_genetic ? `-${(scenario.savings_km_genetic * 100).toFixed(1)}%` : 'NaN'}
                      </TableCell>
                      <TableCell 
                        align="right"
                        sx={{ 
                          color: 'success.main',
                          fontWeight: 'bold'
                        }}
                      >
                        {scenario.savings_time_genetic ? `-${(scenario.savings_time_genetic * 100).toFixed(1)}%` : 'NaN'}
                      </TableCell>
                    </StyledTableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Simulation;
