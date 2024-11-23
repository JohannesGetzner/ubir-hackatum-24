import React, { useState } from 'react';
import { Grid, Paper, TextField, Button, Box, Container, CircularProgress, Typography, TableContainer, Table, TableHead, TableBody, TableRow, TableCell, TableSortLabel } from '@mui/material';
import { styled, keyframes, alpha } from '@mui/material/styles';
import { TimePicker } from '@mui/x-date-pickers/TimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs from 'dayjs';

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

const AnimatedButton = styled(Button)(({ theme }) => ({
  position: 'relative',
  '&.pulsing': {
    animation: `${pulse} 2s infinite`,
  },
  '&:hover': {
    transform: 'scale(1.05)',
    transition: 'transform 0.2s ease-in-out',
  },
}));

interface KPIProps {
  label: string;
  value: number;
}

const KPIDisplay = ({ label, value }: KPIProps) => {
  const isPositive = value > 0;
  const displayValue = `${(value * 100).toFixed(1)}%`;
  const color = isPositive ? '#d32f2f' : '#2e7d32'; // Red for positive (worse), Green for negative (better)
  
  return (
    <Box sx={{ textAlign: 'center' }}>
      <Typography variant="h6" color="text.secondary" gutterBottom>
        {label}
      </Typography>
      <Typography 
        variant="h3" 
        sx={{ 
          color,
          fontWeight: 'bold',
        }}
      >
        {displayValue}
      </Typography>
      <Typography 
        variant="subtitle1" 
        sx={{ 
          color: isPositive ? 'error.main' : 'success.main',
          mt: 1
        }}
      >
        {isPositive ? 'Increase' : 'Reduction'}
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

const mockResults: SimulationResult[] = [
  {
    id: 1,
    fleetSize: 50,
    customers: 200,
    timeOfDay: '08:00',
    breakdownRate: 0.05,
    kmChange: -0.4,
    waitingTimeChange: -0.15,
  },
  {
    id: 2,
    fleetSize: 40,
    customers: 180,
    timeOfDay: '12:00',
    breakdownRate: 0.1,
    kmChange: -0.35,
    waitingTimeChange: -0.2,
  },
  {
    id: 3,
    fleetSize: 60,
    customers: 250,
    timeOfDay: '17:00',
    breakdownRate: 0.08,
    kmChange: -0.25,
    waitingTimeChange: -0.1,
  },
  {
    id: 4,
    fleetSize: 45,
    customers: 190,
    timeOfDay: '14:30',
    breakdownRate: 0.15,
    kmChange: 0.1,
    waitingTimeChange: 0.05,
  },
  {
    id: 5,
    fleetSize: 55,
    customers: 220,
    timeOfDay: '09:30',
    breakdownRate: 0.07,
    kmChange: -0.3,
    waitingTimeChange: -0.18,
  },
  {
    id: 6,
    fleetSize: 48,
    customers: 195,
    timeOfDay: '13:15',
    breakdownRate: 0.12,
    kmChange: -0.22,
    waitingTimeChange: -0.08,
  },
  {
    id: 7,
    fleetSize: 52,
    customers: 210,
    timeOfDay: '16:45',
    breakdownRate: 0.06,
    kmChange: -0.38,
    waitingTimeChange: -0.25,
  },
  {
    id: 8,
    fleetSize: 42,
    customers: 175,
    timeOfDay: '11:20',
    breakdownRate: 0.09,
    kmChange: -0.15,
    waitingTimeChange: -0.12,
  },
  {
    id: 9,
    fleetSize: 58,
    customers: 240,
    timeOfDay: '15:00',
    breakdownRate: 0.11,
    kmChange: 0.05,
    waitingTimeChange: 0.08,
  },
  {
    id: 10,
    fleetSize: 44,
    customers: 185,
    timeOfDay: '10:45',
    breakdownRate: 0.13,
    kmChange: -0.28,
    waitingTimeChange: -0.16,
  },
  {
    id: 11,
    fleetSize: 53,
    customers: 215,
    timeOfDay: '18:30',
    breakdownRate: 0.04,
    kmChange: -0.42,
    waitingTimeChange: -0.22,
  },
  {
    id: 12,
    fleetSize: 46,
    customers: 188,
    timeOfDay: '07:15',
    breakdownRate: 0.14,
    kmChange: 0.08,
    waitingTimeChange: 0.03,
  }
];

const Simulation = () => {
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [selectedTime, setSelectedTime] = useState(dayjs());
  
  // Mock KPI values (will be replaced with actual data)
  const [kmChange, setKmChange] = useState(-0.4); // -40%
  const [waitingTimeChange, setWaitingTimeChange] = useState(-0.15); // -15%

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
  };

  const handleClick = () => {
    if (loading) return;
    
    setLoading(true);
    setProgress(0);

    const timer = setInterval(() => {
      setProgress((prevProgress) => {
        if (prevProgress >= 100) {
          clearInterval(timer);
          setLoading(false);
          return 100;
        }
        return prevProgress + 10;
      });
    }, 800);
  };

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
                value={progress}
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
                className={!loading ? 'pulsing' : ''}
                sx={{
                  borderRadius: '50%',
                  width: 120,
                  height: 120,
                  fontSize: '1.5rem',
                  textTransform: 'none',
                  zIndex: 2,
                  background: loading ? 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)' : 'linear-gradient(45deg, #1976d2 30%, #42a5f5 90%)',
                  boxShadow: loading ? '0 0 20px rgba(33, 203, 243, 0.5)' : 'none',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #1976d2 30%, #42a5f5 90%)',
                    transform: 'scale(1.05)',
                  },
                  '&:active': {
                    transform: 'scale(0.95)',
                  }
                }}
              >
                {loading ? `${progress}%` : 'Run'}
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
                    <TableCell>Fleet Size</TableCell>
                    <TableCell>Customers</TableCell>
                    <TableCell>Time of Day</TableCell>
                    <TableCell>Breakdown Rate</TableCell>
                    <TableCell align="right">Distance Change</TableCell>
                    <TableCell align="right">Waiting Time Change</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {mockResults.map((row) => (
                    <StyledTableRow key={row.id}>
                      <TableCell>{row.fleetSize}</TableCell>
                      <TableCell>{row.customers}</TableCell>
                      <TableCell>{row.timeOfDay}</TableCell>
                      <TableCell>{(row.breakdownRate * 100).toFixed(1)}%</TableCell>
                      <TableCell 
                        align="right"
                        sx={{ 
                          color: row.kmChange > 0 ? 'error.main' : 'success.main',
                          fontWeight: 'bold'
                        }}
                      >
                        {(row.kmChange * 100).toFixed(1)}%
                      </TableCell>
                      <TableCell 
                        align="right"
                        sx={{ 
                          color: row.waitingTimeChange > 0 ? 'error.main' : 'success.main',
                          fontWeight: 'bold'
                        }}
                      >
                        {(row.waitingTimeChange * 100).toFixed(1)}%
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
