import os
volume_name= 'Type.World App'
format = 'UDBZ'
files = [os.path.join(os.eviron['PWD'], 'dist/Type.World.app')]
symlinks = { 'Applications': '/Applications'}
default_view = 'icon-view'
window_rect = ((500, 500), (443, 434))
background = 'wxPython/build/Mac/dmgbackground_final.tiff'

# Icon view
arrange_by = 'name'
icon_size = 128