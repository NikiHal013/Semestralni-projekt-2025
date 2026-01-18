import pygame, json

AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1), (1, 1)])): 0,
    tuple(sorted([(-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)])): 1,
    tuple(sorted([(-1, 0), (-1, 1), (0, 1)])): 2,
    tuple(sorted([(0, 1)])): 3,
    tuple(sorted([(0, 1), (1, 0)])): 4,
    tuple(sorted([(-1, 0), (1, 0), (-1, 1), (0, 1)])): 5,
    tuple(sorted([(-1, 0), (1, 0), (0, 1), (1, 1)])): 6,
    tuple(sorted([(-1, 0), (0, 1)])): 7,
    tuple(sorted([(-1, 0), (1, 0), (0, 1)])): 8,
    tuple(sorted([(-1, -1), (0, -1), (-1, 0), (1, 0), (0, 1), (1, 1)])): 9,
    tuple(sorted([(0, -1), (1, -1), (1, 0), (0, 1), (1, 1)])): 10,
    tuple(sorted([(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)])): 11,
    tuple(sorted([(-1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)])): 12,
    tuple(sorted([(0, -1), (0, 1)])): 13,
    tuple(sorted([(0, -1), (1, -1), (1, 0), (0, 1)])): 14,
    tuple(sorted([(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1)])): 15,
    tuple(sorted([(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (0, 1), (1, 1)])): 16,
    tuple(sorted([(-1, -1), (0, -1), (-1, 0), (0, 1)])): 17,
    tuple(sorted([(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (0, 1)])): 18,
    tuple(sorted([(0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1)])): 19,
    tuple(sorted([(0, -1), (1, -1), (1, 0)])): 20,
    tuple(sorted([(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0)])): 21,
    tuple(sorted([(-1, -1), (0, -1), (-1, 0)])): 22,
    tuple(sorted([(0, -1)])): 23,
    tuple(sorted([(0, -1), (1, 0), (0, 1), (1, 1)])): 24,
    tuple(sorted([(-1, -1), (0, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)])): 25,
    tuple(sorted([(0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)])): 26,
    tuple(sorted([(0, -1), (-1, 0), (-1, 1), (0, 1)])): 27,
    tuple(sorted([(0, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)])): 28,
    tuple(sorted([(0, -1), (-1, 0), (1, 0), (0, 1), (1, 1)])): 29,
    tuple(sorted([(0, -1), (-1, 0), (1, 0), (-1, 1), (0, 1)])): 30,
    tuple(sorted([(1, 0)])): 31,
    tuple(sorted([(-1, 0), (1, 0)])): 32,
    tuple(sorted([(-1, 0)])): 33,
    tuple(sorted([])): 34,
    tuple(sorted([(0, -1), (1, 0)])): 35,
    tuple(sorted([(-1, -1), (0, -1), (-1, 0), (1, 0)])): 36,
    tuple(sorted([(0, -1), (1, -1), (-1, 0), (1, 0)])): 37,
    tuple(sorted([(0, -1), (-1, 0)])): 38,
    tuple(sorted([(0, -1), (-1, 0), (1, 0)])): 39,
    tuple(sorted([(0, -1), (1, -1), (-1, 0), (1, 0), (0, 1)])): 40,
    tuple(sorted([(-1, -1), (0, -1), (-1, 0), (1, 0), (0, 1)])): 41,
    tuple(sorted([(0, -1), (1, 0), (0, 1)])): 42,
    tuple(sorted([(-1, -1), (0, -1), (-1, 0), (1, 0), (-1, 1), (0, 1)])): 43,
    tuple(sorted([(0, -1), (1, -1), (-1, 0), (1, 0), (0, 1), (1, 1)])): 44,
    tuple(sorted([(0, -1), (-1, 0), (0, 1)])): 45,
    tuple(sorted([(0, -1), (-1, 0), (1, 0), (0, 1)])): 46,
    # Additional neighbor patterns observed in maps that previously failed to auto-tile.
    tuple(sorted([(-1, 1), (0, 1), (1, 0), (1, 1)])): 0,
    tuple(sorted([(0, 1), (1, -1), (1, 0), (1, 1)])): 0,
    tuple(sorted([(-1, -1), (-1, 0), (-1, 1), (0, -1), (1, -1), (1, 0)])): 0,
    tuple(sorted([(-1, -1), (-1, 0), (0, -1), (1, -1)])): 0,
    tuple(sorted([(-1, -1), (-1, 0), (0, -1), (1, -1), (1, 0), (1, 1)])): 0,
    tuple(sorted([(-1, -1), (0, -1), (1, -1), (1, 0)])): 0,
    tuple(sorted([(-1, 0), (-1, 1)])): 33,
    tuple(sorted([(-1, 0), (-1, 1), (0, 1), (1, -1), (1, 0), (1, 1)])): 0,
    tuple(sorted([(-1, 1), (0, -1), (0, 1)])): 0,
    tuple(sorted([(1, 0), (1, 1)])): 0,
    tuple(sorted([(-1, -1), (-1, 0), (-1, 1)])): 33,
    tuple(sorted([(-1, -1), (-1, 0), (-1, 1), (0, -1)])): 22,
    tuple(sorted([(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1)])): 12,
    tuple(sorted([(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 1)])): 12,
    tuple(sorted([(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, 1)])): 12,
    tuple(sorted([(-1, -1), (-1, 0), (-1, 1), (0, -1), (1, -1)])): 22,
    tuple(sorted([(-1, -1), (-1, 0), (-1, 1), (0, -1), (1, -1), (1, 0)])): 21,
    tuple(sorted([(-1, -1), (-1, 0), (-1, 1), (0, -1), (1, -1), (1, 0), (1, 1)])): 21,
    tuple(sorted([(-1, -1), (-1, 0), (-1, 1), (0, 1)])): 2,
    tuple(sorted([(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 0), (1, 1)])): 1,
    tuple(sorted([(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1)])): 2,
    tuple(sorted([(-1, -1), (-1, 0), (0, -1), (0, 1), (1, -1)])): 17,
    tuple(sorted([(-1, -1), (-1, 0), (0, -1), (1, -1)])): 22,
    tuple(sorted([(-1, -1), (-1, 0), (0, -1), (1, -1), (1, 0), (1, 1)])): 21,
    tuple(sorted([(-1, -1), (-1, 0), (1, -1), (1, 0)])): 0,
    tuple(sorted([(-1, -1), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)])): 10,
    tuple(sorted([(-1, -1), (0, -1)])): 23,
    tuple(sorted([(-1, -1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)])): 10,
    tuple(sorted([(-1, -1), (0, -1), (1, -1), (1, 0)])): 20,
    tuple(sorted([(-1, 0), (-1, 1), (0, 1), (1, -1), (1, 0), (1, 1)])): 1,
    tuple(sorted([(-1, 0), (-1, 1), (0, 1), (1, 1)])): 2,
    tuple(sorted([(-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)])): 10,
    tuple(sorted([(-1, 1), (0, -1), (0, 1), (1, 0), (1, 1)])): 24,
    tuple(sorted([(-1, 1), (0, 1), (1, -1), (1, 0), (1, 1)])): 0,
    tuple(sorted([(-1, 1), (0, 1), (1, 0), (1, 1)])): 0,
    tuple(sorted([(0, -1), (1, -1)])): 23,
    tuple(sorted([(0, -1), (1, -1), (1, 0), (1, 1)])): 20,
    tuple(sorted([(0, 1), (1, -1), (1, 0), (1, 1)])): 0,
    tuple(sorted([(0, 1), (1, 1)])): 0,
    tuple(sorted([(1, -1), (1, 0), (1, 1)])): 31,
}

