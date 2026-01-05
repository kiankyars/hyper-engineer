export class NotificationManager {
  private permission: NotificationPermission = 'default';
  private notificationDebounceTime: number;
  private lastNotificationTime: number = 0;
  private notificationTitle: string = 'Look at Camera';
  private notificationBody: string = 'You\'re not looking at the camera!';

  constructor(debounceTime: number = 3000) {
    this.notificationDebounceTime = debounceTime;
  }

  async requestPermission(): Promise<boolean> {
    if (!('Notification' in window)) {
      console.warn('This browser does not support notifications');
      return false;
    }

    if (this.permission === 'granted') {
      return true;
    }

    if (this.permission === 'default') {
      const permission = await Notification.requestPermission();
      this.permission = permission;
      return permission === 'granted';
    }

    return false;
  }

  async registerServiceWorker(): Promise<boolean> {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js', {
          scope: '/'
        });
        console.log('Service Worker registered:', registration);
        return true;
      } catch (error) {
        console.error('Service Worker registration failed:', error);
        return false;
      }
    }
    return false;
  }

  async notify(message?: string): Promise<void> {
    if (this.permission !== 'granted') {
      return;
    }

    const now = Date.now();
    if (now - this.lastNotificationTime < this.notificationDebounceTime) {
      return; // Debounce: don't spam notifications
    }

    this.lastNotificationTime = now;

    try {
      if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
        // Use service worker for background notifications
        navigator.serviceWorker.controller.postMessage({
          type: 'NOTIFY',
          title: this.notificationTitle,
          body: message || this.notificationBody
        });
      } else {
        // Fallback to regular notification
        new Notification(this.notificationTitle, {
          body: message || this.notificationBody,
          icon: '/icon.png', // Optional icon
          tag: 'eyesore-notification', // Tag to replace previous notifications
          requireInteraction: false // Don't require user interaction
        });
      }
    } catch (error) {
      console.error('Failed to show notification:', error);
    }
  }

  setDebounceTime(ms: number): void {
    this.notificationDebounceTime = Math.max(1000, Math.min(10000, ms));
  }

  setNotificationText(title: string, body: string): void {
    this.notificationTitle = title;
    this.notificationBody = body;
  }

  getPermission(): NotificationPermission {
    return this.permission;
  }

  isSupported(): boolean {
    return 'Notification' in window;
  }
}

