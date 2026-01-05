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
    console.log('[Notifications] notify() called, permission:', this.permission);
    
    if (this.permission !== 'granted') {
      console.warn('[Notifications] Permission not granted:', this.permission);
      return;
    }

    const now = Date.now();
    const timeSinceLastNotification = now - this.lastNotificationTime;
    
    if (timeSinceLastNotification < this.notificationDebounceTime) {
      console.log(`[Notifications] Debouncing: ${timeSinceLastNotification}ms since last notification (need ${this.notificationDebounceTime}ms)`);
      return; // Debounce: don't spam notifications
    }

    this.lastNotificationTime = now;
    console.log('[Notifications] Sending notification...');

    try {
      // Safari has limited service worker support, so prefer direct notifications
      const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
      
      if (!isSafari && 'serviceWorker' in navigator && navigator.serviceWorker.controller) {
        // Use service worker for background notifications (non-Safari)
        console.log('[Notifications] Using service worker');
        navigator.serviceWorker.controller.postMessage({
          type: 'NOTIFY',
          title: this.notificationTitle,
          body: message || this.notificationBody
        });
      } else {
        // Direct notification (works better in Safari)
        console.log('[Notifications] Using direct notification (Safari or no service worker)');
        const notification = new Notification(this.notificationTitle, {
          body: message || this.notificationBody,
          tag: 'eyesore-notification', // Tag to replace previous notifications
          requireInteraction: false, // Don't require user interaction
          silent: false
        });
        
        notification.onclick = () => {
          console.log('[Notifications] Notification clicked');
          window.focus();
          notification.close();
        };
        
        console.log('[Notifications] Notification created successfully');
      }
    } catch (error) {
      console.error('[Notifications] Failed to show notification:', error);
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

