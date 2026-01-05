# Eyesore

A lightweight web-based eye tracking application that helps you maintain eye contact with your camera during virtual meetings. Uses MediaPipe Face Mesh for real-time eye gaze detection and browser notifications to remind you when you're not looking at the camera.

## Features

- **Real-time eye tracking** using MediaPipe Face Mesh (runs entirely in browser)
- **Browser notifications** that work even when the tab is inactive
- **Configurable sensitivity** for gaze detection
- **Adjustable notification delay** to avoid spam
- **Privacy-first** - all processing happens locally, no data sent to servers

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Open your browser and navigate to the URL shown (typically `http://localhost:3000`)

4. Grant camera and notification permissions when prompted

5. Click "Start Tracking" to begin

## Usage

1. **Start Tracking**: Click the "Start Tracking" button to begin eye tracking
2. **Adjust Sensitivity**: Use the sensitivity slider to fine-tune how strictly the app detects "looking at camera"
3. **Notification Delay**: Set how long you need to look away before receiving a notification (1-10 seconds)
4. **Stop Tracking**: Click "Stop Tracking" to stop the camera and tracking

## How It Works

The app uses MediaPipe Face Mesh to detect facial landmarks, specifically focusing on eye and iris positions. It calculates the deviation of your gaze from the camera center and determines if you're looking at the camera based on a configurable sensitivity threshold.

When you look away for longer than the notification delay, you'll receive a browser notification reminding you to look back at the camera.

## Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari (may have limited notification support)

Requires:
- Camera access
- Notification permissions
- Service Worker support (for background notifications)

## Development

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Privacy

All processing happens locally in your browser. No video data or personal information is sent to any server. The app only uses your camera feed for local eye tracking calculations.

