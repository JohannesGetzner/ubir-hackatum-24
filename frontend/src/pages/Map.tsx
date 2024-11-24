import React, { useEffect, useRef, useState } from 'react';
import * as maptilersdk from '@maptiler/sdk';
import '@maptiler/sdk/dist/maptiler-sdk.css';
import { Box, useTheme } from '@mui/material';
import { mapService } from '../services/mapService';
import type { MapState, Vehicle, Customer } from '../services/mapService';
import { useScenario } from '../context/ScenarioContext';

const Map = () => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maptilersdk.Map | null>(null);
  const vehicleMarkers = useRef<{ [key: string]: maptilersdk.Marker }>({});
  const customerMarkers = useRef<{ [key: string]: maptilersdk.Marker }>({});
  const routeLines = useRef<{ [key: string]: any }>({});  // Store route lines
  const theme = useTheme();
  const [mapState, setMapState] = useState<MapState | null>(null);
  const [errorCount, setErrorCount] = useState(0);
  const { scenarioId } = useScenario();
  const updateTimeoutRef = useRef<NodeJS.Timeout | null>(null);

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
  const createDotMarker = (color: string, size: number = 16) => {
    const dot = document.createElement('div');
    dot.style.width = `${size}px`;
    dot.style.height = `${size}px`;
    dot.style.background = color;
    dot.style.borderRadius = '50%';
    dot.style.border = '2px solid white';
    dot.style.boxShadow = '0 0 2px rgba(0,0,0,0.3)';
    const marker = document.createElement('div');
    marker.appendChild(dot);
    return marker;
  };

  // Create legend component
  const Legend = () => {
    return (
      <Box
        sx={{
          position: 'absolute',
          top: 16,
          left: 16,
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          padding: 2,
          borderRadius: 1,
          boxShadow: 1,
          zIndex: 1000,
        }}
      >
        <Box sx={{ typography: 'subtitle2', mb: 1 }}>Legend</Box>
        {[
          { color: '#FFC107', label: 'Idle Vehicle' },
          { color: '#2196F3', label: 'Vehicle to Customer' },
          { color: '#4CAF50', label: 'Vehicle with Customer' },
          { color: '#9E9E9E', label: 'Customer' },
          { color: '#616161', label: 'Destination' },
        ].map(({ color, label }) => (
          <Box key={label} sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
            <Box
              sx={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                backgroundColor: color,
                border: '2px solid white',
                boxShadow: '0 0 2px rgba(0,0,0,0.3)',
                mr: 1,
              }}
            />
            <Box sx={{ typography: 'body2' }}>{label}</Box>
          </Box>
        ))}
      </Box>
    );
  };

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current) return;

    maptilersdk.config.apiKey = 'JfHqwiLtd3afNgts8zgC';
    
    const initMap = () => {
      if (!map.current && mapContainer.current) {
        try {
          const mapInstance = new maptilersdk.Map({
            container: mapContainer.current,
            style: maptilersdk.MapStyle.STREETS,
            center: [11.5820, 48.1351], // Munich coordinates
            zoom: 12,
            preserveDrawingBuffer: true, // Help prevent context loss
            antialias: true
          });

          map.current = mapInstance;

          mapInstance.on('error', (e) => {
            console.error('Map error:', e);
            // Try to recover from context loss
            if (e.error && e.error.message.includes('WebGL')) {
              map.current?.remove();
              map.current = null;
              setTimeout(initMap, 1000);
            }
          });

          mapInstance.on('load', () => {
            // Source for pickup routes (blue)
            mapInstance.addSource('pickup-routes', {
              type: 'geojson',
              data: {
                type: 'FeatureCollection',
                features: []
              }
            });

            // Source for destination routes (green)
            mapInstance.addSource('destination-routes', {
              type: 'geojson',
              data: {
                type: 'FeatureCollection',
                features: []
              }
            });

            // Layer for pickup routes (blue)
            mapInstance.addLayer({
              id: 'pickup-lines',
              type: 'line',
              source: 'pickup-routes',
              layout: {
                'line-join': 'round',
                'line-cap': 'round'
              },
              paint: {
                'line-color': '#2196F3',
                'line-width': 1,
                'line-dasharray': [2, 2]
              }
            });

            // Layer for destination routes (green)
            mapInstance.addLayer({
              id: 'destination-lines',
              type: 'line',
              source: 'destination-routes',
              layout: {
                'line-join': 'round',
                'line-cap': 'round'
              },
              paint: {
                'line-color': '#4CAF50',
                'line-width': 1,
                'line-dasharray': [2, 2]
              }
            });
          });

          setTimeout(() => {
            mapInstance?.resize();
          }, 100);
        } catch (error) {
          console.error('Error initializing map:', error);
          setTimeout(initMap, 1000);
        }
      }
    };

    initMap();

    const handleResize = () => {
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current);
      }
      updateTimeoutRef.current = setTimeout(() => {
        if (map.current) {
          map.current.resize();
        }
      }, 100);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current);
      }
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
      Object.values(vehicleMarkers.current).forEach(marker => marker.remove());
      Object.values(customerMarkers.current).forEach(marker => marker.remove());
    };
  }, [mapContainer.current]);

  // Fetch map state periodically with debouncing
  useEffect(() => {
    if (!scenarioId) return;

    const fetchMapState = async () => {
      if (!map.current) return;
      
      try {
        const state = await mapService.getMapState(scenarioId);
        setMapState(state);
        setErrorCount(0);
      } catch (error) {
        console.error('Error fetching map state:', error);
        setErrorCount(prev => prev + 1);
      }
    };

    fetchMapState();
    const interval = setInterval(fetchMapState, 2000); // Reduced frequency to 2 seconds
    return () => clearInterval(interval);
  }, [scenarioId]);

  // Update markers with debouncing
  useEffect(() => {
    if (!map.current || !mapState) return;

    if (updateTimeoutRef.current) {
      clearTimeout(updateTimeoutRef.current);
    }

    updateTimeoutRef.current = setTimeout(() => {
      try {
        // Update route lines
        const pickupFeatures: any[] = [];
        const destinationFeatures: any[] = [];
        
        mapState.vehicles.forEach((vehicle: Vehicle) => {
          if (vehicle.current_customer_id) {
            const customer = mapState.customers.find(c => c.id === vehicle.current_customer_id);
            if (customer) {
              if (!customer.picked_up && vehicle.enroute === 'cust') {
                // Add pickup route (blue line)
                pickupFeatures.push({
                  type: 'Feature',
                  geometry: {
                    type: 'LineString',
                    coordinates: [
                      [vehicle.longitude, vehicle.latitude],
                      [customer.longitude, customer.latitude]
                    ]
                  }
                });
              } else if (customer.picked_up && 
                        customer.destination_longitude && 
                        customer.destination_latitude &&
                        vehicle.enroute === 'dest') {
                // Add destination route (green line)
                destinationFeatures.push({
                  type: 'Feature',
                  geometry: {
                    type: 'LineString',
                    coordinates: [
                      [vehicle.longitude, vehicle.latitude],
                      [customer.destination_longitude, customer.destination_latitude]
                    ]
                  }
                });
              }
            }
          }
        });

        // Update the route lines sources
        const mapInstance = map.current;
        if (mapInstance) {
          // Update pickup routes
          if (mapInstance.getSource('pickup-routes')) {
            (mapInstance.getSource('pickup-routes') as any).setData({
              type: 'FeatureCollection',
              features: pickupFeatures
            });
          }
          
          // Update destination routes
          if (mapInstance.getSource('destination-routes')) {
            (mapInstance.getSource('destination-routes') as any).setData({
              type: 'FeatureCollection',
              features: destinationFeatures
            });
          }
        }

        // Update vehicle markers
        mapState.vehicles.forEach((vehicle: Vehicle) => {
          const marker = vehicleMarkers.current[vehicle.id];
          const color = getVehicleColor(vehicle);
          
          if (marker) {
            marker.setLngLat([vehicle.longitude, vehicle.latitude]);
            const dot = marker.getElement().firstChild as HTMLElement;
            if (dot) dot.style.background = color;
          } else if (mapInstance) {
            const el = createDotMarker(color);
            el.style.zIndex = '1000'; // Ensure vehicles are always on top
            vehicleMarkers.current[vehicle.id] = new maptilersdk.Marker({
              element: el,
              anchor: 'center'
            })
              .setLngLat([vehicle.longitude, vehicle.latitude])
              .addTo(mapInstance);
          }
        });

        // Update customer markers
        mapState.customers.forEach((customer: Customer) => {
          const marker = customerMarkers.current[customer.id];
          
          // Remove marker if customer is dropped off
          if (customer.dropped_off) {
            if (marker) {
              marker.remove();
              delete customerMarkers.current[customer.id];
            }
            return;
          }
          
          if (marker) {
            marker.setLngLat([customer.longitude, customer.latitude]);
          } else if (mapInstance) {
            const el = createDotMarker('#9E9E9E');
            el.style.zIndex = '100'; // Lower z-index for customers
            customerMarkers.current[customer.id] = new maptilersdk.Marker({
              element: el,
              anchor: 'center'
            })
              .setLngLat([customer.longitude, customer.latitude])
              .addTo(mapInstance);
          }

          // Add destination marker if customer has a destination
          if (customer.destination_longitude && customer.destination_latitude) {
            const destMarkerId = `${customer.id}-dest`;
            const destMarker = customerMarkers.current[destMarkerId];
            
            // Remove destination marker if customer is dropped off
            if (customer.dropped_off) {
              if (destMarker) {
                destMarker.remove();
                delete customerMarkers.current[destMarkerId];
              }
              return;
            }
            
            if (destMarker) {
              destMarker.setLngLat([customer.destination_longitude, customer.destination_latitude]);
            } else if (mapInstance) {
              const el = createDotMarker('#616161', 12);
              el.style.zIndex = '50'; // Lowest z-index for destinations
              customerMarkers.current[destMarkerId] = new maptilersdk.Marker({
                element: el,
                anchor: 'center'
              })
                .setLngLat([customer.destination_longitude, customer.destination_latitude])
                .addTo(mapInstance);
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
      } catch (error) {
        console.error('Error updating markers:', error);
      }
    }, 100);
  }, [mapState]);

  return (
    <Box sx={{ position: 'relative', width: '100%', height: '100%' }}>
      <div ref={mapContainer} style={{ width: '100%', height: '100%' }} />
      <Legend />
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
