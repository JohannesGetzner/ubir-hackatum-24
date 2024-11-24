import React, { createContext, useContext, useEffect, useState } from 'react';
import { getCurrentScenario, ScenarioResponse } from '../services/scenarioService';

interface ScenarioContextType {
  scenarioId: string;
  utilization: number;
  efficiency: number;
  setScenarioId: (id: string) => void;
}

const ScenarioContext = createContext<ScenarioContextType | undefined>(undefined);

export const ScenarioProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [scenarioId, setScenarioId] = useState<string>('');
  const [utilization, setUtilization] = useState<number>(0);
  const [efficiency, setEfficiency] = useState<number>(0);

  useEffect(() => {
    const fetchScenarioData = async () => {
      try {
        // Only fetch if we have a scenario ID
        if (!scenarioId) return;
        
        const data = await getCurrentScenario(scenarioId);
        if (data.savings_km_genetic !== undefined) {
          setUtilization(data.savings_km_genetic);
        }
        if (data.savings_time_genetic !== undefined) {
          setEfficiency(data.savings_time_genetic);
        }
      } catch (error) {
        console.error('Failed to fetch scenario data:', error);
      }
    };

    fetchScenarioData();
  }, [scenarioId]);

  return (
    <ScenarioContext.Provider value={{ 
      scenarioId, 
      utilization, 
      efficiency,
      setScenarioId 
    }}>
      {children}
    </ScenarioContext.Provider>
  );
};

export const useScenario = () => {
  const context = useContext(ScenarioContext);
  if (context === undefined) {
    throw new Error('useScenario must be used within a ScenarioProvider');
  }
  return context;
};
