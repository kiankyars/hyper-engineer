export interface GazeState {
  isLookingAtCamera: boolean;
  confidence: number;
}

export class EyeTracker {
  private smoothingFactor: number;
  private previousGazeState: GazeState | null = null;
  private debugMode: boolean = false;
  
  // State tracking for debouncing
  private consecutiveLookingFrames: number = 0;
  private consecutiveNotLookingFrames: number = 0;
  private readonly requiredFramesForChange: number = 5; // Require 5 consecutive frames to change state
  private currentStableState: boolean | null = null;

  // Blink detection
  private eyesClosedFrames: number = 0;
  private readonly blinkThresholdFrames: number = 3; // ~150ms at 30fps
  private isBlinking: boolean = false;

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
  private readonly FACE_CENTER = 10; // Forehead center

  // Fixed threshold for gaze detection (no longer configurable)
  private readonly GAZE_THRESHOLD = 0.08; // Fixed threshold for "looking at camera"
  private readonly EAR_CLOSED_THRESHOLD = 0.15; // Lower threshold for detecting closed eyes

  constructor(smoothingFactor: number = 0.85, debugMode: boolean = false) {
    this.smoothingFactor = smoothingFactor;
    this.debugMode = debugMode;
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
      const faceCenter = landmarks[this.FACE_CENTER] as { x: number; y: number; z: number };

      if (!leftEyeInner || !leftEyeOuter || !rightEyeInner || !rightEyeOuter || 
          !leftEyeTop || !leftEyeBottom || !rightEyeTop || !rightEyeBottom ||
          !leftIris || !rightIris || !noseTip || !faceCenter) {
        this.log('Missing required landmarks');
        return null;
      }

      // Check if eyes are open by calculating eye aspect ratio (EAR)
      const leftEyeHeight = Math.abs(leftEyeTop.y - leftEyeBottom.y);
      const leftEyeWidth = Math.abs(leftEyeInner.x - leftEyeOuter.x);
      const leftEAR = leftEyeWidth > 0 ? leftEyeHeight / leftEyeWidth : 0;

      const rightEyeHeight = Math.abs(rightEyeTop.y - rightEyeBottom.y);
      const rightEyeWidth = Math.abs(rightEyeInner.x - rightEyeOuter.x);
      const rightEAR = rightEyeWidth > 0 ? rightEyeHeight / rightEyeWidth : 0;

      const avgEAR = (leftEAR + rightEAR) / 2;

      // Detect blinks (sustained eye closure)
      if (avgEAR < this.EAR_CLOSED_THRESHOLD) {
        this.eyesClosedFrames++;
        if (this.eyesClosedFrames >= this.blinkThresholdFrames) {
          this.isBlinking = true;
        }
      } else {
        this.eyesClosedFrames = 0;
        this.isBlinking = false;
      }

      // If blinking, maintain previous state (don't change during blinks)
      if (this.isBlinking) {
        this.log('Blink detected, maintaining previous state');
        if (this.previousGazeState) {
          return this.previousGazeState;
        }
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

      // Method 1: Iris position relative to eye center (gaze direction)
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

      // Method 2: Face orientation (if face is turned, not looking at camera)
      const faceAngle = Math.atan2(
        (rightEyeCenter.x - leftEyeCenter.x),
        Math.abs(rightEyeCenter.y - leftEyeCenter.y)
      );
      const faceTurned = Math.abs(faceAngle) > 0.3; // Face turned significantly

      // Calculate gaze deviation from center (0,0 means looking straight at camera)
      const gazeDeviation = Math.sqrt(
        avgIrisOffset.x * avgIrisOffset.x + 
        avgIrisOffset.y * avgIrisOffset.y
      );

      // Combine multiple signals
      // If face is turned significantly, definitely not looking at camera
      if (faceTurned) {
        this.log('Face turned, not looking at camera');
        const isLooking = false;
        return this.updateStateWithDebouncing(isLooking, 0);
      }

      // Primary detection: iris position relative to eye center
      const isLookingAtCamera = gazeDeviation < this.GAZE_THRESHOLD;

      // Calculate confidence based on how close to center
      const confidence = Math.max(0, Math.min(1, 1 - (gazeDeviation / this.GAZE_THRESHOLD)));

      this.log(`Gaze deviation: ${gazeDeviation.toFixed(4)}, Looking: ${isLookingAtCamera}, Confidence: ${confidence.toFixed(3)}`);

      return this.updateStateWithDebouncing(isLookingAtCamera, confidence);
    } catch (error) {
      console.error('Error detecting gaze:', error);
      return null;
    }
  }

  private updateStateWithDebouncing(isLooking: boolean, confidence: number): GazeState {
    // Debouncing: require consecutive frames before changing state
    if (isLooking) {
      this.consecutiveLookingFrames++;
      this.consecutiveNotLookingFrames = 0;
    } else {
      this.consecutiveNotLookingFrames++;
      this.consecutiveLookingFrames = 0;
    }

    // Only change state if we have enough consecutive frames
    let stableLooking = this.currentStableState;
    if (this.currentStableState === null) {
      // Initialize
      stableLooking = isLooking;
      this.currentStableState = stableLooking;
    } else if (isLooking && this.consecutiveLookingFrames >= this.requiredFramesForChange) {
      stableLooking = true;
      this.currentStableState = true;
    } else if (!isLooking && this.consecutiveNotLookingFrames >= this.requiredFramesForChange) {
      stableLooking = false;
      this.currentStableState = false;
    } else {
      // Not enough consecutive frames, maintain current stable state
      stableLooking = this.currentStableState;
    }

    // Apply smoothing to confidence
    let finalConfidence = confidence;
    if (this.previousGazeState) {
      finalConfidence = this.previousGazeState.confidence * this.smoothingFactor + 
                       confidence * (1 - this.smoothingFactor);
    }

    const finalState: GazeState = {
      isLookingAtCamera: stableLooking,
      confidence: finalConfidence
    };

    this.previousGazeState = finalState;
    return finalState;
  }

  reset(): void {
    this.previousGazeState = null;
    this.currentStableState = null;
    this.consecutiveLookingFrames = 0;
    this.consecutiveNotLookingFrames = 0;
    this.eyesClosedFrames = 0;
    this.isBlinking = false;
  }
}
