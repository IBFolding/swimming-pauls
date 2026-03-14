import { useState, useEffect } from 'react';
import { Users, RotateCcw, Cpu, HardDrive, Clock, AlertTriangle, Zap } from 'lucide-react';
import type { ScaleConfig, SystemInfo } from '../types';
import { detectSystem, estimateTime, formatTime, cn } from '../utils';

interface ScaleConfigurationProps {
  config: ScaleConfig;
  onConfigChange: (config: ScaleConfig) => void;
  fileCount: number;
}

export function ScaleConfiguration({ config, onConfigChange, fileCount }: ScaleConfigurationProps) {
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [estimatedTime, setEstimatedTime] = useState(0);

  useEffect(() => {
    setSystemInfo(detectSystem());
  }, []);

  useEffect(() => {
    setEstimatedTime(estimateTime(config.paulCount, config.rounds, fileCount));
  }, [config.paulCount, config.rounds, fileCount]);

  const isHighScale = config.paulCount > 100 || config.rounds > 50;
  const isVeryHighScale = config.paulCount > 500 || config.rounds > 200;

  const handlePaulCountChange = (value: number) => {
    onConfigChange({ ...config, paulCount: value });
  };

  const handleRoundsChange = (value: number) => {
    onConfigChange({ ...config, rounds: value });
  };

  const getRecommendation = () => {
    if (!systemInfo) return null;
    
    const maxRecommendedPauls = systemInfo.cpuCores * 50;
    const maxRecommendedRounds = systemInfo.memoryGB * 10;
    
    if (config.paulCount > maxRecommendedPauls) {
      return {
        type: 'warning',
        message: `Your system may struggle with ${config.paulCount} Pauls. Recommended max: ${maxRecommendedPauls}`,
      };
    }
    
    if (config.rounds > maxRecommendedRounds) {
      return {
        type: 'warning', 
        message: `High round count may use significant memory. Recommended max: ${maxRecommendedRounds}`,
      };
    }
    
    return null;
  };

  const recommendation = getRecommendation();

  return (
    <div className="space-y-6">
      {/* System Info Banner */}
      {systemInfo && (
        <div className="flex flex-wrap gap-3 p-3 bg-dark-800/50 rounded-xl border border-dark-600/50">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-dark-700/50 rounded-lg">
            <Cpu className="w-4 h-4 text-accent-cyan" />
            <span className="text-sm text-gray-300">
              {systemInfo.cpuCores} Cores
            </span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-dark-700/50 rounded-lg">
            <HardDrive className="w-4 h-4 text-accent-purple" />
            <span className="text-sm text-gray-300">
              ~{systemInfo.memoryGB} GB RAM
            </span>
          </div>
        </div>
      )}

      {/* Paul Count Slider */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium text-gray-300 flex items-center gap-2">
            <Users className="w-4 h-4 text-accent-blue" />
            Number of Pauls
          </label>
          <div className="flex items-center gap-3">
            <input
              type="number"
              min={1}
              max={10000}
              value={config.paulCount}
              onChange={(e) => handlePaulCountChange(parseInt(e.target.value) || 1)}
              className="w-20 px-2 py-1 bg-dark-900 border border-dark-600 rounded-lg text-right 
                       text-sm focus:outline-none focus:border-accent-blue/50"
            />
            <button
              onClick={() => handlePaulCountChange(10)}
              className="text-xs px-2 py-1 bg-dark-700 hover:bg-dark-600 rounded-md 
                       text-gray-400 hover:text-white transition-colors"
            >
              Reset
            </button>
          </div>        </div>
        
        <div className="relative pt-1">
          <input
            type="range"
            min={1}
            max={1000}
            step={1}
            value={Math.min(config.paulCount, 1000)}
            onChange={(e) => handlePaulCountChange(parseInt(e.target.value))}
            className="w-full h-2 bg-dark-700 rounded-lg appearance-none cursor-pointer
                     accent-accent-blue hover:accent-accent-cyan transition-all"
            style={{
              background: `linear-gradient(to right, #3b82f6 0%, #06b6d4 ${(Math.min(config.paulCount, 1000) / 1000) * 100}%, #252535 ${(Math.min(config.paulCount, 1000) / 1000) * 100}%, #252535 100%)`
            }}
          />
          <div className="flex justify-between mt-1 text-xs text-gray-500">
            <span>1</span>
            <span>250</span>
            <span>500</span>
            <span>750</span>
            <span>1000+</span>
          </div>
        </div>
        
        {config.paulCount > 1000 && (
          <input
            type="number"
            min={1001}
            max={10000}
            value={config.paulCount}
            onChange={(e) => handlePaulCountChange(parseInt(e.target.value) || 1000)}
            placeholder="Enter exact number..."
            className="w-full mt-2 px-3 py-2 bg-dark-900 border border-accent-blue/30 
                     rounded-lg text-sm focus:outline-none focus:border-accent-blue"
          />
        )}
      </div>

      {/* Rounds Slider */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium text-gray-300 flex items-center gap-2">
            <RotateCcw className="w-4 h-4 text-accent-purple" />
            Discussion Rounds
          </label>
          <div className="flex items-center gap-3">
            <input
              type="number"
              min={5}
              max={500}
              value={config.rounds}
              onChange={(e) => handleRoundsChange(parseInt(e.target.value) || 5)}
              className="w-20 px-2 py-1 bg-dark-900 border border-dark-600 rounded-lg text-right 
                       text-sm focus:outline-none focus:border-accent-blue/50"
            />
            <button
              onClick={() => handleRoundsChange(20)}
              className="text-xs px-2 py-1 bg-dark-700 hover:bg-dark-600 rounded-md 
                       text-gray-400 hover:text-white transition-colors"
            >
              Reset
            </button>
          </div>        </div>
        
        <div className="relative pt-1">
          <input
            type="range"
            min={5}
            max={500}
            step={5}
            value={config.rounds}
            onChange={(e) => handleRoundsChange(parseInt(e.target.value))}
            className="w-full h-2 bg-dark-700 rounded-lg appearance-none cursor-pointer
                     accent-accent-purple hover:accent-accent-cyan transition-all"
            style={{
              background: `linear-gradient(to right, #8b5cf6 0%, #3b82f6 ${((config.rounds - 5) / 495) * 100}%, #252535 ${((config.rounds - 5) / 495) * 100}%, #252535 100%)`
            }}
          />
          <div className="flex justify-between mt-1 text-xs text-gray-500">
            <span>5</span>
            <span>125</span>
            <span>250</span>
            <span>375</span>
            <span>500</span>
          </div>
        </div>
      </div>

      {/* Time Estimate */}
      <div className={cn(
        "p-4 rounded-xl border flex items-center gap-4",
        isVeryHighScale 
          ? "bg-red-500/10 border-red-500/30" 
          : isHighScale 
            ? "bg-yellow-500/10 border-yellow-500/30"
            : "bg-dark-800/50 border-dark-600/50"
      )}>
        <div className={cn(
          "p-3 rounded-xl",
          isVeryHighScale 
            ? "bg-red-500/20" 
            : isHighScale 
              ? "bg-yellow-500/20"
              : "bg-accent-blue/20"
        )}>
          <Clock className={cn(
            "w-6 h-6",
            isVeryHighScale 
              ? "text-red-400" 
              : isHighScale 
                ? "text-yellow-400"
                : "text-accent-blue"
          )} />
        </div>
        
        <div className="flex-1">
          <p className="text-sm text-gray-400">Estimated Time</p>
          <p className={cn(
            "text-2xl font-bold",
            isVeryHighScale 
              ? "text-red-400" 
              : isHighScale 
                ? "text-yellow-400"
                : "text-white"
          )}>
            {formatTime(estimatedTime)}
          </p>
        </div>
        
        {isHighScale && (
          <div className="flex items-center gap-2 text-yellow-400">
            <Zap className="w-5 h-5" />
            <span className="text-sm font-medium">High Scale</span>
          </div>
        )}
      </div>

      {/* Warnings */}
      {isVeryHighScale && (
        <div className="flex items-start gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
          <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-400">Very High Scale Configuration</p>
            <p className="text-sm text-red-300/80 mt-1">
              This configuration may take significant time and resources. 
              Consider reducing the number of Pauls or rounds for faster results.
            </p>
          </div>
        </div>
      )}

      {recommendation && !isVeryHighScale && (
        <div className="flex items-start gap-3 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-xl">
          <AlertTriangle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-yellow-400">System Recommendation</p>
            <p className="text-sm text-yellow-300/80 mt-1">{recommendation.message}</p>
          </div>
        </div>
      )}
    </div>
  );
}