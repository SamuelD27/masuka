from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseGenerator(ABC):
    """Abstract base class for all generators."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = None
        self.device = config.get('device', 'cuda')

    @abstractmethod
    def load_model(self):
        """Load the base model."""
        pass

    @abstractmethod
    def load_lora(self, lora_path: str, weight: float = 0.8):
        """Load a LoRA adapter."""
        pass

    @abstractmethod
    def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_images: int = 1,
        **kwargs
    ) -> List[str]:
        """
        Generate images.

        Args:
            prompt: Text prompt
            negative_prompt: Negative prompt
            num_images: Number of images to generate
            **kwargs: Additional generation parameters

        Returns:
            List of file paths to generated images
        """
        pass

    @abstractmethod
    def unload_model(self):
        """Unload model to free memory."""
        pass
