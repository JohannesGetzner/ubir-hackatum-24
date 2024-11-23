import React from 'react';
import { styled } from '@mui/material/styles';
import Switch from '@mui/material/Switch';
import { Box, Typography } from '@mui/material';
import { keyframes } from '@mui/system';
import { useOptimizationMode } from '../context/OptimizationModeContext';

const pulse = keyframes`
  0% {
    box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(255, 193, 7, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(255, 193, 7, 0);
  }
`;

const CustomSwitch = styled(Switch)(({ theme }) => ({
  width: 62,
  height: 34,
  padding: 7,
  '& .MuiSwitch-switchBase': {
    margin: 1,
    padding: 0,
    transform: 'translateX(6px)',
    '&.Mui-checked': {
      color: '#fff',
      transform: 'translateX(22px)',
      '& .MuiSwitch-thumb:before': {
        backgroundImage: `url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" height="20" width="20" viewBox="0 0 20 20"><path fill="${encodeURIComponent(
          '#fff',
        )}" d="M9.305 1.667V3.75h1.389V1.667h-1.39zm-4.707 1.95l-.982.982L5.09 6.072l.982-.982-1.473-1.473zm10.802 0L13.927 5.09l.982.982 1.473-1.473-.982-.982zM10 5.139a4.872 4.872 0 00-4.862 4.86A4.872 4.872 0 0010 14.862 4.872 4.872 0 0014.86 10 4.872 4.872 0 0010 5.139zm0 1.389A3.462 3.462 0 0113.471 10a3.462 3.462 0 01-3.473 3.472A3.462 3.462 0 016.527 10 3.462 3.462 0 0110 6.528zM1.665 9.305v1.39h2.083v-1.39H1.666zm14.583 0v1.39h2.084v-1.39h-2.084zM5.09 13.928L3.616 15.4l.982.982 1.473-1.473-.982-.982zm9.82 0l-.982.982 1.473 1.473.982-.982-1.473-1.473zM9.305 16.25v2.083h1.389V16.25h-1.39z"/></svg>')`,
      },
      '& + .MuiSwitch-track': {
        opacity: 1,
        backgroundColor: theme.palette.success.main,
      },
    },
  },
  '& .MuiSwitch-thumb': {
    backgroundColor: theme.palette.mode === 'dark' ? '#003892' : '#001e3c',
    width: 32,
    height: 32,
    '&:before': {
      content: "''",
      position: 'absolute',
      width: '100%',
      height: '100%',
      left: 0,
      top: 0,
      backgroundRepeat: 'no-repeat',
      backgroundPosition: 'center',
      backgroundImage: `url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" height="20" width="20" viewBox="0 0 24 24"><path fill="${encodeURIComponent(
        '#fff',
      )}" d="M11 21h-1l1-7H7.5c-.58 0-.57-.32-.38-.66.19-.34.05-.08.07-.12C8.48 10.94 10.42 7.54 13 3h1l-1 7h3.5c.49 0 .56.33.47.51l-.07.15C12.96 17.55 11 21 11 21z"/></svg>')`,
    },
  },
  '& .MuiSwitch-track': {
    opacity: 1,
    backgroundColor: theme.palette.warning.main,
    borderRadius: 20 / 2,
  },
}));

const OptimizationModeSwitch = () => {
  const { mode, setMode } = useOptimizationMode();

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setMode(event.target.checked ? 'sustainable' : 'performance');
  };

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1,
        ml: 2,
        '& .MuiSwitch-root': {
          animation: mode === 'performance' ? `${pulse} 2s infinite` : 'none',
        },
      }}
    >
      <Typography
        variant="body2"
        sx={{
          color: mode === 'performance' ? 'warning.main' : 'text.secondary',
          fontWeight: mode === 'performance' ? 600 : 400,
        }}
      >
        Performance
      </Typography>
      <CustomSwitch
        checked={mode === 'sustainable'}
        onChange={handleChange}
      />
      <Typography
        variant="body2"
        sx={{
          color: mode === 'sustainable' ? 'success.main' : 'text.secondary',
          fontWeight: mode === 'sustainable' ? 600 : 400,
        }}
      >
        Sustainable
      </Typography>
    </Box>
  );
};

export default OptimizationModeSwitch;
