from enum import Enum

from worlds.generic.Rules import add_rule, forbid_item
from rule_builder.rules import (Has, HasAny, HasAll, True_)
from .Locations import (SPHERE, BUILDING, locations)


class BUILDING_NAME(Enum):
    CURSOR = "Cursor"
    # GRANDMA = "Grandma"
    FARM = "Farm"
    MINE = "Mine"
    FACTORY = "Factory"
    BANK = "Bank"
    TEMPLE = "Temple"
    WIZARD_TOWER = "Wizard Tower"
    SHIPMENT = "Shipment"
    ALCHEMY_LAB = "Alchemy Lab"
    PORTAL = "Portal"
    TIME_MACHINE = "Time Machine"
    ANTIMATTER_CONDENSER = "Antimatter Condenser"
    PRISM = "Prism"
    CHANCEMAKER = "Chancemaker"
    FRACTAL_ENGINE = "Fractal Engine"
    JAVASCRIPT_CONSOLE = "Javascript Console"
    IDLEVERSE = "Idleverse"
    CORTEX_BAKER = "Cortex Baker"
    YOU = "You"

    def to_building_id(self):
        return BUILDING[self.name].value

    def unlock_item(self):
        return "Unlock " + self.value

    def progressive_item(self):
        return "Progressive " + self.value


def set_rules(self: "CookieClicker"):
    world = self.multiworld
    player = self.player

    # 1) Prevent each “Unlock Building” item from ever appearing in any of that building’s own-achievement locations.
    for building in BUILDING_NAME:
        for location in locations['by_building'][BUILDING[building.name]]:
            cclocation = world.get_location(location.name, player)
            forbid_item(cclocation, building.unlock_item(), player)
            forbid_item(cclocation, building.progressive_item(), player)

    # 2) Make the “sphere 0” achievements always available
    for location in locations['by_sphere'][SPHERE.ZERO]:
        cclocation = world.get_location(location.name, player)
        self.set_rule(cclocation, True_())

    # 3) Rough sphere implementation. Don't ask how it's balanced
    for location in locations["valid"]:
        cclocation = world.get_location(location.name, player)

        # Grandmapocalypse related
        if location.sphere == SPHERE.GRANDMA.value:
            self.set_rule(cclocation, HasAny("One Mind", "Communal brainsweep", "Elder Pact"))
            break

        # Achievements that require ALL buildings, or a lot of specific items (hence very very late game)
        if location.sphere == SPHERE.ENDGAME.value:
            self.set_rule(cclocation, Has("A crumbly egg") &
                     (HasAll(*[b.unlock_item() for b in BUILDING_NAME]) | HasAll(
                         *[b.progressive_item() for b in BUILDING_NAME])))
            break

        # Game progression spere rules are ADDITIVE : a location in sphere 4 must also fulfill rules from sphere 2
        if location.sphere >= SPHERE.ONE.value:
            rule = HasAny(BUILDING_NAME.TEMPLE.unlock_item(), BUILDING_NAME.TEMPLE.progressive_item(),
                          BUILDING_NAME.WIZARD_TOWER.unlock_item(), BUILDING_NAME.WIZARD_TOWER.progressive_item())

            if location.sphere >= SPHERE.TWO.value:
                rule &= HasAny(BUILDING_NAME.ALCHEMY_LAB.unlock_item(), BUILDING_NAME.ALCHEMY_LAB.progressive_item(),
                               BUILDING_NAME.PORTAL.unlock_item(), BUILDING_NAME.PORTAL.progressive_item())

            if location.sphere >= SPHERE.THREE.value:
                rule &= HasAny(BUILDING_NAME.FRACTAL_ENGINE.unlock_item(),
                               BUILDING_NAME.FRACTAL_ENGINE.progressive_item())

            if location.sphere >= SPHERE.FOUR.value:
                rule &= HasAny(BUILDING_NAME.IDLEVERSE.unlock_item(), BUILDING_NAME.IDLEVERSE.progressive_item())

            if location.sphere >= SPHERE.FIVE.value:
                rule &= HasAny(BUILDING_NAME.CORTEX_BAKER.unlock_item(), BUILDING_NAME.CORTEX_BAKER.progressive_item())

            if location.sphere >= SPHERE.LATEGAME.value:
                rule &= HasAny(BUILDING_NAME.YOU.unlock_item(), BUILDING_NAME.YOU.progressive_item())

            self.set_rule(cclocation, rule)

    # 3) Standard completion check. Due to AP limitations, the achievement count check is done client-side
    #    and a special Victory item is unlocked if conditions are met
    self.multiworld.completion_condition[player] = lambda state: state.has("Victory", self.player)
