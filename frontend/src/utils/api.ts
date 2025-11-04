/**
 * API client for communicating with Vizier backend
 */
import axios from 'axios';
import { JobStatus, GenerateResponse } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_URL = `${API_BASE_URL}/api`;

/**
 * Create axios instance with default config
 */
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Upload keyframes and instruction to generate animation
 */
export async function generateAnimation(
  frame1: File,
  frame2: File,
  instruction: string
): Promise<GenerateResponse> {
  const formData = new FormData();
  formData.append('frame1', frame1);
  formData.append('frame2', frame2);
  formData.append('instruction', instruction);

  const response = await apiClient.post<GenerateResponse>('/generate', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
}

/**
 * Poll job status
 */
export async function getJobStatus(jobId: string): Promise<JobStatus> {
  const response = await apiClient.get<JobStatus>(`/jobs/${jobId}`);
  return response.data;
}

/**
 * Get URL for individual frame
 */
export function getFrameUrl(jobId: string, frameName: string): string {
  return `${API_URL}/frames/${jobId}/${frameName}`;
}

/**
 * Get URL for ZIP download
 */
export function getDownloadUrl(jobId: string): string {
  return `${API_URL}/download/${jobId}`;
}

/**
 * Download frames as ZIP
 */
export async function downloadFrames(jobId: string): Promise<void> {
  const url = getDownloadUrl(jobId);
  window.open(url, '_blank');
}
