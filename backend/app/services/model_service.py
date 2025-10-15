from pathlib import Path
from typing import Optional, Dict, Any
import logging
from app.services.storage_service import storage_service
from app.generators.flux_generator import FluxGenerator

logger = logging.getLogger(__name__)

class ModelService:
    """Manage model loading, caching, and lifecycle."""

    def __init__(self):
        self.loaded_generators: Dict[str, FluxGenerator] = {}
        self.cache_dir = Path("/tmp/masuka/model_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

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
        Download model from storage to local cache.

        Args:
            storage_path: S3/R2 path to model

        Returns:
            Local path to downloaded model
        """
        filename = Path(storage_path).name
        local_path = self.cache_dir / filename

        # Check if already cached
        if local_path.exists():
            logger.info(f"Model already cached at {local_path}")
            return str(local_path)

        # Download from storage
        logger.info(f"Downloading model from {storage_path}")
        success = storage_service.download_file(storage_path, str(local_path))

        if not success:
            raise Exception(f"Failed to download model from {storage_path}")

        logger.info(f"Model downloaded to {local_path}")
        return str(local_path)

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
