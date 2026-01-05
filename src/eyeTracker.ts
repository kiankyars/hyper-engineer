export interface EyeLandmarks {
  leftEye: { x: number; y: number; z: number };
  rightEye: { x: number; y: number; z: number };
  leftIris: { x: number; y: number; z: number };
  rightIris: { x: number; y: number; z: number };
  faceCenter: { x: number; y: number; z: number };
}

export interface GazeState {
  isLookingAtCamera: boolean;
  confidence: number;
}

export class EyeTracker {
  private sensitivity: number;
  private smoothingFactor: number;
  private previousGazeState: GazeState | null = null;
  private debugMode: boolean = false;

  // MediaPipe Face Mesh landmark indices
  private readonly LEFT_EYE_INNER = 33;
  private readonly LEFT_EYE_OUTER = 133;
  private readonly LEFT_EYE_TOP = 159;
  private readonly LEFT_EYE_BOTTOM = 145;
  private readonly RIGHT_EYE_INNER = 362;
  private readonly RIGHT_EYE_OUTER = 263;
  private readonly RIGHT_EYE_TOP = 386;
  private readonly RIGHT_EYE_BOTTOM = 374;
  private readonly LEFT_IRIS = 468;
  private readonly RIGHT_IRIS = 473;
  private readonly NOSE_TIP = 4;

  constructor(sensitivity: number = 0.15, smoothingFactor: number = 0.7, debugMode: boolean = false) {
    this.sensitivity = sensitivity;
    this.smoothingFactor = smoothingFactor;
    this.debugMode = debugMode;
  }

  setSensitivity(sensitivity: number): void {
    this.sensitivity = Math.max(0.05, Math.min(0.5, sensitivity));
  }

  setDebugMode(enabled: boolean): void {
    this.debugMode = enabled;
  }

  private log(message: string, ...args: any[]): void {
    if (this.debugMode) {
      console.log(`[EyeTracker] ${message}`, ...args);
    }
  }

