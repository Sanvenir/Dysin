# -*- coding:utf-8 -*-
"""
i18n - 国际化与本地化支持
Dysin 桌面精灵
"""
import json
import os
from pathlib import Path

# 语言文件目录
I18N_DIR = Path(__file__).parent / "res" / "text" / "i18n"

# 当前语言 (默认中文)
_current_lang = "zh_CN"

# 翻译缓存
_translations = {}

# 可用语言
AVAILABLE_LANGS = {
    "zh_CN": "简体中文",
    "en_US": "English (US)",
}


def _load_lang(lang_code):
    """加载语言文件到缓存"""
    lang_file = I18N_DIR / f"{lang_code}.json"
    if lang_file.exists():
        with open(lang_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def set_lang(lang_code):
    """设置当前语言"""
    global _current_lang
    global _translations
    if lang_code in AVAILABLE_LANGS:
        _current_lang = lang_code
        _translations = _load_lang(lang_code)
    else:
        print(f"[i18n] Unknown language: {lang_code}")


def get_lang():
    """获取当前语言代码"""
    return _current_lang


def tr(key, default=None, **kwargs):
    """
    翻译函数 - 根据 key 返回翻译后的字符串
    
    Args:
        key: 翻译键，如 "menu.open"
        default: 默认值（当 key 不存在时返回）
        **kwargs: 字符串格式化参数
    
    Returns:
        翻译后的字符串
    """
    global _translations
    if not _translations:
        _translations = _load_lang(_current_lang)
    
    # 支持点号分隔的嵌套 key
    keys = key.split(".")
    value = _translations
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            # Key 不存在，返回默认值或 key 本身
            return default if default is not None else key
    
    # 格式化
    if kwargs:
        try:
            value = value.format(**kwargs)
        except Exception:
            pass
    
    return value


def init():
    """初始化 i18n 模块（自动调用）"""
    set_lang(_current_lang)


# 自动初始化
init()