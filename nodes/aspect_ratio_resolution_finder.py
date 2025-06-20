from typing import Tuple

# 高さプリセットの定義
HEIGHT_PRESETS = {
    "144p": 144,
    "240p": 240,
    "360p": 360,
    "480p": 480,
    "540p": 540,
    "576p": 576,
    "720p": 720,
    "900p": 900,
    "1080p": 1080,
    "1200p": 1200,
    "1440p": 1440,
    "1600p": 1600,
    "2160p": 2160,
}


class AspectRatioResolutionFinder:
    """
    アスペクト比を維持しながら指定の高さに合わせた解像度を計算するノード
    リサイズは行わず、計算された幅と高さの値のみを返す
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        # プリセットのリストをソート（数値の小さい順）
        height_presets = list(HEIGHT_PRESETS.keys())

        return {
            "required": {
                "image": ("IMAGE",),
                "height_preset": (
                    height_presets,
                    {"default": "720p"},
                ),
            },
        }

    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")

    FUNCTION = "calculate_resolution"
    CATEGORY = "keitNodes"

    def calculate_aspect_ratio(self, width: int, height: int) -> float:
        """アスペクト比を計算"""
        return width / height

    def calculate_resolution_for_height(
        self, original_width: int, original_height: int, target_height: int
    ) -> Tuple[int, int]:
        """
        アスペクト比を維持しながら、指定された高さに対する幅を計算
        """
        aspect_ratio = self.calculate_aspect_ratio(original_width, original_height)
        target_width = int(round(target_height * aspect_ratio))
        return target_width, target_height

    def calculate_resolution(self, image, height_preset="720p"):
        """
        入力画像のアスペクト比を維持して、指定された高さでの解像度を計算して返す
        """
        # 入力画像の形状を取得 [batch, height, width, channels]
        B, H, W, C = image.shape

        original_width = W
        original_height = H
        original_aspect_ratio = self.calculate_aspect_ratio(
            original_width, original_height
        )

        # 指定された高さプリセットの値を取得
        target_height = HEIGHT_PRESETS[height_preset]

        # アスペクト比を維持した幅を計算
        target_width, target_height = self.calculate_resolution_for_height(
            original_width, original_height, target_height
        )

        # 計算後のアスペクト比
        target_aspect_ratio = self.calculate_aspect_ratio(target_width, target_height)

        # デバッグ情報の出力
        print(f"Aspect Ratio Resolution Finder:")
        print(
            f"  Original: {original_width}x{original_height} (aspect: {original_aspect_ratio:.4f})"
        )
        print(
            f"  Target: {target_width}x{target_height} (aspect: {target_aspect_ratio:.4f})"
        )
        print(f"  Height Preset: {height_preset}")
        print(
            f"  Aspect ratio difference: {abs(original_aspect_ratio - target_aspect_ratio):.6f}"
        )

        return (target_width, target_height)
