import curses

from ggj.input import KeyboardListener
from ggj.interface.windows import DialogueBox, RightOptionsMenu
from ggj.world.npc import NPC


def converse(
    npc: NPC,
    diag_box: DialogueBox,
    right_box: RightOptionsMenu,
    il: KeyboardListener,
):
    options = ["Farewell"]
    right_box.set_diag_option(options)
    diag_box.write(npc.states[npc.current_state])

    choice = il.get_choice() - 1
    while choice >= len(options):
        curses.beep()
        choice = il.get_choice()

    if options[choice].lower() == "farewell":
        pass

    right_box.set_diag_option([])
    diag_box.write("")
