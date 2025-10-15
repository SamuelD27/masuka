from abc import ABC, abstractmethod
from typing import Callable, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class BaseTrainer(ABC):
    """Abstract base class for all trainers."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dataset_path = config.get('dataset_path')
        self.output_path = config.get('output_path')

    @abstractmethod
    def train(self, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Train the model.

        Args:
            progress_callback: Function(step, total_steps, loss) called during training

        Returns:
            Dict with training results including model_path
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate training configuration."""
        pass
