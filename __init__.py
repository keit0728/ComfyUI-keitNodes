from .nodes.m2m_translator import M2MTranslator
from .nodes.wan_video_optimal_resizer import WanVideoOptimalResizer

NODE_CLASS_MAPPINGS = {
    "M2MTranslator": M2MTranslator,
    "WanVideoOptimalResizer": WanVideoOptimalResizer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "M2MTranslator": "🌍 M2M-100 Translator",
    "WanVideoOptimalResizer": "🎬 WanVideo Optimal Resizer",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
