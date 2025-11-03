"""
DDS Texture Loader for SpellForce terrain textures

Loads DDS (DirectDraw Surface) texture files and converts them to numpy arrays
for use in OpenGL rendering.

Supports:
- BC1 (DXT1) compression
- BC3 (DXT5) compression
- Multiple formats via Pillow
"""

import io
from pathlib import Path
from typing import Optional, Tuple, Union

import numpy as np
from loguru import logger

try:
    from PIL import Image

    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    logger.warning("Pillow not available - DDS loading will not work")


class DDSLoader:
    """
    Load DDS texture files

    Usage:
        loader = DDSLoader()
        texture = loader.load("path/to/texture.dds")
        # texture is numpy array (height, width, 4) uint8 RGBA
    """

    def __init__(self):
        if not PILLOW_AVAILABLE:
            raise ImportError(
                "Pillow is required for DDS loading. Install with: pip install Pillow"
            )

    def load(
        self,
        source: Union[str, Path, bytes],
        target_size: Optional[Tuple[int, int]] = None,
    ) -> Optional[np.ndarray]:
        """
        Load a DDS texture from file path or bytes

        Args:
            source: File path (str/Path) or raw bytes
            target_size: Optional (width, height) to resize to. Default: keep original

        Returns:
            numpy array (height, width, 4) uint8 RGBA, or None on failure
        """
        try:
            # Load image
            if isinstance(source, bytes):
                image = Image.open(io.BytesIO(source))
            else:
                image = Image.open(source)

            # Log original info
            logger.debug(
                f"Loaded DDS: size={image.size}, mode={image.mode}, format={image.format}"
            )

            # Convert to RGBA if needed
            if image.mode != "RGBA":
                logger.debug(f"Converting from {image.mode} to RGBA")
                image = image.convert("RGBA")

            # Resize if requested
            if target_size and image.size != target_size:
                logger.debug(f"Resizing from {image.size} to {target_size}")
                image = image.resize(target_size, Image.Resampling.LANCZOS)

            # Convert to numpy array
            texture_array = np.array(image, dtype=np.uint8)

            logger.debug(f"Texture array shape: {texture_array.shape}")

            return texture_array

        except Exception as e:
            logger.error(f"Failed to load DDS texture: {e}")
            return None

    def load_from_file(self, filepath: Union[str, Path]) -> Optional[np.ndarray]:
        """Load DDS from file path"""
        return self.load(filepath)

    def load_from_bytes(self, data: bytes) -> Optional[np.ndarray]:
        """Load DDS from raw bytes"""
        return self.load(data)

    def create_test_texture(
        self,
        size: Tuple[int, int] = (256, 256),
        color: Tuple[int, int, int, int] = (128, 128, 128, 255),
    ) -> np.ndarray:
        """
        Create a test texture with solid color

        Args:
            size: (width, height)
            color: (R, G, B, A) values 0-255

        Returns:
            numpy array (height, width, 4) uint8
        """
        width, height = size
        texture = np.full((height, width, 4), color, dtype=np.uint8)

        # Add a border for debugging
        border_color = (255, 255, 255, 255)
        texture[0, :] = border_color  # Top
        texture[-1, :] = border_color  # Bottom
        texture[:, 0] = border_color  # Left
        texture[:, -1] = border_color  # Right

        # Add diagonal lines for orientation
        for i in range(min(width, height)):
            texture[i, i] = (255, 0, 0, 255)  # Red diagonal
            texture[i, width - 1 - i] = (0, 0, 255, 255)  # Blue diagonal

        return texture

    def create_checkerboard(
        self,
        size: Tuple[int, int] = (256, 256),
        squares: int = 8,
        color1: Tuple[int, int, int, int] = (255, 255, 255, 255),
        color2: Tuple[int, int, int, int] = (128, 128, 128, 255),
    ) -> np.ndarray:
        """
        Create a checkerboard test texture

        Args:
            size: (width, height)
            squares: Number of squares per side
            color1: First color (R, G, B, A)
            color2: Second color (R, G, B, A)

        Returns:
            numpy array (height, width, 4) uint8
        """
        width, height = size
        texture = np.zeros((height, width, 4), dtype=np.uint8)

        square_width = width // squares
        square_height = height // squares

        for y in range(squares):
            for x in range(squares):
                # Checkerboard pattern
                color = color1 if (x + y) % 2 == 0 else color2

                y_start = y * square_height
                y_end = (y + 1) * square_height
                x_start = x * square_width
                x_end = (x + 1) * square_width

                texture[y_start:y_end, x_start:x_end] = color

        return texture


# Convenience functions
def load_dds(filepath: Union[str, Path]) -> Optional[np.ndarray]:
    """
    Convenience function to load a DDS texture

    Args:
        filepath: Path to DDS file

    Returns:
        numpy array (height, width, 4) uint8 RGBA, or None on failure
    """
    loader = DDSLoader()
    return loader.load(filepath)


def create_test_texture(size: Tuple[int, int] = (256, 256)) -> np.ndarray:
    """
    Create a test texture for debugging

    Args:
        size: (width, height)

    Returns:
        numpy array (height, width, 4) uint8
    """
    loader = DDSLoader()
    return loader.create_test_texture(size)


def create_test_textures(count: int = 32, size: Tuple[int, int] = (256, 256)) -> list:
    """
    Create multiple test textures with different colors

    Args:
        count: Number of textures to create
        size: (width, height) for each texture

    Returns:
        List of numpy arrays
    """
    loader = DDSLoader()
    textures = []

    # Generate colors
    for i in range(count):
        # Create distinct colors using HSV color space
        hue = (i * 360 / count) % 360

        # Convert HSV to RGB (simple approximation)
        h = hue / 60.0
        c = 255
        x = int(c * (1 - abs(h % 2 - 1)))

        if 0 <= h < 1:
            r, g, b = c, x, 0
        elif 1 <= h < 2:
            r, g, b = x, c, 0
        elif 2 <= h < 3:
            r, g, b = 0, c, x
        elif 3 <= h < 4:
            r, g, b = 0, x, c
        elif 4 <= h < 5:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        texture = loader.create_test_texture(size, (r, g, b, 255))
        textures.append(texture)

    return textures
