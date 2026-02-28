"""Storage service for file management and cleanup"""
import os
import shutil
from typing import Optional, Tuple
from datetime import datetime, timedelta

from app.config import settings


class StorageService:
    """Storage management service"""
    
    def __init__(self):
        """Initialize storage service"""
        self.base_path = settings.STORAGE_PATH
        self.recordings_path = settings.RECORDINGS_PATH
        self.archive_path = settings.ARCHIVE_PATH
        self.exports_path = settings.EXPORTS_PATH
        self.live_stream_path = settings.LIVE_STREAM_PATH
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Ensure all storage directories exist"""
        for path in [
            self.base_path,
            self.recordings_path,
            self.archive_path,
            self.exports_path,
            self.live_stream_path,
        ]:
            os.makedirs(path, exist_ok=True)
    
    def get_disk_usage(self) -> dict:
        """Get disk usage information
        
        Returns:
            Dictionary with disk usage info
        """
        try:
            usage = shutil.disk_usage(self.base_path)
            
            return {
                "total_bytes": usage.total,
                "used_bytes": usage.used,
                "free_bytes": usage.free,
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "usage_percent": round((usage.used / usage.total) * 100, 2),
            }
        except Exception as e:
            print(f"Failed to get disk usage: {e}")
            return {
                "total_bytes": 0,
                "used_bytes": 0,
                "free_bytes": 0,
                "total_gb": 0,
                "used_gb": 0,
                "free_gb": 0,
                "usage_percent": 0,
            }
    
    def check_storage_space(self, required_bytes: int) -> Tuple[bool, str]:
        """Check if there's enough storage space
        
        Args:
            required_bytes: Required space in bytes
            
        Returns:
            Tuple of (has_space, message)
        """
        usage = self.get_disk_usage()
        
        if usage["free_bytes"] < required_bytes:
            return False, f"Not enough space. Required: {required_bytes} bytes, Available: {usage['free_bytes']} bytes"
        
        # Check if usage exceeds threshold
        max_bytes = settings.MAX_DISK_USAGE_GB * (1024**3)
        if usage["used_bytes"] + required_bytes > max_bytes:
            return False, f"Storage would exceed maximum ({settings.MAX_DISK_USAGE_GB} GB)"
        
        return True, "Sufficient space available"
    
    def get_recordings_size(self) -> int:
        """Get total size of recordings
        
        Returns:
            Size in bytes
        """
        total_size = 0
        
        try:
            for root, dirs, files in os.walk(self.recordings_path):
                for file in files:
                    filepath = os.path.join(root, file)
                    total_size += os.path.getsize(filepath)
        except Exception as e:
            print(f"Failed to calculate recordings size: {e}")
        
        return total_size
    
    def get_recordings_count(self) -> int:
        """Get total number of recording files
        
        Returns:
            Number of files
        """
        count = 0
        
        try:
            for root, dirs, files in os.walk(self.recordings_path):
                count += len(files)
        except Exception as e:
            print(f"Failed to count recordings: {e}")
        
        return count
    
    async def cleanup_old_files(
        self,
        retention_days: Optional[int] = None,
        dry_run: bool = False,
    ) -> dict:
        """Cleanup old files based on retention policy
        
        Args:
            retention_days: Retention period in days (default from settings)
            dry_run: If True, don't actually delete files
            
        Returns:
            Dictionary with cleanup results
        """
        if retention_days is None:
            retention_days = settings.RETENTION_DAYS
        
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        cutoff_timestamp = cutoff_date.timestamp()
        
        deleted_files = []
        freed_bytes = 0
        
        try:
            # Cleanup recordings
            for root, dirs, files in os.walk(self.recordings_path):
                for file in files:
                    filepath = os.path.join(root, file)
                    
                    try:
                        file_mtime = os.path.getmtime(filepath)
                        
                        if file_mtime < cutoff_timestamp:
                            file_size = os.path.getsize(filepath)
                            
                            if not dry_run:
                                os.remove(filepath)
                            
                            deleted_files.append(filepath)
                            freed_bytes += file_size
                            
                    except Exception as e:
                        print(f"Failed to process file {filepath}: {e}")
            
            # Cleanup exports
            for root, dirs, files in os.walk(self.exports_path):
                for file in files:
                    filepath = os.path.join(root, file)
                    
                    try:
                        file_mtime = os.path.getmtime(filepath)
                        
                        if file_mtime < cutoff_timestamp:
                            file_size = os.path.getsize(filepath)
                            
                            if not dry_run:
                                os.remove(filepath)
                            
                            deleted_files.append(filepath)
                            freed_bytes += file_size
                            
                    except Exception as e:
                        print(f"Failed to process file {filepath}: {e}")
        
        except Exception as e:
            print(f"Cleanup failed: {e}")
        
        return {
            "deleted_files": len(deleted_files),
            "freed_bytes": freed_bytes,
            "freed_gb": round(freed_bytes / (1024**3), 2),
            "dry_run": dry_run,
            "retention_days": retention_days,
        }
    
    async def cleanup_if_needed(self) -> dict:
        """Cleanup if storage is above threshold
        
        Returns:
            Dictionary with cleanup results
        """
        usage = self.get_disk_usage()
        threshold_percent = 90
        
        if usage["usage_percent"] < threshold_percent:
            return {
                "cleanup_needed": False,
                "usage_percent": usage["usage_percent"],
            }
        
        # Cleanup is needed
        return await self.cleanup_old_files()
    
    def get_camera_recordings_path(self, camera_id: int) -> str:
        """Get recordings path for specific camera
        
        Args:
            camera_id: Camera ID
            
        Returns:
            Path to camera recordings
        """
        return os.path.join(self.recordings_path, str(camera_id))
    
    def get_camera_live_path(self, camera_id: int) -> str:
        """Get live stream path for specific camera
        
        Args:
            camera_id: Camera ID
            
        Returns:
            Path to camera live stream
        """
        return os.path.join(self.live_stream_path, str(camera_id))
    
    def get_export_path(self, export_id: str) -> str:
        """Get export path for specific export
        
        Args:
            export_id: Export ID
            
        Returns:
            Path to export file
        """
        return os.path.join(self.exports_path, f"{export_id}.mp4")
    
    def move_to_archive(
        self,
        source_path: str,
        camera_id: int,
        date: Optional[str] = None,
    ) -> Optional[str]:
        """Move recording to archive
        
        Args:
            source_path: Source file path
            camera_id: Camera ID
            date: Recording date (default: today)
            
        Returns:
            Archive file path or None
        """
        try:
            if date is None:
                date = datetime.utcnow().strftime("%Y-%m-%d")
            
            archive_dir = os.path.join(self.archive_path, str(camera_id), date)
            os.makedirs(archive_dir, exist_ok=True)
            
            filename = os.path.basename(source_path)
            dest_path = os.path.join(archive_dir, filename)
            
            shutil.move(source_path, dest_path)
            
            return dest_path
            
        except Exception as e:
            print(f"Failed to move to archive: {e}")
            return None
    
    def delete_file(self, filepath: str) -> bool:
        """Delete a file
        
        Args:
            filepath: Path to file
            
        Returns:
            True if deleted
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            print(f"Failed to delete file {filepath}: {e}")
            return False


# Global storage service instance
storage_service = StorageService()


# Convenience functions
async def cleanup_old_files(
    retention_days: Optional[int] = None,
    dry_run: bool = False,
) -> dict:
    """Cleanup old files"""
    return await storage_service.cleanup_old_files(retention_days, dry_run)


def get_disk_usage() -> dict:
    """Get disk usage"""
    return storage_service.get_disk_usage()


def check_storage_space(required_bytes: int) -> Tuple[bool, str]:
    """Check storage space"""
    return storage_service.check_storage_space(required_bytes)