  detectGaze(landmarks: any[]): GazeState | null {
    if (!landmarks || landmarks.length === 0) {
      this.log('No landmarks provided');
      return null;
    }

    this.log(`Processing ${landmarks.length} landmarks`);

    try {
      const leftEyeInner = landmarks[this.LEFT_EYE_INNER] as { x: number; y: number; z: number };
      const leftEyeOuter = landmarks[this.LEFT_EYE_OUTER] as { x: number; y: number; z: number };
      const leftEyeTop = landmarks[this.LEFT_EYE_TOP] as { x: number; y: number; z: number };
      const leftEyeBottom = landmarks[this.LEFT_EYE_BOTTOM] as { x: number; y: number; z: number };
      const rightEyeInner = landmarks[this.RIGHT_EYE_INNER] as { x: number; y: number; z: number };
      const rightEyeOuter = landmarks[this.RIGHT_EYE_OUTER] as { x: number; y: number; z: number };
      const rightEyeTop = landmarks[this.RIGHT_EYE_TOP] as { x: number; y: number; z: number };
      const rightEyeBottom = landmarks[this.RIGHT_EYE_BOTTOM] as { x: number; y: number; z: number };
      const leftIris = landmarks[this.LEFT_IRIS] as { x: number; y: number; z: number };
      const rightIris = landmarks[this.RIGHT_IRIS] as { x: number; y: number; z: number };
      const noseTip = landmarks[this.NOSE_TIP] as { x: number; y: number; z: number };

      if (!leftEyeInner || !leftEyeOuter || !rightEyeInner || !rightEyeOuter || 
          !leftEyeTop || !leftEyeBottom || !rightEyeTop || !rightEyeBottom ||
          !leftIris || !rightIris || !noseTip) {
        this.log('Missing required landmarks');
        return null;
      }

      // Check if eyes are open by calculating eye aspect ratio (EAR)
      const leftEyeHeight = Math.abs(leftEyeTop.y - leftEyeBottom.y);
      const leftEyeWidth = Math.abs(leftEyeInner.x - leftEyeOuter.x);
      const leftEAR = leftEyeHeight / leftEyeWidth;

      const rightEyeHeight = Math.abs(rightEyeTop.y - rightEyeBottom.y);
      const rightEyeWidth = Math.abs(rightEyeInner.x - rightEyeOuter.x);
      const rightEAR = rightEyeHeight / rightEyeWidth;

      const avgEAR = (leftEAR + rightEAR) / 2;
      const eyeOpenThreshold = 0.2; // Eyes are considered closed if EAR < 0.2

      this.log(`Eye Aspect Ratio: ${avgEAR.toFixed(3)} (left: ${leftEAR.toFixed(3)}, right: ${rightEAR.toFixed(3)})`);

      if (avgEAR < eyeOpenThreshold) {
        this.log('Eyes detected as closed');
        return { isLookingAtCamera: false, confidence: 0 };
      }

      // Calculate eye centers
      const leftEyeCenter = {
        x: (leftEyeInner.x + leftEyeOuter.x) / 2,
        y: (leftEyeInner.y + leftEyeOuter.y) / 2,
        z: (leftEyeInner.z + leftEyeOuter.z) / 2
      };

      const rightEyeCenter = {
        x: (rightEyeInner.x + rightEyeOuter.x) / 2,
        y: (rightEyeInner.y + rightEyeOuter.y) / 2,
        z: (rightEyeInner.z + rightEyeOuter.z) / 2
      };

      // Calculate iris offset from eye center (gaze direction indicator)
      const leftIrisOffset = {
        x: leftIris.x - leftEyeCenter.x,
        y: leftIris.y - leftEyeCenter.y
      };

      const rightIrisOffset = {
        x: rightIris.x - rightEyeCenter.x,
        y: rightIris.y - rightEyeCenter.y
      };

      // Average the offsets for both eyes
      const avgIrisOffset = {
        x: (leftIrisOffset.x + rightIrisOffset.x) / 2,
        y: (leftIrisOffset.y + rightIrisOffset.y) / 2
      };

      // Calculate distance from center (0,0 means looking straight at camera)
      const gazeDeviation = Math.sqrt(
        avgIrisOffset.x * avgIrisOffset.x + 
        avgIrisOffset.y * avgIrisOffset.y
      );

      this.log(`Gaze deviation: ${gazeDeviation.toFixed(4)}, Sensitivity: ${this.sensitivity.toFixed(4)}`);

      // Determine if looking at camera based on sensitivity threshold
      // Higher sensitivity value = more lenient (allows more deviation)
      // Lower sensitivity value = more strict (less deviation allowed)
      const isLookingAtCamera = gazeDeviation < this.sensitivity;

      // Calculate confidence based on how close to center
      const confidence = Math.max(0, Math.min(1, 1 - (gazeDeviation / this.sensitivity)));

      this.log(`Looking at camera: ${isLookingAtCamera}, Confidence: ${confidence.toFixed(3)}`);

      // Apply smoothing to reduce jitter
      let finalState: GazeState;
      if (this.previousGazeState) {
        const smoothedLooking = (this.previousGazeState.isLookingAtCamera ? 1 : 0) * this.smoothingFactor + 
                               (isLookingAtCamera ? 1 : 0) * (1 - this.smoothingFactor);
        finalState = {
          isLookingAtCamera: smoothedLooking > 0.5,
          confidence: this.previousGazeState.confidence * this.smoothingFactor + 
                     confidence * (1 - this.smoothingFactor)
        };
      } else {
        finalState = { isLookingAtCamera, confidence };
      }

      this.previousGazeState = finalState;
      return finalState;
    } catch (error) {
      console.error('Error detecting gaze:', error);
      return null;
    }
  }

  reset(): void {
    this.previousGazeState = null;
  }
}

