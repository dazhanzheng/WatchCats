# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import plistlib

# 应用程序路径
application = defines.get('app', 'dist/Watch Cats.app')

# DMG 设置
appname = 'Watch Cats'
filename = 'Watch Cats.dmg'

# 卷标
volume_name = 'Watch Cats'

# 卷图标
volume_icon = 'baal/resources/watch_cats.icns'

# DMG 格式
format = 'UDZO'

# DMG 大小
size = None

# 文件和文件夹
files = [application]
symlinks = {'Applications': '/Applications'}

# 图标位置
icon_locations = {
    'Watch Cats.app': (140, 120),
    'Applications': (500, 120)
}

# 背景设置
background = 'builtin-arrow'

# 窗口设置
show_status_bar = False
show_tab_view = False
show_toolbar = False
show_pathbar = False
show_sidebar = False
window_rect = ((100, 100), (640, 280))
sidebar_width = 180

# 图标设置
default_view = 'icon-view'
icon_size = 160
text_size = 16

# 排列设置
arrange_by = None
grid_offset = (0, 0)
grid_spacing = 100
scroll_position = (0, 0)
label_pos = 'bottom'

# 选择设置
show_icon_preview = False
show_item_info = False

# 列表视图设置
list_icon_size = 16
list_text_size = 12
list_scroll_position = (0, 0)
list_sort_by = 'name'
list_use_relative_dates = True
list_calculate_all_sizes = False
list_columns = ('name', 'date-modified', 'size', 'kind', 'date-added')
list_column_widths = {
    'name': 300,
    'date-modified': 181,
    'date-created': 181,
    'date-added': 181,
    'date-last-opened': 181,
    'size': 97,
    'kind': 115,
    'label': 100,
    'version': 75,
    'comments': 300,
}
list_column_sort_directions = {
    'name': 'ascending',
    'date-modified': 'descending',
    'date-created': 'descending',
    'date-added': 'descending',
    'date-last-opened': 'descending',
    'size': 'descending',
    'kind': 'ascending',
    'label': 'ascending',
    'version': 'ascending',
    'comments': 'ascending',
}