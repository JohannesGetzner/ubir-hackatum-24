import React from 'react';
import { 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText, 
  useTheme,
  Box,
  ListItemButton,
  Paper
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import DashboardIcon from '@mui/icons-material/Dashboard';
import MapIcon from '@mui/icons-material/Map';
import DirectionsCarIcon from '@mui/icons-material/DirectionsCar';
import PeopleIcon from '@mui/icons-material/People';
import TimelineIcon from '@mui/icons-material/Timeline';

interface SideNavProps {
  spacing?: number;
}

const menuItems = [
  { text: 'Overview', icon: <DashboardIcon />, path: '/' },
  { text: 'Map', icon: <MapIcon />, path: '/map' },
  { text: 'Fleet', icon: <DirectionsCarIcon />, path: '/fleet' },
  { text: 'Customers', icon: <PeopleIcon />, path: '/customers' },
  { text: 'Predictions', icon: <TimelineIcon />, path: '/predictions' },
];

const SideNav: React.FC<SideNavProps> = ({ spacing = 2 }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();

  return (
    <Paper
      elevation={0}
      sx={{
        borderRadius: '12px',
        background: 'linear-gradient(45deg, #ffffff 30%, #f8fafc 90%)',
        boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.1), 0px 8px 16px rgba(0, 0, 0, 0.1)',
        p: 2,
        height: '100%'
      }}
    >
      <List>
        {menuItems.map((item) => {
          const isSelected = location.pathname === item.path;
          return (
            <ListItem 
              key={item.text} 
              disablePadding
              sx={{ mb: 1 }}
            >
              <ListItemButton
                onClick={() => navigate(item.path)}
                selected={isSelected}
                sx={{
                  borderRadius: 2,
                  '&.Mui-selected': {
                    backgroundColor: theme.palette.primary.main + '15',
                    '&:hover': {
                      backgroundColor: theme.palette.primary.main + '25',
                    },
                    '& .MuiListItemIcon-root': {
                      color: theme.palette.primary.main,
                    },
                    '& .MuiListItemText-primary': {
                      color: theme.palette.primary.main,
                      fontWeight: 600,
                    },
                  },
                  '&:hover': {
                    backgroundColor: theme.palette.secondary.main + '50',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 40,
                    color: isSelected 
                      ? theme.palette.primary.main 
                      : theme.palette.text.secondary,
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.text}
                  sx={{
                    '& .MuiListItemText-primary': {
                      fontSize: '0.95rem',
                      fontWeight: isSelected ? 600 : 400,
                    },
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
    </Paper>
  );
};

export default SideNav;
