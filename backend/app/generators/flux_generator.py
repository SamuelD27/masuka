import torch
from diffusers import FluxPipeline
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from PIL import Image
from app.generators.base_generator import BaseGenerator

logger = logging.getLogger(__name__)

class FluxGenerator(BaseGenerator):
    """Flux image generator with LoRA support."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.pipeline = None
        self.lora_loaded = False

        # Generation defaults
        self.default_steps = config.get('num_inference_steps', 30)
        self.default_guidance = config.get('guidance_scale', 3.5)
        self.default_width = config.get('width', 1024)
        self.default_height = config.get('height', 1024)

    def load_model(self):
        """Load Flux.1 Dev model."""
        if self.pipeline is not None:
            logger.info("Model already loaded")
            return

        logger.info("Loading Flux.1 Dev model...")

        try:
            self.pipeline = FluxPipeline.from_pretrained(
                "black-forest-labs/FLUX.1-dev",
                torch_dtype=torch.bfloat16
            )

            # Move to device
            self.pipeline = self.pipeline.to(self.device)

            # Enable memory optimizations
            if self.device == 'cuda':
                self.pipeline.enable_model_cpu_offload()
                self.pipeline.enable_vae_slicing()

            logger.info(f"Flux model loaded on {self.device}")

        except Exception as e:
            logger.error(f"Failed to load Flux model: {e}")
            raise

    def load_lora(self, lora_path: str, weight: float = 0.8):
        """
        Load a LoRA adapter.

        Args:
            lora_path: Path to LoRA safetensors file
            weight: LoRA weight (0.0 to 1.0)
        """
        if self.pipeline is None:
            raise ValueError("Base model not loaded. Call load_model() first.")

        logger.info(f"Loading LoRA from {lora_path} with weight {weight}")

        try:
            # Load LoRA weights
            self.pipeline.load_lora_weights(lora_path)

            # Set LoRA scale
            self.pipeline.fuse_lora(lora_scale=weight)

            self.lora_loaded = True
            logger.info("LoRA loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load LoRA: {e}")
            raise

    def unload_lora(self):
        """Unload current LoRA and clear CUDA cache."""
        if self.lora_loaded and self.pipeline is not None:
            logger.info("Unloading LoRA")
            self.pipeline.unfuse_lora()
            self.lora_loaded = False

            # Clear CUDA cache to prevent memory leaks
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                logger.info("CUDA cache cleared after LoRA unload")

    def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_images: int = 1,
        num_inference_steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        seed: Optional[int] = None,
        output_dir: Optional[str] = None,
        **kwargs
    ) -> List[str]:
        """
        Generate images with Flux.

        Args:
            prompt: Text prompt
            negative_prompt: Negative prompt (not used by Flux but kept for API compatibility)
            num_images: Number of images to generate
            num_inference_steps: Number of denoising steps (default: 30)
            guidance_scale: Guidance scale (default: 3.5)
            width: Image width (default: 1024)
            height: Image height (default: 1024)
            seed: Random seed for reproducibility
            output_dir: Directory to save images
            **kwargs: Additional parameters

        Returns:
            List of paths to generated images
        """
        if self.pipeline is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        # Use defaults if not specified
        steps = num_inference_steps or self.default_steps
        guidance = guidance_scale or self.default_guidance
        w = width or self.default_width
        h = height or self.default_height

        logger.info(f"Generating {num_images} images: {prompt[:50]}...")
        logger.info(f"Parameters: steps={steps}, guidance={guidance}, size={w}x{h}")

        # Set seed if provided
        generator = None
        if seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(seed)

        try:
            # Generate images
            with torch.inference_mode():
                images = self.pipeline(
                    prompt=prompt,
                    num_inference_steps=steps,
                    guidance_scale=guidance,
                    width=w,
                    height=h,
                    num_images_per_prompt=num_images,
                    generator=generator
                ).images

            # Save images
            output_paths = []
            output_directory = Path(output_dir) if output_dir else Path("/tmp/masuka/generated")
            output_directory.mkdir(parents=True, exist_ok=True)

            for i, image in enumerate(images):
                filename = f"image_{i+1}.png"
                filepath = output_directory / filename
                image.save(filepath)
                output_paths.append(str(filepath))
                logger.info(f"Saved image to {filepath}")

            # Clear CUDA cache after generation to prevent memory leaks
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                logger.info("CUDA cache cleared after generation")

            return output_paths

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            # Clear CUDA cache even on error
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            raise

    def unload_model(self):
        """Unload model to free memory."""
        if self.pipeline is not None:
            logger.info("Unloading Flux model")
            del self.pipeline
            self.pipeline = None
            self.lora_loaded = False

            # Clear CUDA cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            logger.info("Model unloaded")
