import React, { useState } from 'react';
import { Grid, Paper, TextField, Button, Box, Container, CircularProgress } from '@mui/material';
import { styled, keyframes } from '@mui/material/styles';
import { TimePicker } from '@mui/x-date-pickers/TimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs from 'dayjs';

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  height: '100%',
}));

const pulse = keyframes`
  0% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(25, 118, 210, 0.4);
  }
  70% {
    transform: scale(1.05);
    box-shadow: 0 0 0 15px rgba(25, 118, 210, 0);
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

const Simulation = () => {
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [selectedTime, setSelectedTime] = useState(dayjs());

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
  };

  const handleClick = () => {
    setLoading(true);
    setProgress(0);
    
    // Simulate progress
    const interval = setInterval(() => {
      setProgress((prevProgress) => {
        const newProgress = prevProgress + 2;
        if (newProgress >= 100) {
          clearInterval(interval);
          setTimeout(() => {
            setLoading(false);
            setProgress(0);
          }, 500);
          return 100;
        }
        return newProgress;
      });
    }, 50);
  };

  return (
    <Container maxWidth="xl">
      {/* First row with two equal columns */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={6}>
          <Box p={2}>
            <h2>Parameters</h2>
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
                      onChange={(newValue) => setSelectedTime(newValue)}
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
        </Grid>
        <Grid item xs={6}>
          <Box p={2} sx={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center',
            height: '100%'
          }}>
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
                }}
              >
                {loading ? `${progress}%` : 'Run'}
              </AnimatedButton>
            </Box>
          </Box>
        </Grid>
      </Grid>

      {/* Second row with two centered small containers */}
      <Grid container justifyContent="center" spacing={3}>
        <Grid item xs={3}>
          <StyledPaper elevation={3}>
            <Box p={2}>
              <h3>Container 1</h3>
              {/* Add content for container 1 */}
            </Box>
          </StyledPaper>
        </Grid>
        <Grid item xs={3}>
          <StyledPaper elevation={3}>
            <Box p={2}>
              <h3>Container 2</h3>
              {/* Add content for container 2 */}
            </Box>
          </StyledPaper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Simulation;
