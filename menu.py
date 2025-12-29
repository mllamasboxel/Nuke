import nuke
import play_readnode_external

menu = nuke.menu("Nuke")
menu.addCommand(
    "Edit/Node/Play Read with External Player",
    "play_readnode_external.play_readnode_in_rv()",
    "Alt+Q"
)

import GrayAutoBackdrop
nuke.menu('Nuke').addCommand('Extra/Gray Auto Backdrop', lambda: GrayAutoBackdrop.GrayAutoBackdrop(), "alt+b", shortcutContext=2)
