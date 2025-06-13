from typing import Tuple
import math
from comfy.utils import common_upscale

# Maximum pixel count limit
DEFAULT_MAX_PIXELS = 589824  # Approximately equivalent to 1024x576 pixels


class PixelLimitResizer:
    """
    Aspect ratio preserving pixel count limiter with 16-pixel multiple resolution resizer
    Resizes input images while maintaining aspect ratio, staying within max_pixels limit,
    and using resolutions that are multiples of 16 for maximum pixel count.
    Optimized for 3D VAE spatiotemporal compression.
    """

    upscale_methods = ["nearest-exact", "bilinear", "area", "bicubic", "lanczos"]

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "upscale_method": (
                    cls.upscale_methods,
                    {"default": "lanczos"},
                ),
                "max_pixels": (
                    "INT",
                    {
                        "default": DEFAULT_MAX_PIXELS,
                        "min": 16 * 16,
                        "max": 2048 * 2048,
                        "step": 1,
                        "tooltip": "Maximum pixel count limit (width × height). The image will be resized to stay within this limit while maintaining aspect ratio and 16-pixel alignment. Default: 589824 pixels (ex: 1024×576)",
                    },
                ),
            },
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT", "FLOAT", "STRING")
    RETURN_NAMES = ("image", "width", "height", "aspect_ratio", "resize_info")

    FUNCTION = "resize_with_pixel_limit"
    CATEGORY = "🖼️ Image/Resize"

    def calculate_aspect_ratio(self, width: int, height: int) -> float:
        """Calculate aspect ratio"""
        return width / height

    def find_optimal_resolution(
        self, original_width: int, original_height: int, max_pixels: int
    ) -> Tuple[int, int, int]:
        """
        Find optimal resolution maintaining aspect ratio within pixel limit with 16-pixel multiples
        Optimized for 3D VAE spatiotemporal compression (spatial 8×8×temporal 4× = 256× compression)

        Returns:
            tuple: (optimal_width, optimal_height, actual_pixels)
        """
        original_aspect = self.calculate_aspect_ratio(original_width, original_height)

        # Calculate theoretical maximum height
        # aspect_ratio * height * height <= max_pixels
        # height <= sqrt(max_pixels / aspect_ratio)
        max_height_theoretical = math.sqrt(max_pixels / original_aspect)

        # Find maximum height that is a multiple of 16
        max_height_16multiple = int(max_height_theoretical // 16) * 16

        best_width = 0
        best_height = 0
        best_pixels = 0

        # Search for optimal solution by decreasing height in multiples of 16
        for height in range(
            max_height_16multiple, 15, -16
        ):  # Start from 16 and decrease in multiples of 16
            # Calculate width from aspect ratio
            width_exact = original_aspect * height

            # Adjust to multiples of 16 (try both floor and ceil)
            width_down = int(width_exact // 16) * 16
            width_up = width_down + 16

            # Check pixel count for both cases
            for width in [width_down, width_up]:
                if width > 0 and (width * height) <= max_pixels:
                    pixels = width * height
                    if pixels > best_pixels:
                        best_pixels = pixels
                        best_width = width
                        best_height = height

        # Safety fallback if no optimal solution found
        if best_width == 0 or best_height == 0:
            # Fallback to minimum size (16x16)
            if original_aspect >= 1:  # Landscape or square
                best_width = 16
                best_height = 16
            else:  # Portrait
                best_width = 16
                best_height = 16
            best_pixels = best_width * best_height

        return best_width, best_height, best_pixels

    def resize_with_pixel_limit(
        self,
        image,
        upscale_method="lanczos",
        max_pixels=DEFAULT_MAX_PIXELS,
    ):
        """
        Resize within pixel limit while maintaining aspect ratio
        16-pixel multiple constraint ensures 3D VAE compatibility
        """
        # Get input image shape [batch, height, width, channels]
        B, H, W, C = image.shape

        original_width = W
        original_height = H
        original_pixels = original_width * original_height

        # Find optimal resolution
        target_width, target_height, target_pixels = self.find_optimal_resolution(
            original_width, original_height, max_pixels
        )

        # Check if resize is needed
        if original_width == target_width and original_height == target_height:
            out_image = image.clone()
        else:
            # Resize using common_upscale
            # Adjust tensor dimensions: [B, H, W, C] -> [B, C, H, W]
            out_image = image.clone()
            out_image = common_upscale(
                out_image.movedim(-1, 1),
                target_width,
                target_height,
                upscale_method,
                crop="disabled",
            ).movedim(1, -1)

        # Calculate aspect ratios
        original_aspect = self.calculate_aspect_ratio(original_width, original_height)
        target_aspect = self.calculate_aspect_ratio(target_width, target_height)

        # Detailed information
        resize_info = (
            f"Original: {original_width}x{original_height} "
            f"({original_pixels:,} pixels, aspect: {original_aspect:.4f}) → "
            f"Target: {target_width}x{target_height} "
            f"({target_pixels:,} pixels, aspect: {target_aspect:.4f}) [16×]"
        )

        print(f"Pixel limit resize (16×): {resize_info}")
        print(f"Aspect ratio change: {abs(original_aspect - target_aspect):.6f}")
        print(
            f"Pixel efficiency: {target_pixels/max_pixels*100:.1f}% of limit ({max_pixels:,})"
        )
        print(f"3D VAE compatibility: ✓ (256× compression ready)")

        return (out_image, target_width, target_height, target_aspect, resize_info)


# Node registration mapping
NODE_CLASS_MAPPINGS = {
    "PixelLimitResizer": PixelLimitResizer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PixelLimitResizer": "Pixel Limit Resizer (16× Multiple)",
}
