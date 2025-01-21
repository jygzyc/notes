# -*- coding:utf-8 -*-

from datetime import datetime

def on_config(config, **kwargs):
    config.copyright = f"版权所有 © 2022-{datetime.now().year} Ecool的知识花园"