NEIGHBOR_OFFSETS = [(-1, -1), (0, -1), (1, -1),
                     (-1, 0), (0, 0), (1, 0),
                     (-1, 1),  (0, 1),  (1, 1)] #relative positions of neighboring tiles (including self)

PHYSICS_TILES = {"rocky_tiles", "grassy_tiles", "swing_tiles", "pole_tiles", "rocky_platform"}
AUTOTILE_TILES = {"rocky_tiles", "grassy_tiles", "water_tiles"}
AUTOTILE_GROUPS = {"rocky_tiles": {"rocky_tiles", "grassy_tiles"}, "grassy_tiles": {"rocky_tiles", "grassy_tiles"}}  # tiles that autotile together
RANDOMIZE_TILES = {"rocky_decor", "grassy_decor"}

class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []

    def extract(self, id_pairs, keep=False): #extract tiles matching given (type, variant) pairs
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile) #remove tile from offgrid list
    
        to_delete = []
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy()) 
                matches [-1]["pos"] = matches[-1]["pos"].copy() #store pixel position instead of tile coordinates #copy to avoid modifying original
                matches [-1]["pos"][0] *= self.tile_size
                matches [-1]["pos"][1] *= self.tile_size
                if not keep:
                    to_delete.append(loc)
        
        for loc in to_delete:
            del self.tilemap[loc] #remove tile from tilemap
        
        return matches
    
    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles
    
    def save(self, path):
        f = open(path, 'w')
        json.dump({"tilemap": self.tilemap, "tile_size": self.tile_size, "offgrid": self.offgrid_tiles}, f)
        f.close()

    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()

        self.tilemap = map_data["tilemap"]
        self.tile_size = map_data["tile_size"]
        self.offgrid_tiles = map_data["offgrid"]

    def solid_check(self, pos):
        tile_loc = str(int(pos[0]//self.tile_size)) + ';' + str(int(pos[1]//self.tile_size)) #get tile coordinates
        if tile_loc in self.tilemap:
            if self.tilemap[tile_loc]['type'] in PHYSICS_TILES:
                return self.tilemap[tile_loc]
    
    def physics_rects_around(self, pos, entity_size=None):
        """Return physics tile rects around the given position.
        Expands the search area based on `entity_size` to avoid misses that cause bouncing.
        """
        rects = []
        # Determine bounds in tile coordinates covering the entity rect with 1-tile padding
        width = entity_size[0] if entity_size else self.tile_size
        height = entity_size[1] if entity_size else self.tile_size
        x0 = int((pos[0] - self.tile_size) // self.tile_size)
        x1 = int((pos[0] + width + self.tile_size) // self.tile_size)
        y0 = int((pos[1] - self.tile_size) // self.tile_size)
        y1 = int((pos[1] + height + self.tile_size) // self.tile_size)

        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    if tile['type'] in PHYSICS_TILES:
                        rects.append(pygame.Rect(
                            tile['pos'][0] * self.tile_size,
                            tile['pos'][1] * self.tile_size,
                            self.tile_size,
                            self.tile_size
                        ))
        return rects
    
    def auto_tile(self):
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                if check_loc in self.tilemap:
                    neighbor_type = self.tilemap[check_loc]["type"]
                    # Check if tiles are compatible for autotiling
                    if tile["type"] in AUTOTILE_GROUPS:
                        if neighbor_type in AUTOTILE_GROUPS[tile["type"]]:
                            neighbors.add(shift)
                    elif neighbor_type == tile["type"]:
                        neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            # Special handling for water tiles: variant 0 on top surface, variant 1 elsewhere
            if tile["type"] == "water_tiles":
                # Check if there's water above (north neighbor)
                if (0, -1) not in neighbors:
                    tile["variant"] = 0  # Top surface
                else:
                    tile["variant"] = 1  # Everywhere else
            elif (tile["type"] in AUTOTILE_TILES) and (neighbors in AUTOTILE_MAP):
                tile["variant"] = AUTOTILE_MAP[neighbors]

    def randomize_tiles(self):
        import random
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            if tile["type"] in RANDOMIZE_TILES:
                tile["variant"] = random.randint(0, len(self.game.assets[tile["type"]]) - 1)

    def fill_tiles(self, tile_type, variant=0, padding=1):
        """Fill the currently visible grid (plus padding) with the given tile if empty.

        This is intentionally conservative: it only places tiles where none exist
        to avoid overwriting placed objects (spawners, powerups, etc.).
        """
        view_w, view_h = self.game.display.get_size()
        tiles_x = view_w // self.tile_size + padding * 2
        tiles_y = view_h // self.tile_size + padding * 2

        start_x = int(self.game.scroll[0] // self.tile_size) - padding
        start_y = int(self.game.scroll[1] // self.tile_size) - padding

        for x in range(start_x, start_x + tiles_x):
            for y in range(start_y, start_y + tiles_y):
                loc = f"{x};{y}"
                if loc not in self.tilemap:
                    self.tilemap[loc] = {"type": tile_type, "variant": variant, "pos": [x, y]}

    def render(self, surf, offset=(0, 0)):
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))
            
        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))

    def render_debug_hitboxes(self, surf, offset=(0, 0)):
        # Draw physics tile rectangles in green
        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    if tile['type'] in PHYSICS_TILES:
                        rect = pygame.Rect(
                            tile['pos'][0] * self.tile_size - offset[0],
                            tile['pos'][1] * self.tile_size - offset[1],
                            self.tile_size,
                            self.tile_size
                        )
                        pygame.draw.rect(surf, (0, 255, 0), rect, 1)