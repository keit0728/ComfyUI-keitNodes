from .nodes.m2m_translator import M2MTranslator
from .nodes.pixel_limit_resizer import PixelLimitResizer
from .nodes.wan_video_optimal_resizer import WanVideoOptimalResizer
from .nodes.wan_video_resolution_finder import WanVideoResolutionFinder
from .nodes.aspect_ratio_resolution_finder import AspectRatioResolutionFinder

NODE_CLASS_MAPPINGS = {
    "M2MTranslator": M2MTranslator,
    "PixelLimitResizer": PixelLimitResizer,
    "WanVideoOptimalResizer": WanVideoOptimalResizer,
    "WanVideoResolutionFinder": WanVideoResolutionFinder,
    "AspectRatioResolutionFinder": AspectRatioResolutionFinder,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "M2MTranslator": "M2MTranslator",
    "PixelLimitResizer": "PixelLimitResizer",
    "WanVideoOptimalResizer": "WanVideoOptimalResizer",
    "WanVideoResolutionFinder": "WanVideoResolutionFinder",
    "AspectRatioResolutionFinder": "AspectRatioResolutionFinder",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
