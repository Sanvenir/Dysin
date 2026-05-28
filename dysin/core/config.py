# -*- coding:utf-8 -*-
"""Shared path constants."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
RES_DIR = PROJECT_ROOT / 'res'
IMAGE_DIR = RES_DIR / 'image'
SOUND_DIR = RES_DIR / 'sound'
TEXT_DIR = RES_DIR / 'text'
SAV_DIR = PROJECT_ROOT / 'sav'
