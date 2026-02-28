import { useEffect } from 'react';
import { cameraStore } from '@store/cameraStore';

export const useCameras = (autoFetch = true) => {
  const {
    cameras,
    selectedCamera,
    isLoading,
    error,
    filters,
    fetchCameras,
    fetchCamera,
    createCamera,
    updateCamera,
    deleteCamera,
    selectCamera,
    clearSelectedCamera,
    setFilters,
    clearFilters,
    clearError,
    getFilteredCameras,
  } = cameraStore();

  // Автоматически загружаем камеры при монтировании
  useEffect(() => {
    if (autoFetch && cameras.length === 0) {
      fetchCameras();
    }
  }, [autoFetch, cameras.length, fetchCameras]);

  const handleCreateCamera = async (cameraData) => {
    const result = await createCamera(cameraData);
    return result;
  };

  const handleUpdateCamera = async (cameraId, cameraData) => {
    const result = await updateCamera(cameraId, cameraData);
    return result;
  };

  const handleDeleteCamera = async (cameraId) => {
    const result = await deleteCamera(cameraId);
    return result;
  };

  const getCameraById = (cameraId) => {
    return cameras.find((camera) => camera.id === cameraId);
  };

  const getOnlineCameras = () => {
    return cameras.filter((camera) => camera.status === 'online');
  };

  const getOfflineCameras = () => {
    return cameras.filter((camera) => camera.status === 'offline');
  };

  const getErrorCameras = () => {
    return cameras.filter((camera) => camera.status === 'error');
  };

  return {
    cameras,
    selectedCamera,
    isLoading,
    error,
    filters,
    filteredCameras: getFilteredCameras(),
    fetchCameras,
    fetchCamera,
    createCamera: handleCreateCamera,
    updateCamera: handleUpdateCamera,
    deleteCamera: handleDeleteCamera,
    selectCamera,
    clearSelectedCamera,
    setFilters,
    clearFilters,
    clearError,
    getCameraById,
    getOnlineCameras,
    getOfflineCameras,
    getErrorCameras,
  };
};
