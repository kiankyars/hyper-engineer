import { FaceMesh } from '@mediapipe/face_mesh';
import { Camera } from '@mediapipe/camera_utils';

export interface CameraConfig {
  onResults: (results: any) => void;
  width?: number;
  height?: number;
}

export class CameraManager {
  private faceMesh: FaceMesh;
  private camera: Camera | null = null;
  private videoElement: HTMLVideoElement;

  constructor(videoElement: HTMLVideoElement) {
    this.videoElement = videoElement;
    this.faceMesh = new FaceMesh({
      locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`;
      }
    });

    this.faceMesh.setOptions({
      maxNumFaces: 1,
      refineLandmarks: true,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5
    });

    this.faceMesh.onResults((results) => {
      // Results will be handled by the callback
    });
  }

  async start(config: CameraConfig): Promise<void> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: config.width || 640,
          height: config.height || 480,
          facingMode: 'user'
        }
      });

      this.videoElement.srcObject = stream;
      await this.videoElement.play();

      this.faceMesh.onResults(config.onResults);

      this.camera = new Camera(this.videoElement, {
        onFrame: async () => {
          await this.faceMesh.send({ image: this.videoElement });
        },
        width: config.width || 640,
        height: config.height || 480
      });

      this.camera.start();
    } catch (error) {
      throw new Error(`Failed to start camera: ${error}`);
    }
  }

  stop(): void {
    if (this.camera) {
      this.camera.stop();
      this.camera = null;
    }

    if (this.videoElement.srcObject) {
      const stream = this.videoElement.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      this.videoElement.srcObject = null;
    }
  }

  isActive(): boolean {
    return this.camera !== null;
  }
}

