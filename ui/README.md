# Swimming Pauls UI

A modern React/Vite web interface for the Swimming Pauls multi-agent analysis system.

## Features

### 1. File Upload Zone
- Drag & drop support for Images, Videos, PDFs, CSVs, and JSON files
- File preview thumbnails
- File type icons with color coding
- Remove button per file
- Upload progress indicators
- Multiple file support (up to 10 files)

### 2. Questions Interface
- Primary question textarea
- Dynamic follow-up questions (add/remove)
- Voice input using Web Speech API
- Question templates dropdown
- Real-time text updates

### 3. Scale Configuration
- Number of Pauls slider (1-1000+)
- Rounds slider (5-500)
- System detection (CPU cores, RAM)
- Time estimate display
- Warning indicators for high values
- Recommended settings based on hardware

### 4. Paul Selector
- Grid of Paul cards with emoji, name, and type
- Toggle on/off selection
- Filter by type (Analyst, Creative, Technical, Researcher, Reviewer)
- "Select All" / "Clear All" buttons
- Selected count display
- Type breakdown summary

### 5. Modern UI
- Dark theme with blue gradient accents
- Glassmorphism cards with backdrop blur
- Smooth animations (fade, slide, pulse)
- Responsive design (mobile, tablet, desktop)
- Gradient text and glow effects

## Tech Stack

- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **Icons:** Lucide React

## Getting Started

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── components/
│   ├── FileUploadZone.tsx    # File upload with drag & drop
│   ├── QuestionsInterface.tsx # Questions with voice input
│   ├── ScaleConfiguration.tsx # Sliders and system info
│   └── PaulSelector.tsx       # Paul selection grid
├── types/
│   └── index.ts               # TypeScript interfaces
├── utils/
│   └── index.ts               # Utility functions
├── App.tsx                    # Main application
├── main.tsx                   # Entry point
└── index.css                  # Global styles & Tailwind
```

## Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari
- Voice input requires browsers with Web Speech API support

## License

MIT