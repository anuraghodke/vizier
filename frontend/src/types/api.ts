/**
 * Type definitions for API requests and responses
 */

export interface JobStatus {
  job_id: string;
  status: 'pending' | 'processing' | 'complete' | 'failed';
  progress: number;
  stage?: string;
  frames?: string[];
  params?: AnimationParams;
  error?: string;
}

export interface AnimationParams {
  num_frames: number;
  motion_type: 'linear' | 'ease-in' | 'ease-out' | 'ease-in-out' | 'bounce' | 'elastic';
  speed: 'very-slow' | 'slow' | 'normal' | 'fast' | 'very-fast';
  emphasis: string;
  interpolation_times?: number[];
}

export interface GenerateRequest {
  frame1: File;
  frame2: File;
  instruction: string;
}

export interface GenerateResponse {
  job_id: string;
  status: string;
}
