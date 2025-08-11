# -*- coding: utf-8 -*-
"""
DMG creation settings for dmgbuild
"""

import os.path

# Application name
application = defines.get('app', 'dist/Baal Pet Assistant.app')
appname = os.path.basename(application).replace('.app', '')

# Volume name
volume_name = appname

# Volume format (UDZO = compressed)
format = 'UDZO'

# Volume size (None = automatic)
size = None

# Files to include
files = [application]

# Symlinks to create
symlinks = {'Applications': '/Applications'}

# Volume icon (uses app icon if not specified)
icon = 'baal/resources/cat.icns'

# Background image for DMG window
background = 'installer/dmg_background.png'

# Icon size in DMG window
icon_size = 100

# Window position and size
window_rect = ((100, 100), (600, 400))

# Icon positions
icon_locations = {
    appname + '.app': (150, 190),
    'Applications': (450, 190)
}

# Text size
text_size = 12

# Default view (icon-view, list-view, column-view)
default_view = 'icon-view'

# Show status bar
show_status_bar = False

# Show tab view
show_tab_view = False

# Show toolbar
show_toolbar = False

# Show pathbar
show_pathbar = False

# Show sidebar
show_sidebar = False

# Sidebar width
sidebar_width = 180

# Grid settings for icon view
arrange_by = None
grid_offset = (0, 0)
grid_spacing = 100
scroll_position = (0, 0)
label_pos = 'bottom'

# License file (optional)
license = {
    'default-language': 'en_US',
    'licenses': {
        'en_US': 'LICENSE'
    }
} if os.path.exists('LICENSE') else None