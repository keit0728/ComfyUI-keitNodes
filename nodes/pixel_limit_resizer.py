from typing import Tuple
import math
from comfy.utils import common_upscale

# 最大ピクセル数制限
DEFAULT_MAX_PIXELS = 728320  # 1138x640相当


class PixelLimitResizer:
    """
    アスペクト比維持・ピクセル数制限・16の倍数解像度リサイザー
    入力画像のアスペクト比を維持しつつ、ピクセル数がmax_pixels以下で
    16の倍数の解像度の中で最もピクセル数が多い解像度にリサイズします
    3D VAEの時空間圧縮に最適化されています
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
                        "tooltip": "Maximum pixel count limit (width × height). The image will be resized to stay within this limit while maintaining aspect ratio and 16-pixel alignment.",
                    },
                ),
            },
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT", "FLOAT", "STRING")
    RETURN_NAMES = ("image", "width", "height", "aspect_ratio", "resize_info")

    FUNCTION = "resize_with_pixel_limit"
    CATEGORY = "🖼️ Image/Resize"

    def calculate_aspect_ratio(self, width: int, height: int) -> float:
        """アスペクト比を計算"""
        return width / height

    def find_optimal_resolution(
        self, original_width: int, original_height: int, max_pixels: int
    ) -> Tuple[int, int, int]:
        """
        アスペクト比を維持しつつ、ピクセル数制限内で16の倍数の最適解像度を見つける
        3D VAEの時空間圧縮（空間8×8×時間4×=256×圧縮）に最適化

        Returns:
            tuple: (optimal_width, optimal_height, actual_pixels)
        """
        original_aspect = self.calculate_aspect_ratio(original_width, original_height)

        # 理論上の最大高さを計算
        # aspect_ratio * height * height <= max_pixels
        # height <= sqrt(max_pixels / aspect_ratio)
        max_height_theoretical = math.sqrt(max_pixels / original_aspect)

        # 16の倍数で最大の高さを見つける
        max_height_16multiple = int(max_height_theoretical // 16) * 16

        best_width = 0
        best_height = 0
        best_pixels = 0

        # 高さを16の倍数で減らしながら最適解を探す
        for height in range(
            max_height_16multiple, 15, -16
        ):  # 16から始まって16の倍数で減少
            # アスペクト比から幅を計算
            width_exact = original_aspect * height

            # 16の倍数に調整（切り捨てと切り上げの両方を試す）
            width_down = int(width_exact // 16) * 16
            width_up = width_down + 16

            # 両方のケースでピクセル数チェック
            for width in [width_down, width_up]:
                if width > 0 and (width * height) <= max_pixels:
                    pixels = width * height
                    if pixels > best_pixels:
                        best_pixels = pixels
                        best_width = width
                        best_height = height

        # 最適解が見つからない場合の安全策
        if best_width == 0 or best_height == 0:
            # 最小サイズ（16x16）にフォールバック
            if original_aspect >= 1:  # 横長または正方形
                best_width = 16
                best_height = 16
            else:  # 縦長
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
        ピクセル数制限内でアスペクト比を維持してリサイズ
        16の倍数制約で3D VAEとの互換性を確保
        """
        # 入力画像の形状を取得 [batch, height, width, channels]
        B, H, W, C = image.shape

        original_width = W
        original_height = H
        original_pixels = original_width * original_height

        # 最適な解像度を見つける
        target_width, target_height, target_pixels = self.find_optimal_resolution(
            original_width, original_height, max_pixels
        )

        # リサイズが必要かチェック
        if original_width == target_width and original_height == target_height:
            out_image = image.clone()
        else:
            # common_upscaleを使用してリサイズ
            # テンソルの次元を調整: [B, H, W, C] -> [B, C, H, W]
            out_image = image.clone()
            out_image = common_upscale(
                out_image.movedim(-1, 1),
                target_width,
                target_height,
                upscale_method,
                crop="disabled",
            ).movedim(1, -1)

        # アスペクト比計算
        original_aspect = self.calculate_aspect_ratio(original_width, original_height)
        target_aspect = self.calculate_aspect_ratio(target_width, target_height)

        # 詳細情報
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


# ノード登録用のマッピング
NODE_CLASS_MAPPINGS = {
    "PixelLimitResizer": PixelLimitResizer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PixelLimitResizer": "Pixel Limit Resizer (16× Multiple)",
}
