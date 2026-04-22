import random
from dataclasses import asdict
from BaseClasses import Tutorial, Region, MultiWorld, Item, CollectionState, ItemClassification
from Utils import visualize_regions
from worlds.AutoWorld import World
from worlds.generic.Rules import add_rule
from Options import PerGameCommonOptions
from .Items import CCItem, traps, item_table, upgrades, structures, can_become_progressive, cookie_multiplier, \
    cookie_multiplier_weights, progressive_structures
from .Locations import CCLocation, locations, SPHERE
from .Options import CCOptions
from .Rules import set_rules

class CookieClicker(World):
    game = "Cookie Clicker"
    worldversion = "0.8.0a3"
    location_name_to_id = locations["name_to_id"]
    options_dataclass = CCOptions
    options: CCOptions
    item_name_to_id = { name: data.code for name, data in item_table.items() }
    cookie_names = [ item.item_name for item in cookie_multiplier ]
    cookie_weights = [ cookie_multiplier_weights.get(item.item_name, 1) for item in cookie_multiplier ]
    start_inventory = {}
    trashitems = 0

    def create_regions(self):
        region = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(region)

        achievement_region = Region("Achievements Region", self.player, self.multiworld)
        self.multiworld.regions.append(achievement_region)
        for location in locations["valid"]:
            achievement_region.add_locations({ f"{location.name}":location.id}, CCLocation)
        # Just one region for now, but we should add more later for sanity checks
        region.connect(achievement_region, "Achievements")

        # Special virtual item (event) to check victory. Think of it as a flag item
        event_location = CCLocation(self.player, "Victory location", 42000000, achievement_region)
        event_location.place_locked_item(CCItem("Victory", ItemClassification.progression, 42000000, self.player))
        achievement_region.locations.append(event_location)
        self.location_name_to_id["Victory location"] = 42000000
        self.item_name_to_id["Victory"] = 42000000

    def create_item(self, name: str) -> CCItem:
        item_data = item_table.get(name)
        if item_data is None:
            raise Exception(f"Tried to create unknown item: {name}")
        return CCItem(name, item_data.classification, item_data.code, self.player)

    def create_items(self):
        for upgrade in upgrades:
            self.multiworld.itempool.append(self.create_item(upgrade.item_name))

        placed_structures = 0
        if self.options.enable_progressive_buildings.value:
            # We skipp all the others and use progressive structures instead
            for structure_unlock in progressive_structures:
                progressive_item = self.create_item(structure_unlock.item_name)

                # ugly 3x lines because only for synergy for now
                self.multiworld.itempool.append(progressive_item)
                self.multiworld.itempool.append(progressive_item)
                self.multiworld.itempool.append(progressive_item)
                placed_structures += 3

        else:
            for structure_unlock in structures:
                self.multiworld.itempool.append(self.create_item(structure_unlock.item_name))

            for item in can_become_progressive:
                self.multiworld.itempool.append(self.create_item(item.item_name))

            placed_structures = len(structures) + len(can_become_progressive)

        total_locations = len(self.multiworld.get_unfilled_locations(self.player))
        placed_items_count = len(upgrades) + placed_structures
        remaining_locations = total_locations - placed_items_count

        if remaining_locations < 0:
            raise Exception("More upgrades and structures than locations!")

        trap_percent = self.options.traps_percentage.value / 100.0
        trap_count = int(remaining_locations * trap_percent)
        filler_count = remaining_locations - trap_count

        trap_names = [item.item_name for item in traps]
        for _ in range(trap_count):
            trap_name = random.choice(trap_names)
            self.multiworld.itempool.append(self.create_item(trap_name))

        for _ in range(filler_count):
            name = random.choices(self.cookie_names, weights = self.cookie_weights, k = 1)[0]
            self.multiworld.itempool.append(self.create_item(name))

    # We got some games which leave some locations unfilled, so we need to fill them with some filler items
    def pre_fill(self):
        pass

    def create_filler(self) -> Item:
        name = random.choices(self.cookie_names, weights = self.cookie_weights, k = 1)[0]
        return self.create_item(name)

    def fill_slot_data(self) -> dict:
        return {
            "player_name": self.multiworld.get_player_name(self.player),
            "player_id": self.player,
            "race": self.multiworld.is_race
        } | {k: v.value for k, v in asdict(self.options).items()}

    set_rules = set_rules
