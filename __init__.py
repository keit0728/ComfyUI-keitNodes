from .nodes.m2m_translator import M2MTranslator

NODE_CLASS_MAPPINGS = {
    "M2MTranslator": M2MTranslator,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "M2MTranslator": "🌍 M2M-100 Translator",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
