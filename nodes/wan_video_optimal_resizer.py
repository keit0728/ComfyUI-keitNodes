from typing import Tuple
from comfy.utils import common_upscale

# WanVideo向けの解像度プリセット定義
RESOLUTION_PRESETS = {
    "480p": [
        (480, 832),  # 16:9 vertical
        (832, 480),  # 16:9 horizontal
        (624, 624),  # 1:1 square
        (704, 544),  # 1.29:1 landscape
        (544, 704),  # 1:1.29 portrait
    ],
    "720p": [
        (720, 1280),  # 16:9 vertical
        (1280, 720),  # 16:9 horizontal
        (960, 960),  # 1:1 square
        (1088, 832),  # 1.31:1 landscape
        (832, 1088),  # 1:1.31 portrait
    ],
}


class WanVideoOptimalResizer:
    """
    WanVideoに最適化されたプリセット解像度変換ノード
    指定されたプリセット解像度の中から入力画像に最も適したものを選択して変換
    """

    upscale_methods = ["nearest-exact", "bilinear", "area", "bicubic", "lanczos"]

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "resolution_preset": (
                    ["480p", "720p"],
                    {"default": "480p"},
                ),
                "upscale_method": (
                    cls.upscale_methods,
                    {"default": "lanczos"},
                ),
            },
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("image", "width", "height")

    FUNCTION = "resize_to_optimal"
    CATEGORY = "keitNodes"

    def calculate_aspect_ratio(self, width: int, height: int) -> float:
        """アスペクト比を計算"""
        return width / height

    def find_best_resolution(
        self, original_width: int, original_height: int, preset: str
    ) -> Tuple[int, int]:
        """
        最も近いアスペクト比の最も近い解像度を選択
        1. 最もアスペクト比が近い候補を特定
        2. その中で最も解像度（ピクセル数）が近いものを選択
        """
        original_aspect = self.calculate_aspect_ratio(original_width, original_height)
        original_pixels = original_width * original_height
        candidates = RESOLUTION_PRESETS[preset]

        # 1. 最もアスペクト比が近い候補を見つける
        min_aspect_diff = float("inf")
        closest_aspect_candidates = []

        for width, height in candidates:
            candidate_aspect = self.calculate_aspect_ratio(width, height)
            aspect_diff = abs(original_aspect - candidate_aspect)

            if aspect_diff < min_aspect_diff:
                min_aspect_diff = aspect_diff
                closest_aspect_candidates = [(width, height)]
            elif aspect_diff == min_aspect_diff:
                closest_aspect_candidates.append((width, height))

        # 2. アスペクト比が最も近い候補の中で、最も解像度が近いものを選択
        best_resolution = None
        min_pixel_diff = float("inf")

        for width, height in closest_aspect_candidates:
            candidate_pixels = width * height
            pixel_diff = abs(original_pixels - candidate_pixels)

            if pixel_diff < min_pixel_diff:
                min_pixel_diff = pixel_diff
                best_resolution = (width, height)

        return best_resolution

    def resize_to_optimal(
        self, image, resolution_preset="480p", upscale_method="lanczos"
    ):
        """
        WanVideo用の最適な解像度にリサイズ
        """
        # 入力画像の形状を取得 [batch, height, width, channels]
        B, H, W, C = image.shape

        original_width = W
        original_height = H
        original_pixels = original_width * original_height

        # 最適な解像度を見つける
        target_width, target_height = self.find_best_resolution(
            original_width, original_height, resolution_preset
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

        # アスペクト比の計算
        original_aspect = self.calculate_aspect_ratio(original_width, original_height)
        target_aspect = self.calculate_aspect_ratio(target_width, target_height)
        target_pixels = target_width * target_height

        # 詳細情報の出力
        print(f"WanVideo Optimal Resize:")
        print(
            f"  Original: {original_width}x{original_height} ({original_pixels:,} pixels, aspect: {original_aspect:.4f})"
        )
        print(
            f"  Target: {target_width}x{target_height} ({target_pixels:,} pixels, aspect: {target_aspect:.4f})"
        )
        print(f"  Preset: {resolution_preset}")
        print(f"  Aspect ratio change: {abs(original_aspect - target_aspect):.6f}")
        print(f"  Upscale method: {upscale_method}")

        return (out_image, target_width, target_height)
