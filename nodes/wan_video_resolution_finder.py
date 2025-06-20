from typing import Tuple
from .wan_video_optimal_resizer import WanVideoOptimalResizer


class WanVideoResolutionFinder(WanVideoOptimalResizer):
    """
    WanVideoに最適な解像度を計算するノード
    リサイズは行わず、最適な解像度の値のみを返す
    """

    def __init__(self):
        super().__init__()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "resolution_preset": (
                    ["480p", "720p"],
                    {"default": "480p"},
                ),
            },
        }

    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")

    FUNCTION = "find_optimal_resolution"
    CATEGORY = "keitNodes"

    def find_optimal_resolution(self, image, resolution_preset="480p"):
        """
        入力画像に対して最適な解像度を計算して返す
        """
        # 入力画像の形状を取得 [batch, height, width, channels]
        B, H, W, C = image.shape

        original_width = W
        original_height = H

        # 最適な解像度を見つける
        target_width, target_height = self.find_best_resolution(
            original_width, original_height, resolution_preset
        )

        # デバッグ情報の出力
        print(f"WanVideo Resolution Finder:")
        print(f"  Original: {original_width}x{original_height}")
        print(f"  Optimal: {target_width}x{target_height}")
        print(f"  Preset: {resolution_preset}")

        return (target_width, target_height)
