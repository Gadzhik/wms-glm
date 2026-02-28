import { useEffect } from 'react';
import { recordingStore } from '@store/recordingStore';

export const useRecordings = (autoFetch = false) => {
  const {
    recordings,
    selectedRecording,
    timeline,
    isLoading,
    error,
    filters,
    fetchRecordings,
    fetchRecording,
    fetchCameraRecordings,
    fetchTimeline,
    getPlaybackUrl,
    exportRecording,
    fetchExportStatus,
    downloadExport,
    deleteRecording,
    fetchRecordingThumbnail,
    fetchRecordingStats,
    selectRecording,
    clearSelectedRecording,
    setFilters,
    clearFilters,
    clearError,
  } = recordingStore();

  // Автоматически загружаем записи при монтировании если указаны фильтры
  useEffect(() => {
    if (autoFetch && filters.cameraId && filters.startDate && filters.endDate) {
      fetchCameraRecordings(filters.cameraId, filters.startDate, filters.endDate);
    }
  }, [autoFetch, filters, fetchCameraRecordings]);

  const handleFetchRecordings = async (params = {}) => {
    return await fetchRecordings(params);
  };

  const handleFetchCameraRecordings = async (cameraId, startDate, endDate) => {
    setFilters({ cameraId, startDate, endDate });
    return await fetchCameraRecordings(cameraId, startDate, endDate);
  };

  const handleFetchTimeline = async (cameraId, startDate, endDate) => {
    return await fetchTimeline(cameraId, startDate, endDate);
  };

  const handleExportRecording = async (recordingId, startTime, endTime, format = 'mp4') => {
    return await exportRecording(recordingId, startTime, endTime, format);
  };

  const handleDownloadExport = async (exportId, filename) => {
    return await downloadExport(exportId, filename);
  };

  const handleDeleteRecording = async (recordingId) => {
    const result = await deleteRecording(recordingId);
    return result;
  };

  const getRecordingById = (recordingId) => {
    return recordings.find((recording) => recording.id === recordingId);
  };

  const getRecordingsByCamera = (cameraId) => {
    return recordings.filter((recording) => recording.camera_id === cameraId);
  };

  const getRecordingsByDate = (date) => {
    return recordings.filter((recording) => {
      const recordingDate = new Date(recording.start_time).toDateString();
      return recordingDate === date;
    });
  };

  const getRecordingsByType = (type) => {
    return recordings.filter((recording) => recording.type === type);
  };

  return {
    recordings,
    selectedRecording,
    timeline,
    isLoading,
    error,
    filters,
    fetchRecordings: handleFetchRecordings,
    fetchRecording,
    fetchCameraRecordings: handleFetchCameraRecordings,
    fetchTimeline: handleFetchTimeline,
    getPlaybackUrl,
    exportRecording: handleExportRecording,
    fetchExportStatus,
    downloadExport: handleDownloadExport,
    deleteRecording: handleDeleteRecording,
    fetchRecordingThumbnail,
    fetchRecordingStats,
    selectRecording,
    clearSelectedRecording,
    setFilters,
    clearFilters,
    clearError,
    getRecordingById,
    getRecordingsByCamera,
    getRecordingsByDate,
    getRecordingsByType,
  };
};
