import subprocess
import os
import yaml
import logging
import re
from pathlib import Path
from typing import Callable, Optional, Dict, Any
from app.trainers.base_trainer import BaseTrainer
from app.config import settings

logger = logging.getLogger(__name__)

class FluxTrainer(BaseTrainer):
    """Wrapper for SimpleTuner to train Flux LoRAs."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        # Training parameters with defaults
        self.learning_rate = config.get('learning_rate', settings.DEFAULT_FLUX_LEARNING_RATE)
        self.steps = config.get('steps', settings.DEFAULT_FLUX_STEPS)
        self.network_dim = config.get('network_dim', settings.DEFAULT_FLUX_RANK)
        self.network_alpha = config.get('network_alpha', settings.DEFAULT_FLUX_ALPHA)
        self.resolution = config.get('resolution', settings.DEFAULT_RESOLUTION)
        self.trigger_word = config.get('trigger_word', '')
        self.save_every_n_steps = config.get('save_every_n_steps', 250)

        # Paths
        self.simpletuner_path = Path(settings.SIMPLETUNER_PATH)
        self.config_path = Path(self.output_path) / 'training_config.yaml'

        logger.info(f"FluxTrainer initialized: LR={self.learning_rate}, Steps={self.steps}, Rank={self.network_dim}")

    def validate_config(self) -> bool:
        """Validate training configuration."""
        if not self.dataset_path or not os.path.exists(self.dataset_path):
            logger.error(f"Dataset path does not exist: {self.dataset_path}")
            return False

        if not self.output_path:
            logger.error("Output path not specified")
            return False

        if not self.simpletuner_path.exists():
            logger.error(f"SimpleTuner not found at {self.simpletuner_path}")
            return False

        # Check for images in dataset
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        images = [f for f in Path(self.dataset_path).glob('*') if f.suffix.lower() in image_extensions]
        if len(images) == 0:
            logger.error("No images found in dataset")
            return False

        logger.info(f"Found {len(images)} images in dataset")
        return True

    def create_config(self) -> str:
        """Create SimpleTuner YAML configuration file."""
        config_dict = {
            'model': {
                'name_or_path': 'black-forest-labs/FLUX.1-dev',
                'is_flux': True,
                'quantize': True,
                'quantize_dtype': 'fp8',
            },
            'train': {
                'learning_rate': self.learning_rate,
                'lr_scheduler': 'constant_with_warmup',
                'lr_warmup_steps': 100,
                'optimizer': 'adamw8bit',
                'num_train_epochs': 1,
                'max_train_steps': self.steps,
                'save_steps': self.save_every_n_steps,
                'gradient_accumulation_steps': 1,
                'mixed_precision': 'bf16',
                'gradient_checkpointing': True,
            },
            'network': {
                'type': 'lora',
                'rank': self.network_dim,
                'alpha': self.network_alpha,
                'dropout': 0.0,
                'target_modules': ['to_q', 'to_k', 'to_v', 'to_out.0'],
            },
            'data': {
                'dataset_path': str(self.dataset_path),
                'resolution': self.resolution,
                'caption_ext': 'txt',
                'cache_latents': True,
                'batch_size': 1,
                'num_workers': 2,
            },
            'output': {
                'output_dir': str(self.output_path),
                'save_precision': 'bf16',
                'logging_dir': str(Path(self.output_path) / 'logs'),
            },
        }

        # Create output directory
        Path(self.output_path).mkdir(parents=True, exist_ok=True)

        # Write config
        with open(self.config_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)

        logger.info(f"Created training config at {self.config_path}")
        return str(self.config_path)

    def train(self, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Train Flux LoRA using SimpleTuner.

        Args:
            progress_callback: Function(step, total_steps, loss) called during training

        Returns:
            Dict with model_path and checkpoint paths
        """
        # Validate configuration
        if not self.validate_config():
            raise ValueError("Invalid training configuration")

        # Create config file
        config_path = self.create_config()

        # Build command - SimpleTuner's train script is in simpletuner_sdk subdirectory
        train_script = self.simpletuner_path / 'simpletuner_sdk' / 'train.py'

        # Check if train script exists
        if not train_script.exists():
            # Try old location as fallback
            train_script_old = self.simpletuner_path / 'train.py'
            if train_script_old.exists():
                train_script = train_script_old
            else:
                raise FileNotFoundError(
                    f"SimpleTuner train script not found at {train_script} or {train_script_old}. "
                    f"Please ensure SimpleTuner is properly installed at {self.simpletuner_path}"
                )

        cmd = [
            'python', str(train_script),
            '--config', config_path
        ]

        logger.info(f"Starting training with command: {' '.join(cmd)}")
        logger.info(f"Config path: {config_path}")
        logger.info(f"Dataset path: {self.dataset_path}")
        logger.info(f"Output path: {self.output_path}")

        # Run training
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            cwd=str(self.simpletuner_path)
        )

        # Parse output
        current_step = 0
        current_loss = None

        for line in process.stdout:
            logger.info(line.strip())

            # Parse step information
            # Example: "Step 100/2000: loss=0.1234"
            step_match = re.search(r'[Ss]tep\s*(\d+)[/\s]+(\d+)', line)
            if step_match:
                current_step = int(step_match.group(1))
                total_steps = int(step_match.group(2))

                # Parse loss
                loss_match = re.search(r'loss[:\s=]+([0-9.]+)', line, re.IGNORECASE)
                if loss_match:
                    current_loss = float(loss_match.group(1))

                # Call progress callback
                if progress_callback:
                    progress_callback(current_step, total_steps, current_loss)

        # Wait for completion
        return_code = process.wait()

        if return_code != 0:
            error_msg = f"Training failed with return code {return_code}. Check logs at {self.output_path}/logs for details."
            logger.error(error_msg)
            logger.error(f"Command was: {' '.join(cmd)}")
            logger.error(f"Working directory: {self.simpletuner_path}")
            raise Exception(error_msg)

        # Get checkpoint paths
        checkpoints = self._get_checkpoints()

        logger.info(f"Training completed. Found {len(checkpoints)} checkpoints")

        return {
            'model_path': str(self.output_path),
            'checkpoints': checkpoints,
            'final_step': current_step,
            'final_loss': current_loss
        }

    def _get_checkpoints(self) -> list:
        """List all checkpoint files."""
        output_path = Path(self.output_path)
        checkpoints = list(output_path.glob('*.safetensors'))
        return [str(ckpt) for ckpt in sorted(checkpoints)]
