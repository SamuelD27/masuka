from pathlib import Path
from typing import Optional, Dict, Any
import logging
import fcntl
import time
import shutil
import os
from app.services.storage_service import storage_service
from app.generators.flux_generator import FluxGenerator

logger = logging.getLogger(__name__)

class ModelService:
    """Manage model loading, caching, and lifecycle."""

    def __init__(self):
        self.loaded_generators: Dict[str, FluxGenerator] = {}
        self.cache_dir = Path("/tmp/masuka/model_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.min_free_space_gb = 15  # Minimum free space required
        self.max_cache_size_gb = 50  # Maximum cache size before LRU eviction

    def _get_disk_space(self) -> Dict[str, float]:
        """Get disk space information in GB."""
        stat = shutil.disk_usage(self.cache_dir)
        return {
            'total_gb': stat.total / (1024**3),
            'used_gb': stat.used / (1024**3),
            'free_gb': stat.free / (1024**3)
        }

    def _get_cache_size(self) -> float:
        """Get total cache size in GB."""
        total_size = 0
        for file in self.cache_dir.rglob('*'):
            if file.is_file():
                total_size += file.stat().st_size
        return total_size / (1024**3)

    def _evict_lru_models(self, target_free_gb: float = 15):
        """Evict least recently used models to free space."""
        logger.info(f"Evicting LRU models to free {target_free_gb}GB")

        # Get all model files with access times
        model_files = []
        for file in self.cache_dir.rglob('*.safetensors'):
            if file.is_file():
                stat = file.stat()
                model_files.append({
                    'path': file,
                    'size_gb': stat.st_size / (1024**3),
                    'atime': stat.st_atime
                })

        # Sort by access time (oldest first)
        model_files.sort(key=lambda x: x['atime'])

        # Evict until we have enough space
        freed_gb = 0
        space_info = self._get_disk_space()

        for model in model_files:
            if space_info['free_gb'] + freed_gb >= target_free_gb:
                break

            try:
                model['path'].unlink()
                freed_gb += model['size_gb']
                logger.info(f"Evicted {model['path'].name} ({model['size_gb']:.2f}GB)")
            except Exception as e:
                logger.error(f"Failed to evict {model['path'].name}: {e}")

        logger.info(f"Freed {freed_gb:.2f}GB from cache")

    def _check_disk_space(self, required_gb: float = 15):
        """Check if sufficient disk space is available."""
        space_info = self._get_disk_space()
        cache_size = self._get_cache_size()

        logger.info(f"Disk space: {space_info['free_gb']:.2f}GB free, cache: {cache_size:.2f}GB")

        # Check if we need to evict based on free space
        if space_info['free_gb'] < required_gb:
            logger.warning(f"Low disk space: {space_info['free_gb']:.2f}GB < {required_gb}GB")
            self._evict_lru_models(required_gb)

            # Re-check after eviction
            space_info = self._get_disk_space()
            if space_info['free_gb'] < required_gb:
                raise Exception(
                    f"Insufficient disk space: {space_info['free_gb']:.2f}GB free, "
                    f"need {required_gb}GB"
                )

        # Check if cache is too large
        if cache_size > self.max_cache_size_gb:
            logger.warning(f"Cache too large: {cache_size:.2f}GB > {self.max_cache_size_gb}GB")
            self._evict_lru_models(self.min_free_space_gb)

    def get_generator(
        self,
        model_type: str = 'flux',
        config: Optional[Dict[str, Any]] = None
    ) -> FluxGenerator:
        """
        Get or create a generator instance.

        Args:
            model_type: Type of generator ('flux', 'sd', etc.)
            config: Generator configuration

        Returns:
            Generator instance
        """
        if model_type not in self.loaded_generators:
            logger.info(f"Creating new {model_type} generator")

            if model_type == 'flux':
                config = config or {}
                generator = FluxGenerator(config)
                generator.load_model()
                self.loaded_generators[model_type] = generator
            else:
                raise ValueError(f"Unsupported model type: {model_type}")

        return self.loaded_generators[model_type]

    def download_model(self, storage_path: str) -> str:
        """
        Download model from storage to local cache with file locking.

        Args:
            storage_path: S3/R2 path to model

        Returns:
            Local path to downloaded model
        """
        filename = Path(storage_path).name
        local_path = self.cache_dir / filename
        lock_path = self.cache_dir / f"{filename}.lock"

        # Create lock file
        lock_file = open(lock_path, 'w')

        try:
            # Try to acquire exclusive lock
            logger.info(f"Acquiring lock for {filename}")
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)

            # Check if already cached (after acquiring lock)
            if local_path.exists():
                logger.info(f"Model already cached at {local_path}")
                # Update access time for LRU
                os.utime(local_path, None)
                return str(local_path)

            # Check disk space before downloading
            self._check_disk_space(self.min_free_space_gb)

            # Download from storage
            logger.info(f"Downloading model from {storage_path}")
            success = storage_service.download_file(storage_path, str(local_path))

            if not success:
                raise Exception(f"Failed to download model from {storage_path}")

            logger.info(f"Model downloaded to {local_path}")
            return str(local_path)

        finally:
            # Release lock and close file
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            lock_file.close()

            # Clean up lock file
            try:
                lock_path.unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"Failed to remove lock file: {e}")

    def load_lora_for_generation(
        self,
        model_id: str,
        storage_path: str,
        weight: float = 0.8
    ) -> FluxGenerator:
        """
        Load a LoRA model for generation.

        Args:
            model_id: Model ID for tracking
            storage_path: S3/R2 path to LoRA
            weight: LoRA weight

        Returns:
            Generator with LoRA loaded
        """
        # Download LoRA to cache
        local_lora_path = self.download_model(storage_path)

        # Get generator
        generator = self.get_generator('flux')

        # Unload existing LoRA if any
        if generator.lora_loaded:
            generator.unload_lora()

        # Load new LoRA
        generator.load_lora(local_lora_path, weight)

        return generator

    def unload_all(self):
        """Unload all generators to free memory."""
        logger.info("Unloading all generators")
        for model_type, generator in self.loaded_generators.items():
            generator.unload_model()

        self.loaded_generators.clear()
        logger.info("All generators unloaded")

    def clear_cache(self):
        """Clear downloaded model cache."""
        import shutil
        logger.info("Clearing model cache")
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Model cache cleared")

# Global instance
model_service = ModelService()
