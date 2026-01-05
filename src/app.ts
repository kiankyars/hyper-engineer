import { CameraManager } from './camera';
import { EyeTracker, GazeState } from './eyeTracker';
import { NotificationManager } from './notifications';

class App {
  private cameraManager: CameraManager;
  private eyeTracker: EyeTracker;
  private notificationManager: NotificationManager;
  private isTracking: boolean = false;
  private lookAwayStartTime: number | null = null;
  private readonly lookAwayThreshold: number = 2000; // 2 seconds before notification

  // UI Elements
  private videoElement: HTMLVideoElement;
  private startBtn: HTMLButtonElement;
  private stopBtn: HTMLButtonElement;
  private statusIcon: HTMLElement;
  private statusText: HTMLElement;
  private notificationDelaySlider: HTMLInputElement;
  private notificationDelayValue: HTMLElement;
  private cameraPermissionStatus: HTMLElement;
  private notificationPermissionStatus: HTMLElement;

  constructor() {
    this.videoElement = document.getElementById('video') as HTMLVideoElement;
    this.startBtn = document.getElementById('startBtn') as HTMLButtonElement;
    this.stopBtn = document.getElementById('stopBtn') as HTMLButtonElement;
    this.statusIcon = document.getElementById('statusIcon') as HTMLElement;
    this.statusText = document.getElementById('statusText') as HTMLElement;
    this.notificationDelaySlider = document.getElementById('notificationDelay') as HTMLInputElement;
    this.notificationDelayValue = document.getElementById('notificationDelayValue') as HTMLElement;
    this.cameraPermissionStatus = document.getElementById('cameraPermission') as HTMLElement;
    this.notificationPermissionStatus = document.getElementById('notificationPermission') as HTMLElement;

    this.cameraManager = new CameraManager(this.videoElement);
    this.eyeTracker = new EyeTracker(0.85, true); // Higher smoothing, debug mode enabled
    this.notificationManager = new NotificationManager();

    this.setupEventListeners();
    this.initializePermissions();
  }

  private setupEventListeners(): void {
    this.startBtn.addEventListener('click', () => this.start());
    this.stopBtn.addEventListener('click', () => this.stop());

    this.notificationDelaySlider.addEventListener('input', (e) => {
      const value = parseInt((e.target as HTMLInputElement).value);
      this.notificationDelayValue.textContent = value.toString();
      this.notificationManager.setDebounceTime(value * 1000);
    });
  }

  private async initializePermissions(): Promise<void> {
    // Check notification permission status
    if (this.notificationManager.isSupported()) {
      const permission = this.notificationManager.getPermission();
      this.updateNotificationPermissionStatus(permission);
    } else {
      this.updateNotificationPermissionStatus('denied');
    }

    // Register service worker
    await this.notificationManager.registerServiceWorker();
  }

  private updateNotificationPermissionStatus(permission: NotificationPermission): void {
    this.notificationPermissionStatus.textContent = permission;
    this.notificationPermissionStatus.className = `permission-status ${permission}`;
  }

  private updateCameraPermissionStatus(granted: boolean): void {
    const status = granted ? 'granted' : 'denied';
    this.cameraPermissionStatus.textContent = status;
    this.cameraPermissionStatus.className = `permission-status ${status}`;
  }

  private updateStatus(gazeState: GazeState | null): void {
    if (!gazeState) {
      this.statusIcon.className = 'status-icon initializing';
      this.statusText.textContent = 'No face detected';
      return;
    }

    if (gazeState.isLookingAtCamera) {
      this.statusIcon.className = 'status-icon looking';
      this.statusText.textContent = 'Looking at camera';
      this.lookAwayStartTime = null;
    } else {
      this.statusIcon.className = 'status-icon not-looking';
      this.statusText.textContent = 'Not looking at camera';
      
      // Track when user started looking away
      if (this.lookAwayStartTime === null) {
        this.lookAwayStartTime = Date.now();
      } else {
        const lookAwayDuration = Date.now() - this.lookAwayStartTime;
        if (lookAwayDuration >= this.lookAwayThreshold) {
          this.notificationManager.notify();
        }
      }
    }
  }

  private async start(): Promise<void> {
    try {
      // Request notification permission if not already granted
      if (this.notificationManager.getPermission() !== 'granted') {
        const granted = await this.notificationManager.requestPermission();
        this.updateNotificationPermissionStatus(
          granted ? 'granted' : 'denied'
        );
      }

      // Set tracking flag before starting camera so callbacks work
      this.isTracking = true;

      // Start camera
      await this.cameraManager.start({
        onResults: (results) => {
          if (!this.isTracking) return;

          if (results.multiFaceLandmarks && results.multiFaceLandmarks.length > 0) {
            const landmarks = results.multiFaceLandmarks[0];
            const gazeState = this.eyeTracker.detectGaze(landmarks);
            this.updateStatus(gazeState);
          } else {
            this.updateStatus(null);
          }
        },
        width: 640,
        height: 480
      });

      this.updateCameraPermissionStatus(true);
      this.startBtn.disabled = true;
      this.stopBtn.disabled = false;
      this.statusIcon.className = 'status-icon initializing';
      this.statusText.textContent = 'Initializing...';
    } catch (error) {
      console.error('Failed to start:', error);
      this.updateCameraPermissionStatus(false);
      alert(`Failed to start camera: ${error}`);
    }
  }

  private stop(): void {
    this.cameraManager.stop();
    this.isTracking = false;
    this.eyeTracker.reset();
    this.lookAwayStartTime = null;
    this.startBtn.disabled = false;
    this.stopBtn.disabled = true;
    this.statusIcon.className = 'status-icon initializing';
    this.statusText.textContent = 'Stopped';
  }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new App();
});

