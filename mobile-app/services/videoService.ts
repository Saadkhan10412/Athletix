/**
 * ATHLETIX — Video Service
 * mobile-app/services/videoService.ts
 *
 * Cross-platform (Web, iOS, Android) video upload, management, and assessment retrieval service.
 *
 * Key Functionalities:
 * - Binary Blob & Multipart Form Handling: Normalizes local video files across web blobs and native file URIs.
 * - Upload Progress Tracking: Streams byte upload percentage events back to UI progress indicators.
 * - Video Lifecycle Management: Fetches athlete submission history, detailed AI assessment scorecards,
 *   retries failed analysis jobs, and deletes attempts.
 */

import { Platform } from 'react-native';
import type { AxiosRequestConfig } from 'axios';

import api from './api';

export interface VideoRecord {
  id: string;
  athlete_id: string;
  sport: string;
  exercise: string;
  video_url: string;
  cloudinary_public_id?: string | null;
  duration_seconds: number;
  status:
  | 'pending'
  | 'processing'
  | 'completed'
  | 'failed';
  error_msg?: string | null;
  uploaded_at: string;
  assessments?: AssessmentRecord[];
}

export interface AssessmentRecord {
  id: string;
  video_id: string;
  score: number;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  rep_count?: number | null;
  created_at: string;
  videos?: VideoRecord;
}

export interface UploadVideoPayload {
  uri: string;
  name: string;
  type: string;
  sport: string;
  exercise: string;
  durationSeconds?: number;
}

/**
 * Converts a web blob URI into a standard browser Blob instance for multipart upload.
 */
async function createWebVideoBlob(
  uri: string,
  mimeType: string,
): Promise<Blob> {
  const response = await fetch(uri);

  if (!response.ok) {
    throw new Error(
      `Selected video could not be read (${response.status}).`,
    );
  }

  const blob = await response.blob();

  if (blob.size === 0) {
    throw new Error('Selected video file is empty.');
  }

  if (!blob.type && mimeType) {
    return new Blob([blob], {
      type: mimeType,
    });
  }

  return blob;
}

/**
 * Submits an exercise video attempt to the FastAPI backend for storage and MediaPipe AI evaluation.
 *
 * @param payload - Video file metadata, sport category, and exercise type.
 * @param onProgress - Optional callback receiving upload progress percentages (0 - 100).
 */
export async function uploadVideoAttempt(
  payload: UploadVideoPayload,
  onProgress?: (percent: number) => void,
): Promise<{
  id: string;
  status: string;
  message: string;
}> {
  if (!payload.uri.trim()) {
    throw new Error('Please select a video file.');
  }

  if (!payload.sport.trim()) {
    throw new Error('Please select a sport.');
  }

  if (!payload.exercise.trim()) {
    throw new Error('Please select an exercise.');
  }

  const fileName = payload.name?.trim() || 'attempt.mp4';
  const mimeType = payload.type?.trim() || 'video/mp4';
  const formData = new FormData();

  if (Platform.OS === 'web') {
    // Web platform requires standard browser Blob object
    const videoBlob = await createWebVideoBlob(
      payload.uri,
      mimeType,
    );

    formData.append(
      'file',
      videoBlob,
      fileName,
    );
  } else {
    // React Native iOS/Android native file dictionary structure
    formData.append(
      'file',
      {
        uri: payload.uri,
        name: fileName,
        type: mimeType,
      } as any,
    );
  }

  formData.append(
    'sport',
    payload.sport.trim().toLowerCase(),
  );

  formData.append(
    'exercise',
    payload.exercise.trim().toLowerCase(),
  );

  if (
    typeof payload.durationSeconds === 'number' &&
    payload.durationSeconds > 0
  ) {
    formData.append(
      'duration_seconds',
      String(payload.durationSeconds),
    );
  }

  const config: AxiosRequestConfig = {
    // 3-minute timeout to accommodate large high-definition video uploads
    timeout: 180_000,

    onUploadProgress: (progressEvent) => {
      if (!onProgress || !progressEvent.total) {
        return;
      }

      const percent = Math.min(
        100,
        Math.round(
          (progressEvent.loaded * 100) / progressEvent.total,
        ),
      );

      onProgress(percent);
    },
  };

  if (Platform.OS !== 'web') {
    config.headers = {
      'Content-Type': 'multipart/form-data',
    };
  }

  const response = await api.post(
    '/videos/upload',
    formData,
    config,
  );

  const data = response.data?.data;

  if (!data?.id) {
    throw new Error('Backend returned an invalid video upload response.');
  }

  return {
    id: String(data.id),
    status:
      typeof data.status === 'string'
        ? data.status
        : 'pending',
    message:
      typeof data.message === 'string'
        ? data.message
        : 'Video uploaded successfully.',
  };
}

/**
 * Retrieves all assessment video submissions uploaded by the authenticated athlete.
 */
export async function getMyVideos(): Promise<VideoRecord[]> {
  const response = await api.get('/videos');

  return Array.isArray(response.data?.data)
    ? response.data.data
    : [];
}

/**
 * Fetches detailed assessment information for a specific video submission.
 */
export async function getVideoDetail(videoId: string): Promise<VideoRecord> {
  if (!videoId.trim()) {
    throw new Error('Video ID is required.');
  }

  const response = await api.get(`/videos/${videoId}`);
  return response.data.data;
}

/**
 * Triggers re-analysis of a video attempt if initial AI processing encountered errors.
 */
export async function retryVideoAnalysis(videoId: string): Promise<{
  message: string;
  video_id: string;
}> {
  if (!videoId.trim()) {
    throw new Error('Video ID is required.');
  }

  const response = await api.post(`/videos/${videoId}/retry`);
  return response.data.data;
}

/**
 * Permanently deletes a video submission along with its associated AI assessment data.
 */
export async function deleteVideoAttempt(videoId: string): Promise<void> {
  if (!videoId.trim()) {
    throw new Error('Video ID is required.');
  }

  await api.delete(`/videos/${videoId}`);
}