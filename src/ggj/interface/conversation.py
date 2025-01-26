import curses
import logging

from ggj.input import KeyboardListener
from ggj.interface.windows import DialogueBox, RightOptionsMenu, LeftOptionsMenu
from ggj.world.item import Item
from ggj.world.npc import NPC
from ggj.world.player import Player

logger = logging.getLogger(__name__)


class Conversations:

    def __init__(
        self,
        p: Player,
        inv_box: LeftOptionsMenu,
        diag_box: DialogueBox,
        right_box: RightOptionsMenu,
        il: KeyboardListener,
    ):
        self.p = p
        self.inv_box = inv_box
        self.diag_box = diag_box
        self.right_box = right_box
        self.il = il

    def get_valid_choice(self, options: list[str]) -> int:

        choice = self.il.get_choice()
        while choice == 0 or choice > len(options):
            curses.beep()
            choice = self.il.get_choice()
        choice -= 1
        logger.info(f"dialogue option {choice}, {options[choice]} selected")
        return choice

    def attempt_trade(
        self,
        seller: dict[Item, int],
        buyer: dict[Item, int],
        trade: tuple[Item, Item],
    ) -> bool:

        sellers_item, buyers_item = trade

        # check trade

        if sellers_item not in seller or buyers_item not in buyer:
            curses.beep()
            return False

        assert seller[sellers_item] >= 1
        assert buyer[buyers_item] >= 1

        # remove items

        seller[sellers_item] -= 1
        buyer[buyers_item] -= 1

        if seller[sellers_item] == 0:
            del seller[sellers_item]

        if buyer[buyers_item] == 0:
            del buyer[buyers_item]

        # add items

        if sellers_item in buyer:
            buyer[sellers_item] += 1
        else:
            buyer[sellers_item] = 1

        if buyers_item in seller:
            seller[buyers_item] += 1
        else:
            seller[buyers_item] = 1

        self.inv_box.draw()
        logger.info(f"player sold {sellers_item} for {buyers_item}")

        return True

    def sell_to(self, npc: NPC):
        self.diag_box.write(npc.name + ": " + npc.trade_as_buyer)
        options = ["No trade"] + [
            f"1 x {a.name} for 1 x {b.name}" for (a, b) in npc.trades
        ]
        self.right_box.set_option_choices(
            options, option_label=f"{npc.name}'s Offers"
        )

        while True:
            choice = self.get_valid_choice(options)

            if choice == 0:  # no trade
                break
            elif choice == 1:  # sell wheat
                if self.attempt_trade(
                    self.p.inventory.inventory,
                    npc.inventory,
                    npc.trades[choice - 1],
                ):
                    self.diag_box.write(npc.name + ": " + npc.trade_success)
                else:
                    self.diag_box.write(npc.name + ": " + npc.trade_fail)

    def converse(
        self,
        npc: NPC,
    ):
        logger.info(f"dialogue initiated with {npc.name}")
        options = [
            "Farewell",
            f"Sell to {npc.name}",
        ]  # , f"Buy from {npc.name}"]
        self.right_box.set_option_choices(options)
        self.diag_box.write(npc.name + ": " + npc.states[npc.current_state])

        choice = self.get_valid_choice(options)

        if choice == 0:  # goodbye
            pass
        elif choice == 1:  # sell to
            self.sell_to(npc)

        self.right_box.set_option_choices([])
        self.diag_box.write("")
