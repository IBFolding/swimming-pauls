# Swimming Pauls - Immersive UI Components

Atmospheric underwater-themed UI components for the Swimming Pauls dApp.

## 🎨 Components

### OceanBackground
Animated ocean background with gradient, light rays, and wave effects.

```tsx
import { OceanBackground } from './components/immersive';

<OceanBackground />
```

### BubbleParticles
Canvas-based floating bubble particle system.

```tsx
import { BubbleParticles } from './components/immersive';

<BubbleParticles />
```

### SwimmingPauls
Silhouette Pauls that swim across the screen periodically.

```tsx
import { SwimmingPauls } from './components/immersive';

<SwimmingPauls />
```

### AudioPlayer
Music player with play/pause, mute, and volume controls.

```tsx
import { AudioPlayer } from './components/immersive';

<AudioPlayer
  trackUrl="/swimming-paul.mp3"
  trackName="Swimming Paul"
  artistName="The Deep End"
/>
```

### GlassCard
Glassmorphism card with hover effects.

```tsx
import { GlassCard } from './components/immersive';

<GlassCard hoverEffect="lift" | "glow" | "both" | "none">
  Content here
</GlassCard>
```

### LoadingSwimmer
Animated loading state with swimming Paul animation.

```tsx
import { LoadingSwimmer } from './components/immersive';

<LoadingSwimmer text="Swimming into the pool..." size="sm" | "md" | "lg" />
```

### SplashEffect
Creates water splash animation on clicks.

```tsx
import { SplashEffect, triggerSplash } from './components/immersive';

// Wrap components for auto-splash on click
<SplashEffect>
  <button>Click for splash!</button>
</SplashEffect>

// Or trigger manually
triggerSplash(x, y);
```

### PoolCard
Fish/pool metaphor card for displaying pools.

```tsx
import { PoolCard } from './components/immersive';

<PoolCard
  title="Shallow Reef"
  description="Beginner-friendly waters"
  depth={25}
  fishCount={42}
  rewardToken="PAUL"
  onCast={() => console.log('Cast!')}
/>
```

## 🌊 Color Palette

| Name | Value | Usage |
|------|-------|-------|
| Ocean Deep | `#0a0e27` | Background base |
| Cyan Glow | `#00d4ff` | Primary accent |
| Purple Glow | `#a855f7` | Secondary accent |
| Pink Glow | `#ec4899` | Tertiary accent |
| Blue Bright | `#3b82f6` | Links, buttons |

## 🎵 Audio

Place `swimming-paul.mp3` in the `public/` folder for the AudioPlayer to work.

## 📦 Usage Example

```tsx
import {
  OceanBackground,
  BubbleParticles,
  SwimmingPauls,
  AudioPlayer,
  GlassCard,
} from './components/immersive';

function App() {
  return (
    <>
      <OceanBackground />
      <BubbleParticles />
      <SwimmingPauls />
      
      <div style={{ position: 'relative', zIndex: 10 }}>
        <AudioPlayer />
        <GlassCard>
          <h1>Swimming Pauls</h1>
        </GlassCard>
      </div>
    </>
  );
}
```

## 🎯 CSS Classes

- `.ocean-background` - Animated background
- `.glass-card` - Glassmorphism effect
- `.glass-panel` - Darker glass panel
- `.btn-ocean` - Ocean-themed button
- `.text-glow` - Glowing text
- `.text-gradient` - Gradient text
- `.text-shimmer` - Animated shimmer text
- `.card-hover-lift` - Lift on hover
- `.card-hover-glow` - Glow on hover
- `.pool-card` - Pool-themed card
