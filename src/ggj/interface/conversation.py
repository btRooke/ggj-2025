import curses
import logging
import time

from ggj.input import KeyboardListener
from ggj.interface.windows import DialogueBox, RightOptionsMenu
from ggj.world.npc import NPC

logger = logging.getLogger(__name__)


def sell_to(
    npc: NPC,
    diag_box: DialogueBox,
    right_box: RightOptionsMenu,
    il: KeyboardListener,
):
    diag_box.write(npc.trade_as_buyer)
    options = ["No trade", "TODO sell wheat"]
    right_box.set_option_choices(options, option_label=f"{npc.name}'s Offers")
    choice = get_valid_choice(options, il)

    if choice == 0:  # no trade
        pass
    elif choice == 1:  # sell wheat
        pass


def get_valid_choice(options: list[str], il: KeyboardListener) -> int:

    choice = il.get_choice()
    while choice == 0 or choice > len(options):
        curses.beep()
        choice = il.get_choice()
    choice -= 1
    logger.info(f"dialogue option {choice}, {options[choice]} selected")
    return choice


def converse(
    npc: NPC,
    diag_box: DialogueBox,
    right_box: RightOptionsMenu,
    il: KeyboardListener,
):
    logger.info(f"dialogue initiated with {npc.name}")
    options = ["Farewell", f"Sell to {npc.name}"]  # , f"Buy from {npc.name}"]
    right_box.set_option_choices(options)
    diag_box.write(npc.states[npc.current_state])

    choice = get_valid_choice(options, il)

    if choice == 0:  # goodbye
        pass
    elif choice == 1:  # sell to
        sell_to(npc, diag_box, right_box, il)

    right_box.set_option_choices([])
    diag_box.write("")
