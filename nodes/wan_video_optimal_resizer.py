from typing import Any, Tuple
import torch
import numpy as np
from comfy.utils import common_upscale

# サポートする解像度リスト
SUPPORTED_RESOLUTIONS = [
    (640, 640),  # 1:1 正方形
    (512, 768),  # 2:3 縦長
    (768, 512),  # 3:2 横長
    (854, 480),  # 16:9 横長 (480p)
    (270, 480),  # 9:16 縦長 (480p)
]


class WanVideoOptimalResizer:
    """
    WanVideoに最適な解像度への変換
    入力画像をWanVideo推奨解像度の中で最もアスペクト比が近いものにstretchします
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
            },
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT", "FLOAT", "STRING")
    RETURN_NAMES = ("image", "width", "height", "aspect_ratio", "resolution_info")

    FUNCTION = "resize_to_best_aspect"
    CATEGORY = "🖼️ Image/Resize"

    def calculate_aspect_ratio(self, width: int, height: int) -> float:
        """アスペクト比を計算"""
        return width / height

    def find_best_resolution(
        self, original_width: int, original_height: int
    ) -> Tuple[int, int, float]:
        """
        入力画像のアスペクト比に最も近い解像度を見つける

        Returns:
            tuple: (best_width, best_height, aspect_difference)
        """
        original_aspect = self.calculate_aspect_ratio(original_width, original_height)

        best_resolution = None
        min_difference = float("inf")

        for width, height in SUPPORTED_RESOLUTIONS:
            target_aspect = self.calculate_aspect_ratio(width, height)
            difference = abs(original_aspect - target_aspect)

            if difference < min_difference:
                min_difference = difference
                best_resolution = (width, height)

        return best_resolution[0], best_resolution[1], min_difference

    def resize_to_best_aspect(
        self,
        image,
        upscale_method="lanczos",
    ):
        """
        画像を最適なアスペクト比の解像度にリサイズ
        """
        # 入力画像の形状を取得 [batch, height, width, channels]
        B, H, W, C = image.shape

        original_width = W
        original_height = H

        # 最適な解像度を見つける
        best_width, best_height, aspect_difference = self.find_best_resolution(
            original_width, original_height
        )

        # common_upscaleを使用してリサイズ（stretch）
        # テンソルの次元を調整: [B, H, W, C] -> [B, C, H, W]
        out_image = image.clone()
        out_image = common_upscale(
            out_image.movedim(-1, 1),
            best_width,
            best_height,
            upscale_method,
            crop="disabled",
        ).movedim(1, -1)

        # アスペクト比計算
        original_aspect = self.calculate_aspect_ratio(original_width, original_height)
        new_aspect = self.calculate_aspect_ratio(best_width, best_height)

        # 解像度情報
        resolution_info = f"Original: {original_width}x{original_height} (aspect: {original_aspect:.3f}) → Target: {best_width}x{best_height} (aspect: {new_aspect:.3f})"

        print(f"Image resized: {resolution_info}")
        print(f"Aspect ratio difference: {aspect_difference:.6f}")

        return (out_image, best_width, best_height, new_aspect, resolution_info)
