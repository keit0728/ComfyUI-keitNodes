from .nodes.m2m_translator import M2MTranslator
from .nodes.pixel_limit_resizer import PixelLimitResizer

NODE_CLASS_MAPPINGS = {
    "M2MTranslator": M2MTranslator,
    "PixelLimitResizer": PixelLimitResizer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "M2MTranslator": "M2MTranslator",
    "PixelLimitResizer": "PixelLimitResizer",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
