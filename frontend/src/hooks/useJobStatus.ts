/**
 * Hook for polling job status
 */
import { useState, useEffect, useCallback } from 'react';
import { getJobStatus } from '../utils/api';
import { JobStatus } from '../types/api';

interface UseJobStatusResult {
  jobStatus: JobStatus | null;
  isPolling: boolean;
  error: string | null;
  startPolling: (jobId: string) => void;
  stopPolling: () => void;
}

export function useJobStatus(): UseJobStatusResult {
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pollInterval, setPollInterval] = useState<NodeJS.Timeout | null>(null);

  const stopPolling = useCallback(() => {
    if (pollInterval) {
      clearInterval(pollInterval);
      setPollInterval(null);
    }
    setIsPolling(false);
  }, [pollInterval]);

  const startPolling = useCallback((jobId: string) => {
    setIsPolling(true);
    setError(null);

    // Poll immediately
    const poll = async () => {
      try {
        const status = await getJobStatus(jobId);
        setJobStatus(status);

        // Stop polling if job is complete or failed
        if (status.status === 'complete' || status.status === 'failed') {
          stopPolling();
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch job status');
        stopPolling();
      }
    };

    // Initial poll
    poll();

    // Set up polling interval (every 2 seconds)
    const interval = setInterval(poll, 2000);
    setPollInterval(interval);
  }, [stopPolling]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, [pollInterval]);

  return {
    jobStatus,
    isPolling,
    error,
    startPolling,
    stopPolling,
  };
}
