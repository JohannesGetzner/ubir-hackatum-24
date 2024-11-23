import React, { createContext, useContext, useState } from 'react';

export type OptimizationMode = 'sustainable' | 'performance';

interface OptimizationModeContextType {
  mode: OptimizationMode;
  setMode: (mode: OptimizationMode) => void;
}

const OptimizationModeContext = createContext<OptimizationModeContextType | undefined>(undefined);

export const OptimizationModeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [mode, setMode] = useState<OptimizationMode>('sustainable');

  return (
    <OptimizationModeContext.Provider value={{ mode, setMode }}>
      {children}
    </OptimizationModeContext.Provider>
  );
};

export const useOptimizationMode = () => {
  const context = useContext(OptimizationModeContext);
  if (context === undefined) {
    throw new Error('useOptimizationMode must be used within an OptimizationModeProvider');
  }
  return context;
};
