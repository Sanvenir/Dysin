# -*- coding:utf-8 -*-
"""YAML 配置文件加载器"""
import os
import random
import yaml
from pathlib import Path
TEXT_DIR = Path(__file__).parent.parent.parent / 'res' / 'text'

class YamlLoader:
    """统一加载所有 YAML 配置"""
    def __init__(self):
        self.config = {}
        self.define = {}
        self.function = {}
        self.dialogue = {}
        self._load_all()
    def _load_all(self):
        config_path = TEXT_DIR / 'config.yaml'
        define_path = TEXT_DIR / 'define.yaml'
        function_path = TEXT_DIR / 'function.yaml'
        dialogue_path = TEXT_DIR / 'dialogue.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        with open(define_path, 'r', encoding='utf-8') as f:
            self.define = yaml.safe_load(f)
        with open(function_path, 'r', encoding='utf-8') as f:
            self.function = yaml.safe_load(f)
        with open(dialogue_path, 'r', encoding='utf-8') as f:
            self.dialogue = yaml.safe_load(f)
    # ---- config 访问 ----
    @property
    def spirit_config(self):
        return self.config.get('spirit', {})
    @property
    def dialog_config(self):
        return self.config.get('dialog', {})
    @property
    def character(self):
        return self.define.get('character', {})
    @property
    def outer_define(self):
        """兼容旧 outerDefine 字典（大写 key）"""
        ch = self.define.get('character', {})
        return {
            'TRAY_NAME': ch.get('tray_name', ''),
            'TRAYNAME': ch.get('tray_name', ''),
            'NAME': ch.get('name', ''),
            'CALLING': ch.get('calling', ''),
            'SECONDCALLING': ch.get('second_calling', ''),
            'WELCOMING_TEXT': ch.get('welcome_text', ''),
            'CLICK_TEXT': ch.get('click_text', ''),
            'TRAY_TOOL_TIPS': ch.get('tray_tooltip', ''),
        }
    # ---- 状态随机选择 ----
    def get_dialogue(self, state_name, relation):
        """返回 (text, goto, icon_path, sound_path)"""
        state = self.dialogue.get('states', {}).get(state_name, {})
        # 关系 fallback
        rel_data = state.get(relation) or state.get('normal') or []
        # 应用条件过滤
        ready = self._filter(rel_data)
        if not ready:
            return '', '', '', ''
        chosen = random.choice(ready)
        text = chosen.get('text', '')
        goto = chosen.get('goto', '')
        icon_name = chosen.get('icon', '')
        sound_name = chosen.get('sound', '')
        icon_path = str(TEXT_DIR.parent / 'image' / f'{icon_name}.png') if icon_name else ''
        sound_path = str(TEXT_DIR.parent / 'sound' / f'{sound_name}.wav') if sound_name else ''
        return text, goto, icon_path, sound_path
    def _filter(self, items):
        """根据当前变量过滤条目"""
        from dysin.core import setting
        result = []
        for item in items:
            when = item.get('when')
            if when:
                match = True
                for var, val in when.items():
                    if setting.variable.get(var) != val:
                        match = False
                        break
                if match:
                    result.append(item)
            else:
                result.append(item)
        return result
    def get_weighted_dialogue(self, state_name, relation):
        """带权重的随机选择"""
        state = self.dialogue.get('states', {}).get(state_name, {})
        rel_data = state.get(relation) or state.get('normal') or []
        ready = self._filter(rel_data)
        if not ready:
            return '', '', '', ''
        # 权重选择
        total_weight = sum(item.get('weight', 1) for item in ready)
        r = random.uniform(0, total_weight)
        cum = 0
        for item in ready:
            cum += item.get('weight', 1)
            if r <= cum:
                chosen = item
                break
        else:
            chosen = ready[-1]
        text = chosen.get('text', '')
        goto = chosen.get('goto', '')
        icon_name = chosen.get('icon', '')
        sound_name = chosen.get('sound', '')
        icon_path = str(TEXT_DIR.parent / 'image' / f'{icon_name}.png') if icon_name else ''
        sound_path = str(TEXT_DIR.parent / 'sound' / f'{sound_name}.wav') if sound_name else ''
        return text, goto, icon_path, sound_path
    # ---- function 反应菜单 ----
    def get_reaction(self, state_name):
        """返回 {reaction: (label, next_state)}"""
        state = self.function.get('states', {}).get(state_name, {})
        result = {}
        for reaction, data in state.items():
            result[reaction] = (data.get('label', ''), data.get('next', ''))
        return result
# 全局单例
loader = None
def get_loader():
    global loader
    if loader is None:
        loader = YamlLoader()
    return loader
