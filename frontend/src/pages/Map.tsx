import React, { useEffect, useRef, useState } from 'react';
import * as maptilersdk from '@maptiler/sdk';
import '@maptiler/sdk/dist/maptiler-sdk.css';
import { Box, useTheme } from '@mui/material';
import { mapService } from '../services/mapService';
import type { MapState, Vehicle, Customer } from '../services/mapService';

const Map = () => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maptilersdk.Map | null>(null);
  const vehicleMarkers = useRef<{ [key: string]: maptilersdk.Marker }>({});
  const customerMarkers = useRef<{ [key: string]: maptilersdk.Marker }>({});
  const theme = useTheme();
  const [mapState, setMapState] = useState<MapState | null>(null);
  const [errorCount, setErrorCount] = useState(0);

  // Get vehicle color based on status
  const getVehicleColor = (vehicle: Vehicle) => {
    switch (vehicle.enroute) {
      case 'idle':
        return '#FFC107'; // Yellow for idle
      case 'cust':
        return '#2196F3'; // Blue for en route to customer
      case 'dest':
        return '#4CAF50'; // Green when with customer
      default:
        return '#FFC107'; // Default yellow
    }
  };

  // Create dot marker element
  const createDotMarker = (color: string, size: number = 12) => {
    const dot = document.createElement('div');
    dot.style.width = `${size}px`;
    dot.style.height = `${size}px`;
    dot.style.background = color;
    dot.style.borderRadius = '50%';
    const marker = document.createElement('div');
    marker.appendChild(dot);
    return marker;
  };

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current) return;

    maptilersdk.config.apiKey = 'JfHqwiLtd3afNgts8zgC';
    
    if (!map.current) {
      map.current = new maptilersdk.Map({
        container: mapContainer.current,
        style: maptilersdk.MapStyle.STREETS,
        center: [11.5820, 48.1351], // Munich coordinates
        zoom: 12
      });

      setTimeout(() => {
        map.current?.resize();
      }, 100);
    }

    const handleResize = () => {
      if (map.current) {
        map.current.resize();
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
      Object.values(vehicleMarkers.current).forEach(marker => marker.remove());
      Object.values(customerMarkers.current).forEach(marker => marker.remove());
    };
  }, [mapContainer.current]);

  // Fetch map state every 2 seconds
  useEffect(() => {
    const fetchMapState = async () => {
      try {
        const state = await mapService.getMapState();
        if (state.status === 'error') {
          setErrorCount(prev => prev + 1);
          console.warn('Map state update failed:', state.message);
        } else {
          setErrorCount(0);
        }
        if (state.vehicles.length > 0 || state.customers.length > 0) {
          setMapState(state);
        }
      } catch (error) {
        console.error('Failed to fetch map state:', error);
        setErrorCount(prev => prev + 1);
      }
    };

    fetchMapState();
    const interval = setInterval(fetchMapState, 2000);
    return () => clearInterval(interval);
  }, []);

  // Update markers when map state changes
  useEffect(() => {
    if (!map.current || !mapState) return;

    // Update vehicle markers
    mapState.vehicles.forEach((vehicle: Vehicle) => {
      const marker = vehicleMarkers.current[vehicle.id];
      const color = getVehicleColor(vehicle);
      
      if (marker) {
        marker.setLngLat([vehicle.longitude, vehicle.latitude]);
        const dot = marker.getElement().firstChild as HTMLElement;
        if (dot) dot.style.background = color;
      } else if (map.current) {
        const el = createDotMarker(color);
        el.style.zIndex = '1000'; // Ensure vehicles are always on top
        vehicleMarkers.current[vehicle.id] = new maptilersdk.Marker({
          element: el,
          anchor: 'center'
        })
          .setLngLat([vehicle.longitude, vehicle.latitude])
          .addTo(map.current);
      }
    });

    // Update customer markers
    mapState.customers.forEach((customer: Customer) => {
      const marker = customerMarkers.current[customer.id];
      
      if (marker) {
        marker.setLngLat([customer.longitude, customer.latitude]);
      } else if (map.current) {
        const el = createDotMarker('#9E9E9E');
        el.style.zIndex = '100'; // Lower z-index for customers
        customerMarkers.current[customer.id] = new maptilersdk.Marker({
          element: el,
          anchor: 'center'
        })
          .setLngLat([customer.longitude, customer.latitude])
          .addTo(map.current);
      }

      // Add destination marker if customer has a destination
      if (customer.destination_longitude && customer.destination_latitude) {
        const destMarkerId = `${customer.id}-dest`;
        const destMarker = customerMarkers.current[destMarkerId];
        
        if (destMarker) {
          destMarker.setLngLat([customer.destination_longitude, customer.destination_latitude]);
        } else if (map.current) {
          const el = createDotMarker('#616161', 8);
          el.style.zIndex = '50'; // Lowest z-index for destinations
          customerMarkers.current[destMarkerId] = new maptilersdk.Marker({
            element: el,
            anchor: 'center'
          })
            .setLngLat([customer.destination_longitude, customer.destination_latitude])
            .addTo(map.current);
        }
      }
    });

    // Remove markers that are no longer present
    Object.keys(vehicleMarkers.current).forEach(id => {
      if (!mapState.vehicles.some(v => v.id === id)) {
        vehicleMarkers.current[id].remove();
        delete vehicleMarkers.current[id];
      }
    });

    Object.keys(customerMarkers.current).forEach(id => {
      const baseId = id.replace('-dest', '');
      if (!mapState.customers.some(c => c.id === baseId)) {
        customerMarkers.current[id].remove();
        delete customerMarkers.current[id];
      }
    });
  }, [mapState]);

  return (
    <Box sx={{ 
      height: '100%', 
      width: '100%', 
      display: 'flex',
      borderRadius: '15px',
      overflow: 'hidden',
      position: 'relative',
      '& .mapboxgl-canvas': {
        borderRadius: '15px'
      }
    }} ref={mapContainer}>
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
    </Box>
  );
};

export default Map;
