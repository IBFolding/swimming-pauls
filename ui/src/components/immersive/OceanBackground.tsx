import React, { useEffect, useRef } from 'react';
import '../../styles/immersive.css';

/**
 * OceanBackground - Animated underwater background
 * Features: Gradient animation, light rays, wave effects
 */
export const OceanBackground: React.FC = () => {
  return (
    <div className="ocean-background">
      {/* Animated gradient overlay */}
      <div className="light-rays" />
      
      {/* Wave animations at bottom */}
      <div className="wave-container">
        <div className="wave" />
        <div className="wave" />
        <div className="wave" />
      </div>
    </div>
  );
};

export default OceanBackground;
