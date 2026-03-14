import React, { useEffect, useRef, useCallback } from 'react';
import '../../styles/immersive.css';

interface Bubble {
  x: number;
  y: number;
  radius: number;
  speed: number;
  opacity: number;
  wobble: number;
  wobbleSpeed: number;
}

/**
 * BubbleParticles - Canvas-based floating bubble system
 * Creates realistic underwater bubble effects
 */
export const BubbleParticles: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const bubblesRef = useRef<Bubble[]>([]);
  const animationRef = useRef<number>(0);

  const createBubble = useCallback((canvas: HTMLCanvasElement): Bubble => ({
    x: Math.random() * canvas.width,
    y: canvas.height + Math.random() * 100,
    radius: Math.random() * 8 + 2,
    speed: Math.random() * 1.5 + 0.5,
    opacity: Math.random() * 0.4 + 0.1,
    wobble: Math.random() * Math.PI * 2,
    wobbleSpeed: Math.random() * 0.02 + 0.01,
  }), []);

  const drawBubble = useCallback((ctx: CanvasRenderingContext2D, bubble: Bubble) => {
    const gradient = ctx.createRadialGradient(
      bubble.x - bubble.radius * 0.3,
      bubble.y - bubble.radius * 0.3,
      0,
      bubble.x,
      bubble.y,
      bubble.radius
    );
    
    gradient.addColorStop(0, `rgba(255, 255, 255, ${bubble.opacity * 0.8})`);
    gradient.addColorStop(0.5, `rgba(0, 212, 255, ${bubble.opacity * 0.3})`);
    gradient.addColorStop(1, `rgba(0, 212, 255, 0)`);

    ctx.beginPath();
    ctx.arc(bubble.x, bubble.y, bubble.radius, 0, Math.PI * 2);
    ctx.fillStyle = gradient;
    ctx.fill();

    // Add highlight
    ctx.beginPath();
    ctx.arc(
      bubble.x - bubble.radius * 0.3,
      bubble.y - bubble.radius * 0.3,
      bubble.radius * 0.2,
      0,
      Math.PI * 2
    );
    ctx.fillStyle = `rgba(255, 255, 255, ${bubble.opacity})`;
    ctx.fill();
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Initialize bubbles
    const bubbleCount = Math.floor(window.innerWidth / 30);
    bubblesRef.current = Array.from({ length: bubbleCount }, () => createBubble(canvas));

    // Animation loop
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      bubblesRef.current.forEach((bubble, index) => {
        // Update position
        bubble.y -= bubble.speed;
        bubble.wobble += bubble.wobbleSpeed;
        bubble.x += Math.sin(bubble.wobble) * 0.5;

        // Reset bubble when it goes off screen
        if (bubble.y < -bubble.radius * 2) {
          bubblesRef.current[index] = createBubble(canvas);
        }

        drawBubble(ctx, bubble);
      });

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationRef.current);
    };
  }, [createBubble, drawBubble]);

  return <canvas ref={canvasRef} className="bubble-canvas" />;
};

export default BubbleParticles;
