import { useEffect } from 'react';
import { eventStore } from '@store/eventStore';

export const useEvents = (autoFetch = true) => {
  const {
    events,
    selectedEvent,
    isLoading,
    error,
    filters,
    fetchEvents,
    fetchEvent,
    fetchCameraEvents,
    fetchEventsByType,
    fetchEventsByPeriod,
    fetchEventThumbnail,
    fetchEventVideo,
    markAsViewed,
    markManyAsViewed,
    fetchEventStats,
    deleteEvent,
    selectEvent,
    clearSelectedEvent,
    setFilters,
    clearFilters,
    addEvent,
    updateEvent,
    clearError,
  } = eventStore();

  // Автоматически загружаем события при монтировании
  useEffect(() => {
    if (autoFetch && events.length === 0) {
      fetchEvents();
    }
  }, [autoFetch, events.length, fetchEvents]);

  const getEventById = (eventId) => {
    return events.find((event) => event.id === eventId);
  };

  const getEventsByCamera = (cameraId) => {
    return events.filter((event) => event.cameraId === cameraId);
  };

  const getEventsByType = (eventType) => {
    return events.filter((event) => event.eventType === eventType);
  };

  const getUnviewedEvents = () => {
    return events.filter((event) => !event.viewed);
  };

  const getRecentEvents = (limit = 10) => {
    return events.slice(0, limit);
  };

  return {
    events,
    selectedEvent,
    isLoading,
    error,
    filters,
    fetchEvents,
    fetchEvent,
    fetchCameraEvents,
    fetchEventsByType,
    fetchEventsByPeriod,
    fetchEventThumbnail,
    fetchEventVideo,
    markAsViewed,
    markManyAsViewed,
    fetchEventStats,
    deleteEvent,
    selectEvent,
    clearSelectedEvent,
    setFilters,
    clearFilters,
    addEvent,
    updateEvent,
    clearError,
    getEventById,
    getEventsByCamera,
    getEventsByType,
    getUnviewedEvents,
    getRecentEvents,
  };
};
