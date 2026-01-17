"""
Enhanced First-Person Dungeon Renderer with Tileset Support
Renders dungeon exploration using pre-rendered perspective tiles.
"""

import math
import os

import pygame
from PIL import Image


class EnhancedDungeonRenderer:
    """
    Advanced dungeon renderer using tileset-based approach.
    Loads and renders pre-made perspective tiles for authentic first-person view.
    """

    def __init__(self, presenter):
        self.presenter = presenter
        self.screen = presenter.screen
        self.width = presenter.width
        self.height = presenter.height

        # View dimensions
        self.view_width = int(self.width * 0.65)
        self.view_height = self.height
        self.view_rect = pygame.Rect(0, 0, self.view_width, self.view_height)

        # Horizon line (eye level)
        self.horizon = self.view_height // 2

        # Debug flags - must be set before loading tileset
        self.enable_gradients = True  # Set to False to disable gradient shading for debugging
        self.enable_darkness = True  # Set to False to disable darkness effects
        self.enable_vignette = False  # Set to False to disable vignette effects TODO: fix vignette rendering
        self.debug_mode = False  # Set to True to disable all effects for debugging

        # Animation time for torch flicker
        self.time = 0

        # --- Render caches (rebuilt on resize) ---
        self._cache_key = None  # (view_w, view_h)
        self._layer_cache = {}  # per-depth scaled perspective pieces + bg
        self._flat_cache = {}   # scaled/gradient flat corridor pieces (recursive corridors)
        self._vignette_surf = None
        self._torch_frames = []
        self._torch_frame_idx = 0
        self._torch_frame_count = 24
        self._torch_anim_ms = 120  # should match dungeon_manager’s anim interval
        self._last_torch_tick = 0

        # Damage flash overlay state
        self._damage_flash_active = False
        self._damage_flash_start = 0
        self._damage_flash_duration = 0
        self._damage_flash_alpha = 0
        self._damage_flash_color = (255, 64, 32)

        # Optimization: Precompute backgrounds for different depths/sizes
        self._bg_cache = {}  # (depth, w, h, alpha, dark_bg) -> Surface

        # Tie debug_mode to the game launcher
        if presenter.debug_mode:
            self.debug_mode = True
            self.enable_gradients = True
            self.enable_darkness = True
            self.enable_vignette = False

        # Optimization: Lazy load tileset to reduce initial loading time
        self.tiles = None  # Tileset will be loaded on first use

        # Special tiles (lazy-loaded)
        self._closed_door_base = None
        self._closed_door_cache = {}
        self._open_door_base = None
        self._open_door_cache = {}
        self._stairs_up_base = None
        self._stairs_up_cache = {}
        self._stairs_down_base = None
        self._stairs_down_cache = {}
        # Chest tiles (lazy-loaded)
        self._chest_locked_base = None
        self._chest_locked_cache = {}
        self._chest_unlocked_base = None
        self._chest_unlocked_cache = {}
        self._chest_open_base = None
        self._chest_open_cache = {}
        # Altar tiles (lazy-loaded) - for RelicRoom
        self._altar_bases = {}  # relic_num -> base image
        self._altar_caches = {}  # relic_num -> {depth -> scaled surface}

        # Color palette with atmospheric depth
        self.colors = {
            # Stone/wall colors with variation - cooler gray tones
            'stone_base': (75, 75, 75),
            'stone_light': (100, 100, 100),
            'stone_dark': (50, 50, 50),
            'stone_mortar': (55, 55, 55),

            # Floor colors - darker stone
            'floor_base': (40, 40, 42),
            'floor_dark': (28, 28, 30),

            # Ceiling - darkest
            'ceiling_base': (18, 18, 20),
            'ceiling_dark': (10, 10, 12),

            # Lighting - subtle warm glow instead of dominant yellow
            'torch_bright': (220, 200, 170),
            'torch_dim': (100, 90, 70),
            'ambient': (45, 45, 50),

            # Special elements
            'door': (90, 60, 30),
            'door_metal': (120, 120, 130),
            'chest': (139, 90, 43),
            'gold': (255, 215, 0),
            'enemy_red': (180, 40, 40),
            'stairs_up': (100, 140, 200),
            'stairs_down': (200, 120, 80),
            'magic_glow': (180, 140, 255),
        }

        # Define perspective rendering zones
        # Layer 1, 2, and 3 for proper depth
        self.zones = [
            # Layer 3 (far distance - 2 tiles ahead)
            # 25% size, 80% darker, centered
            {
                'distance': 3,
                'wall_top': 0.44,
                'wall_bottom': 0.56,
                'wall_width': 0.25,  # 25% of screen width
                'darkness': 0.80,
            },
            # Layer 2 (middle distance - 1 tile ahead)
            # 50% size, 40% darker, centered
            {
                'distance': 2,
                'wall_top': 0.38,
                'wall_bottom': 0.62,
                'wall_width': 0.50,  # 50% of screen width
                'darkness': 0.40,
            },
            # Layer 1 (current cell - immediate surroundings)
            # Full size, base brightness
            {
                'distance': 1,
                'wall_top': 0.05,
                'wall_bottom': 0.95,
                'wall_width': 1.0,  # 100% of screen width
                'darkness': 0.0,
            },
        ]

    def _load_tileset(self):
        """Load raw texture files from the tileset pack.

        Following the Screaming Brain Studios tutorial approach,
        we load seamless textures which will be transformed at runtime.
        Load base textures (512x512) and scale them at runtime for each layer.
        """
        tiles = {}

        # Load base textures from consolidated PNG files
        tileset_base = "assets/dungeon_tiles"

        # Texture selections - single PNG file per type
        # Includes standard floor types and special tile floor variants
        textures = {
            'wall': 'walls/brick.png',
            'floor': 'floors/dirt.png',
            'ceiling': 'ceilings/stone.png',
            'floor_fire': 'floors/firepath.png',  # FirePath floor
            'floor_spring': 'special_tiles/underground_spring.png',  # Underground Spring floor
        }

        # Load base texture and scale to required sizes
        for tex_type, file_path in textures.items():
            tiles[tex_type] = {}
            full_path = os.path.join(tileset_base, file_path)
            try:
                base_image = pygame.image.load(full_path).convert_alpha()
                # Store base image and create scaled versions for each layer
                tiles[tex_type][512] = base_image
                # Scale for Layer 2 (256x256)
                tiles[tex_type][256] = pygame.transform.smoothscale(base_image, (256, 256))
                # Scale for Layer 3 (128x128)
                tiles[tex_type][128] = pygame.transform.smoothscale(base_image, (128, 128))
            except Exception as e:
                print(f"Warning: Could not load texture {full_path}: {e}")
                tiles[tex_type][512] = None
                tiles[tex_type][256] = None
                tiles[tex_type][128] = None

        # Pre-generate perspective tiles for each layer
        # Layer 1: 512x512 (foreground)
        # Layer 2: 256x256 (middle distance), scaled from base
        # Layer 3: 128x128 (far distance), scaled from base
        tiles['perspective'] = {}
        for layer in [1, 2, 3]:
            tiles['perspective'][layer] = self._generate_perspective_tiles(tiles, layer)

        return tiles

    def _get_floor_texture_for_tile(self, tile, base_size):
        """Get the appropriate floor texture based on tile type.
        
        Args:
            tile: The map tile object
            base_size: The base texture size (512, 256, or 128)
            
        Returns:
            The floor texture surface, or default floor if no special texture
        """
        if not tile:
            return self.tiles.get('floor', {}).get(base_size)
        
        tile_type = type(tile).__name__
        
        # Check for special floor types
        if 'FirePath' in tile_type:
            floor_tex = self.tiles.get('floor_fire', {}).get(base_size)
            if floor_tex:
                return floor_tex
        
        if 'UndergroundSpring' in tile_type:
            floor_tex = self.tiles.get('floor_spring', {}).get(base_size)
            if floor_tex:
                return floor_tex
        
        # Default to regular floor
        return self.tiles.get('floor', {}).get(base_size)

    def _generate_perspective_tiles(self, textures, layer):
        """Generate perspective-transformed tiles for a given layer.

        Following the tutorial:
        - Back wall: 1/2 size of layer, centered
        - Left/Right walls: Perspective skewed, 1/4 width
        - Top/Bottom: Perspective skewed, fill to back wall edges
        - Layer 1: 512x512, 0% darker (foreground)
        - Layer 2: 256x256, 40% darker (middle)
        - Layer 3: 128x128, 80% darker (background)
        """
        tiles = {}

        # Base size and darkness for this layer
        # Darkness is based on distance from player:
        # Layer 1 (1 tile away): 0.0 darkness (full brightness)
        # Layer 2 (2 tiles away): 0.4 darkness
        # Layer 3 (3 tiles away): 0.8 darkness (very dark)
        if layer == 1:
            base_size = 512
            darkness = 0.0  # Walls at 1 tile distance - full brightness
        elif layer == 2:
            base_size = 256
            darkness = 0.4  # Walls at 2 tiles distance - half brightness
        else:  # layer == 3
            base_size = 128
            darkness = 0.8  # Walls at 3 tiles distance - very dark

        # Get textures at the appropriate size for this layer
        wall_tex = textures.get('wall', {}).get(base_size)
        floor_tex = textures.get('floor', {}).get(base_size)
        ceiling_tex = textures.get('ceiling', {}).get(base_size)
        floor_fire_tex = textures.get('floor_fire', {}).get(base_size)
        floor_spring_tex = textures.get('floor_spring', {}).get(base_size)

        if not wall_tex:
            return tiles

        # Create back wall - simple scaled version
        tiles['back'] = self._create_back_wall(wall_tex, base_size, darkness)

        # Create left and right walls - perspective skewed
        # These need to be created with pygame transforms
        tiles['left'] = self._create_side_wall(wall_tex, base_size, 'left', darkness, layer)
        tiles['right'] = self._create_side_wall(wall_tex, base_size, 'right', darkness, layer)

        # Create side corridor walls - thin vertical strips for when corridors are open
        # These represent the wall continuing past the corridor opening
        tiles['left_corridor'] = self._create_corridor_wall(wall_tex, base_size, 'left', darkness)
        tiles['right_corridor'] = self._create_corridor_wall(wall_tex, base_size, 'right', darkness)

        # Create floor and ceiling
        tiles['floor'] = self._create_floor_ceiling(floor_tex, base_size, 'floor', darkness, layer)
        tiles['floor_left'] = self._create_side_floor_ceiling(floor_tex, base_size, 'floor', darkness, layer, 'left')
        tiles['floor_right'] = self._create_side_floor_ceiling(floor_tex, base_size, 'floor', darkness, layer, 'right')
        tiles['ceiling'] = self._create_floor_ceiling(ceiling_tex, base_size, 'ceiling', darkness, layer)
        tiles['ceiling_left'] = self._create_side_floor_ceiling(ceiling_tex, base_size, 'ceiling', darkness, layer, 'left')
        tiles['ceiling_right'] = self._create_side_floor_ceiling(ceiling_tex, base_size, 'ceiling', darkness, layer, 'right')

        # Create special floor tiles with perspective transformation
        if floor_fire_tex:
            tiles['floor_fire'] = self._create_floor_ceiling(floor_fire_tex, base_size, 'floor', darkness, layer)
            tiles['floor_fire_left'] = self._create_side_floor_ceiling(floor_fire_tex, base_size, 'floor', darkness, layer, 'left')
            tiles['floor_fire_right'] = self._create_side_floor_ceiling(floor_fire_tex, base_size, 'floor', darkness, layer, 'right')

        if floor_spring_tex:
            tiles['floor_spring'] = self._create_floor_ceiling(floor_spring_tex, base_size, 'floor', darkness, layer)
            tiles['floor_spring_left'] = self._create_side_floor_ceiling(floor_spring_tex, base_size, 'floor', darkness, layer, 'left')
            tiles['floor_spring_right'] = self._create_side_floor_ceiling(floor_spring_tex, base_size, 'floor', darkness, layer, 'right')

        return tiles

    def _get_perspective_coeffs(self, source_points, target_points):
        """Calculate coefficients for perspective transform.

        Args:
            source_points: List of 4 (x,y) tuples - corners of source quad
            target_points: List of 4 (x,y) tuples - corners of target quad

        Returns:
            8-tuple of coefficients for PIL perspective transform
        """
        matrix = []
        for s, t in zip(source_points, target_points):
            matrix.append([t[0], t[1], 1, 0, 0, 0, -s[0]*t[0], -s[0]*t[1]])
            matrix.append([0, 0, 0, t[0], t[1], 1, -s[1]*t[0], -s[1]*t[1]])

        A = []
        B = []
        for i, row in enumerate(matrix):
            A.append(row)
            B.append(source_points[i//2][i%2])

        # Solve using numpy if available, otherwise use simple method
        try:
            import numpy as np
            A = np.matrix(A, dtype=float)
            B = np.array(B).reshape(8)
            res = np.linalg.solve(A, B)
            return tuple(res)
        except:
            # Fallback: just return identity-ish transform
            return (1, 0, 0, 0, 1, 0, 0, 0)

    def _pil_to_pygame(self, pil_image):
        """Convert PIL Image to pygame Surface."""
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()

        return pygame.image.fromstring(data, size, mode)

    def _create_back_wall(self, texture, base_size, darkness):
        """Create the back wall texture for a given layer.

        The back wall is simply a scaled version of the wall texture,
        sized to half the base size for that layer.
        """
        back_size = base_size // 2
        scaled_back = pygame.transform.scale(texture, (back_size, back_size))

        return scaled_back

    def _create_corridor_wall(self, texture, base_size, side, darkness):
        """Create a half-width wall section for side corridors.

        When there's an open corridor to the left/right, we use half of the back wall
        from this layer to show the wall continuing into the corridor.
        This is literally half of the center/back wall texture.
        """
        # This should be half the back wall size
        back_size = base_size // 2
        half_width = back_size // 2  # Half of the back wall

        # Convert pygame surface to PIL Image
        texture_string = pygame.image.tostring(texture, 'RGBA')
        pil_image = Image.frombytes('RGBA', texture.get_size(), texture_string)

        # Scale to back wall size first
        pil_image = pil_image.resize((back_size, back_size), Image.LANCZOS)

        # Crop to get half of it
        if side == 'left':
            # Take the right half for left corridor
            half_wall = pil_image.crop((half_width, 0, back_size, back_size))
        else:  # right
            # Take the left half for right corridor
            half_wall = pil_image.crop((0, 0, half_width, back_size))

        # Convert back to pygame
        surf = self._pil_to_pygame(half_wall)

        if darkness > 0:
            surf = self._apply_darkness_to_surface(surf, darkness)

        return surf

    def _create_side_wall(self, texture, base_size, side, darkness, layer):
        """Create a perspective-skewed side wall using PIL transforms.

        Following tutorial: walls need perspective distortion to create depth.
        We use PIL's perspective transform to create trapezoid-shaped walls.
        """
        wall_width = base_size
        wall_height = base_size

        # Convert pygame surface to PIL Image
        texture_string = pygame.image.tostring(texture, 'RGBA')
        pil_image = Image.frombytes('RGBA', texture.get_size(), texture_string)

        # Create a larger working canvas to apply perspective
        work_size = base_size
        pil_image = pil_image.resize((work_size, work_size), Image.LANCZOS)

        # Tutorial approach: Use perspective tool to skew the texture
        # Inset: 16 grid squares on 512px = 128px, so for any size: base_size/4
        inset = base_size // 4

        if side == 'left':
            # Left wall: trapezoid with right edge angled inward
            # We want to create a shape that's full height on left, angles in on right
            # Use perspective transform with these corner mappings:
            # Output corners -> Source texture sample points
            coeffs = self._get_perspective_coeffs(
                # Destination quad (output image corners)
                [(0, 0), (wall_width, 0), (wall_width, wall_height), (0, wall_height)],
                # Source quad (where to sample from in texture)
                [(0, 0), (wall_width, inset), (wall_width, wall_height-inset), (0, wall_height)]
            )
        else:  # right
            # Right wall: trapezoid with left edge angled inward
            coeffs = self._get_perspective_coeffs(
                # Destination quad (output image corners)
                [(0, 0), (wall_width, 0), (wall_width, wall_height), (0, wall_height)],
                # Source quad (where to sample from in texture)
                [(0, inset), (wall_width, 0), (wall_width, wall_height), (0, wall_height-inset)]
            )

        # Apply perspective transform
        wall_pil = pil_image.transform(
            (wall_width, wall_height),
            Image.PERSPECTIVE,
            coeffs,
            Image.BICUBIC
        )

        # Convert back to pygame surface
        wall_surf = self._pil_to_pygame(wall_pil)

        # Apply gradient shading
        wall_surf = self._apply_wall_gradient(wall_surf, side, darkness, layer)

        return wall_surf

    def _create_floor_ceiling(self, texture, base_size, type_name, darkness, layer):
        """Create perspective-transformed floor or ceiling using PIL.

        Floor/ceiling need to narrow toward the back to create depth perspective.
        """
        width = base_size
        height = base_size

        # Convert pygame surface to PIL Image
        texture_string = pygame.image.tostring(texture, 'RGBA')
        pil_image = Image.frombytes('RGBA', texture.get_size(), texture_string)

        # Scale texture to working size
        pil_image = pil_image.resize((width, width), Image.LANCZOS)

        # Inset for perspective (1/4 of width on each side at far edge)
        inset = width // 4

        # Calculate perspective coefficients
        if type_name == 'floor':
            # Floor: wide at bottom (close), narrow at top (far)
            coeffs = self._get_perspective_coeffs(
                # Output corners
                [(0, 0), (width, 0), (width, height), (0, height)],
                # Source sample points - compressed at top
                [(inset, 0), (width-inset, 0), (width, height), (0, height)]
            )
        else:  # ceiling
            # Ceiling: wide at top (close), narrow at bottom (far)
            coeffs = self._get_perspective_coeffs(
                # Output corners
                [(0, 0), (width, 0), (width, height), (0, height)],
                # Source sample points - compressed at bottom
                [(0, 0), (width, 0), (width-inset, height), (inset, height)]
            )

        # Apply perspective transform
        transformed = pil_image.transform(
            (width, height),
            Image.PERSPECTIVE,
            coeffs,
            Image.BICUBIC
        )

        # Convert back to pygame
        surf = self._pil_to_pygame(transformed)

        # Apply gradient shading
        if type_name == 'floor':
            surf = self._apply_floor_ceiling_gradient(surf, 'floor', darkness, layer)
        else:
            surf = self._apply_floor_ceiling_gradient(surf, 'ceiling', darkness, layer)

        return surf

    def _create_side_floor_ceiling(self, texture, base_size, type_name, darkness, layer, side):
        """Create perspective-transformed floor/ceiling for side corridors.

        These have opposite perspective - wide on the outer edge (left/right),
        narrow toward the center.
        """
        # Side tiles should be same dimensions as center tiles for proper alignment
        width = base_size // 2
        height = base_size // 2  # Half the base_size to match composition proportions

        # Convert pygame surface to PIL Image
        texture_string = pygame.image.tostring(texture, 'RGBA')
        pil_image = Image.frombytes('RGBA', texture.get_size(), texture_string)

        # Scale texture to working size first
        pil_image = pil_image.resize((width, width), Image.LANCZOS)

        # Inset for perspective (1/4 of width on each side at far edge)
        inset = width // 4

        # Calculate perspective coefficients
        if type_name == 'floor':
            # Side floor uses inverted perspective (like center ceiling)
            # Narrow at bottom, wide at top
            coeffs = self._get_perspective_coeffs(
                # Output corners
                [(0, 0), (width, 0), (width, height), (0, height)],
                # Source sample points - compressed at bottom (like ceiling)
                [(0, 0), (width, 0), (width-inset, height), (inset, height)]
            )
        else:  # ceiling
            # Side ceiling uses inverted perspective (like center floor)
            # Narrow at top, wide at bottom
            coeffs = self._get_perspective_coeffs(
                # Output corners
                [(0, 0), (width, 0), (width, height), (0, height)],
                # Source sample points - compressed at top (like floor)
                [(inset, 0), (width-inset, 0), (width, height), (0, height)]
            )

        # Apply perspective transform
        transformed = pil_image.transform(
            (width, height),
            Image.PERSPECTIVE,
            coeffs,
            Image.BICUBIC
        )

        # Crop to get half of it (like corridor walls)
        half_width = width // 2
        if side == 'left':
            # Take the right half for left corridor
            half_wall = transformed.crop((half_width, 0, width, height))
        else:  # right
            # Take the left half for right corridor
            half_wall = transformed.crop((0, 0, half_width, height))

        # Convert back to pygame
        surf = self._pil_to_pygame(half_wall)

        # Apply gradient shading (sideways gradient instead of forward)
        surf = self._apply_side_floor_ceiling_gradient(surf, type_name, darkness, layer)

        return surf

    def _apply_darkness_to_surface(self, surface, darkness):
        """Apply darkness multiplier to a surface."""
        if darkness == 0:
            return surface

        # Clamp darkness to [0, 1] range
        darkness = max(0.0, min(1.0, darkness))

        # Ensure surface has alpha channel
        if surface.get_flags() & pygame.SRCALPHA:
            dark_surf = surface.copy()
        else:
            dark_surf = surface.convert_alpha()

        factor = 1.0 - darkness

        # Multiply all RGB values by factor
        dark_surf.fill((int(255 * factor), int(255 * factor), int(255 * factor), 255),
                       special_flags=pygame.BLEND_RGBA_MULT)

        return dark_surf

    def _apply_wall_gradient(self, surface, side, base_darkness, layer):
        """Apply gradient shading to wall following tutorial.

        Walls get darker towards the back (right edge for left wall, left edge for right wall).
        Uses pygame blend modes for performance.
        Tutorial specifies using Grain Merge blend mode, but we approximate with multiply.
        """
        if not self.enable_gradients:
            return surface  # Return original surface when gradient disabled

        grad_surf = surface.copy()
        width, height = grad_surf.get_size()

        # Create a gradient surface
        gradient = pygame.Surface((width, height), pygame.SRCALPHA)

        for x in range(width):
            # Gradient from light (front) to dark (back)
            if side == 'left':
                ratio = x / width  # 0 at left (front) to 1 at right (back)
            else:
                ratio = 1.0 - (x / width)  # 1 at left (back) to 0 at right (front)

            # Gradient from base_darkness (front edge) to next layer's darkness (back edge)
            # The back edge should match the next layer's base darkness for seamless transition
            if layer < 3:
                target_darkness = base_darkness + 0.4  # Transition to next layer
            else:
                target_darkness = base_darkness  # Layer 3 stays dark

            darkness = base_darkness + (ratio * (target_darkness - base_darkness))
            factor = int(255 * max(0, 1.0 - darkness))

            # Draw vertical line with calculated darkness
            pygame.draw.line(gradient, (factor, factor, factor, 255), (x, 0), (x, height))

        # Apply gradient using multiply blend
        grad_surf.blit(gradient, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Add slight brightness adjustment to the base (as per tutorial step)
        # Left and right walls should be -50 brightness in tutorial
        darkness_overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        darkness_overlay.fill((200, 200, 200, 255))  # 20% darker
        grad_surf.blit(darkness_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        return grad_surf

    def _apply_floor_ceiling_gradient(self, surface, type_name, base_darkness, layer):
        """Apply gradient to floor/ceiling - darker towards back.
        Uses pygame blend modes for performance.
        Tutorial shows floor/ceiling should have perspective gradient.
        """
        if not self.enable_gradients:
            return surface  # Return original surface when gradient disabled

        grad_surf = surface.copy()
        width, height = grad_surf.get_size()

        # Create a gradient surface
        gradient = pygame.Surface((width, height), pygame.SRCALPHA)

        for y in range(height):
            # Gradient from front to back
            if type_name == 'floor':
                ratio = 1.0 - (y / height)  # Bright at bottom (close), dark at top (far)
            else:  # ceiling
                ratio = y / height  # Bright at top (close), dark at bottom (far)

            # Gradient transitions to match next layer; cap at full darkness
            if layer < 3:
                target_darkness = min(1.0, base_darkness + 0.4)
            else:
                target_darkness = base_darkness

            darkness = min(1.0, base_darkness + (ratio * (target_darkness - base_darkness)))
            factor = int(255 * max(0, 1.0 - darkness))

            # Draw horizontal line with calculated darkness
            pygame.draw.line(gradient, (factor, factor, factor, 255), (0, y), (width, y))

        # Apply gradient using multiply blend
        grad_surf.blit(gradient, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Ceiling should be darker overall (tutorial: -75 brightness)
        if type_name == 'ceiling':
            ceiling_darkness = pygame.Surface((width, height), pygame.SRCALPHA)
            ceiling_darkness.fill((180, 180, 180, 255))  # ~30% darker
            grad_surf.blit(ceiling_darkness, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        return grad_surf

    def _apply_side_floor_ceiling_gradient(self, surface, type_name, base_darkness, layer):
        """Apply gradient to side corridor floor/ceiling.

        The gradient follows the perspective depth - from near (wide) to far (narrow).
        For inverted perspective tiles: floor is narrow at bottom, ceiling is narrow at top.
        """
        if not self.enable_gradients:
            return surface  # Return original surface when gradient disabled

        grad_surf = surface.copy()
        width, height = grad_surf.get_size()

        # Create a gradient surface
        gradient = pygame.Surface((width, height), pygame.SRCALPHA)

        for y in range(height):
            # Gradient from near (bright) to far (dark) following the perspective
            if type_name == 'floor':
                # Floor: narrow at bottom (far), wide at top (near)
                # So bright at top (near), dark at bottom (far)
                ratio = 1.0 - (y / height)  # 1 at top (near) to 0 at bottom (far)
            else:  # ceiling
                # Ceiling: narrow at top (far), wide at bottom (near)
                # So bright at bottom (near), dark at top (far)
                ratio = y / height  # 0 at top (far) to 1 at bottom (near)

            # Gradient transitions to match next layer; cap at full darkness
            if layer < 3:
                target_darkness = min(1.0, base_darkness + 0.4)
            else:
                target_darkness = base_darkness

            darkness = min(1.0, base_darkness + (ratio * (target_darkness - base_darkness)))
            factor = int(255 * max(0, 1.0 - darkness))

            # Draw horizontal line with calculated darkness
            pygame.draw.line(gradient, (factor, factor, factor, 255), (0, y), (width, y))

        # Apply gradient using multiply blend
        grad_surf.blit(gradient, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Ceiling should be darker overall
        if type_name == 'ceiling':
            ceiling_darkness = pygame.Surface((width, height), pygame.SRCALPHA)
            ceiling_darkness.fill((180, 180, 180, 255))  # ~30% darker
            grad_surf.blit(ceiling_darkness, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        return grad_surf

    def get_visible_tiles(self, player_char, world_dict):
        """Get tiles visible from player's current position.

        Returns tiles at various depths:
        - Depth 1: Immediately in front of player
        - Depth 2: Two tiles ahead
        - Depth 3: Three tiles ahead
        """
        from player import DIRECTIONS

        x, y, z = player_char.location_x, player_char.location_y, player_char.location_z
        facing = player_char.facing

        dx, dy = DIRECTIONS[facing]["move"]

        # Perpendicular directions for left/right
        perpendicular = {
            "north": {"left": (-1, 0), "right": (1, 0)},
            "south": {"left": (1, 0), "right": (-1, 0)},
            "east": {"left": (0, -1), "right": (0, 1)},
            "west": {"left": (0, 1), "right": (0, -1)},
        }

        left_dx, left_dy = perpendicular[facing]["left"]
        right_dx, right_dy = perpendicular[facing]["right"]

        visible = {}

        # Following the tutorial pattern, we need to gather all potentially visible tiles
        # Layer 1: 3 tiles (center ahead, left/right from current position)
        # Layer 2: 5 tiles (center 2 ahead, left/right from 1 ahead, left2/right2 from 1 ahead)
        # Layer 3: 9 tiles (center 3 ahead, left/right from 2 ahead, left2/right2 from 2 ahead,
        #                   center-left/center-right from 2 ahead, left3/right3 from 2 ahead)

        for layer in range(1, 4):
            # Center tile: looking ahead 'layer' tiles
            forward_x = x + (dx * layer)
            forward_y = y + (dy * layer)
            center_tile = world_dict.get((forward_x, forward_y, z))

            # Side tiles: checking at depth layer-1 (where the side walls are)
            # For Layer 1, this is depth 0 (current position)
            # For Layer 2, this is depth 1 (one tile ahead)
            # For Layer 3, this is depth 2 (two tiles ahead)
            side_depth = layer - 1
            side_x = x + (dx * side_depth)
            side_y = y + (dy * side_depth)

            left_tile = world_dict.get((side_x + left_dx, side_y + left_dy, z))
            right_tile = world_dict.get((side_x + right_dx, side_y + right_dy, z))

            # Store with layer as key
            visible[layer] = {
                # Center: straight ahead at this layer
                'center': center_tile,
                # Left: to the left at the side wall position
                'left': left_tile,
                # Right: to the right at the side wall position
                'right': right_tile,
                # Far left: two tiles to the left at side wall position
                'left2': world_dict.get((side_x + left_dx*2, side_y + left_dy*2, z)),
                # Far right: two tiles to the right at side wall position
                'right2': world_dict.get((side_x + right_dx*2, side_y + right_dy*2, z)),
                # Center-left and center-right (diagonal visibility at this depth)
                'center_left': world_dict.get((forward_x + left_dx, forward_y + left_dy, z)),
                'center_right': world_dict.get((forward_x + right_dx, forward_y + right_dy, z)),
                # Far left: three tiles forward and two left (diagonal at depth 3)
                'left3': world_dict.get((x + dx*3 + left_dx*2, y + dy*3 + left_dy*2, z)),
                # Far right: three tiles forward and two right (diagonal at depth 3)
                'right3': world_dict.get((x + dx*3 + right_dx*2, y + dy*3 + right_dy*2, z)),
                # Center-left2: two tiles forward and one left (diagonal at depth 2)
                'center_left2': world_dict.get((x + dx*2 + left_dx, y + dy*2 + left_dy, z)),
                # Center-right2: two tiles forward and one right (diagonal at depth 2)
                'center_right2': world_dict.get((x + dx*2 + right_dx, y + dy*2 + right_dy, z)),
            }

        return visible

    def render_dungeon_view(self, player_char, world_dict):
        """Render the enhanced first-person dungeon view."""
        self._ensure_caches()
        self.time += 0.05
        
        # Store player_char for access in tile content rendering
        self.player_char = player_char
        # Keep a reference to the world dict for tile lookups
        self.world_dict = world_dict
        # Store current tile for correct floor selection at depth 1
        try:
            x, y, z = player_char.location_x, player_char.location_y, player_char.location_z
            self.current_tile = world_dict.get((x, y, z))
        except Exception:
            self.current_tile = None

        # Start with black background
        self.screen.fill((0, 0, 0))

        # Ensure tileset is loaded before rendering
        self._ensure_tileset_loaded()

        # Get visible tiles
        visible = self.get_visible_tiles(player_char, world_dict)

        # Render from far to near for proper depth
        for zone in self.zones:
            depth = int(zone['distance'])
            if depth in visible:
                next_tiles = visible.get(depth + 1) if depth < 3 else None
                self._render_zone(visible[depth], zone, depth, next_tiles, visible)

        # Add atmospheric torch lighting and vignette effects if not in debug mode
        if self.enable_vignette:
            self._render_torch_light()
            self._render_vignette()

    def _get_floor_source_tile(self, depth):
        """Return the map tile whose floor should render for a given depth layer.

        Depth mapping:
        - depth 1: current tile (under the player)
        - depth 2: one tile ahead
        - depth 3: two tiles ahead
        """
        try:
            from player import DIRECTIONS
            x = self.player_char.location_x
            y = self.player_char.location_y
            z = self.player_char.location_z
            facing = self.player_char.facing
            dx, dy = DIRECTIONS[facing]["move"]
            offset = depth - 1
            fx = x + dx * offset
            fy = y + dy * offset
            return self.world_dict.get((fx, fy, z))
        except Exception:
            return None

    def _render_zone(self, tiles, zone, depth, next_tiles=None, visible=None):
        """Render a depth layer using the new texture-based approach.

        Following the tutorial approach:
        - Layer 1 (depth=1): Full screen view of current cell (512x512)
        - Layer 2 (depth=2): Half-size centered view of next cell (256x256)
        - Layer 3 (depth=3): Quarter-size centered view of far cell (128x128)

        Composites: back wall, left wall, right wall, ceiling, floor

        Args:
            tiles: Tile data for this depth
            zone: Zone configuration
            depth: Depth layer (1, 2, or 3)
            next_tiles: Tiles at depth+1 for corridor continuation checks
            visible: Complete visible tiles dict with all depth layers
        """
        center_tile = tiles.get('center')
        left_tile = tiles.get('left')
        right_tile = tiles.get('right')

        # For side corridors, check if there's a wall when you step into the corridor
        # If the side is open (no wall blocking), check one step into that direction
        # to see if there's a back wall (player would hit a wall if they moved that way)
        left_has_back_wall = False
        left_is_open = False
        right_has_back_wall = False
        right_is_open = False

        # Left corridor: if left side is open, check center-left tile
        # This is the tile you'd see if you stepped left from the side wall position
        if left_tile is not None and not self._is_wall(left_tile):
            left_is_open = True
            center_left_tile = tiles.get('center_left')
            # Show back wall if there's a wall one step into the left corridor
            left_has_back_wall = center_left_tile is None or self._is_wall(center_left_tile)

        # Right corridor: if right side is open, check center-right tile
        # This is the tile you'd see if you stepped right from the side wall position
        if right_tile is not None and not self._is_wall(right_tile):
            right_is_open = True
            center_right_tile = tiles.get('center_right')
            # Show back wall if there's a wall one step into the right corridor
            right_has_back_wall = center_right_tile is None or self._is_wall(center_right_tile)

        # Check if side corridors continue to the next depth (for rendering deeper corridor elements)
        # Only relevant when corridor is open and has no back wall
        left_continues = False
        right_continues = False
        if next_tiles and depth < 3:
            # Left corridor continues if it's open here and also open at next depth
            if left_is_open and not left_has_back_wall:
                next_center_left = next_tiles.get('center_left')
                left_continues = next_center_left is not None and not self._is_wall(next_center_left)

            # Right corridor continues if it's open here and also open at next depth
            if right_is_open and not right_has_back_wall:
                next_center_right = next_tiles.get('center_right')
                right_continues = next_center_right is not None and not self._is_wall(next_center_right)

        # Get pre-generated perspective tiles for this layer
        layer_tiles = self.tiles.get('perspective', {}).get(depth, {})
        if not layer_tiles:
            return  # Skip rendering if tiles aren't ready

        # Calculate composition area
        if depth == 1:
            # Layer 1: Full screen (512x512)
            comp_width = self.view_width
            comp_height = self.view_height
            comp_x = 0
            comp_y = 0
        elif depth == 2:
            # Layer 2: Centered at 50% size (256x256)
            comp_width = self.view_width // 2
            comp_height = self.view_height // 2
            comp_x = (self.view_width - comp_width) // 2
            comp_y = (self.view_height - comp_height) // 2
        else:  # depth == 3
            # Layer 3: Centered at 25% size (128x128)
            comp_width = self.view_width // 4
            comp_height = self.view_height // 4
            comp_x = (self.view_width - comp_width) // 2
            comp_y = (self.view_height - comp_height) // 2

        # Retrieve layer cache (may be empty if caches not built)
        cache = self._layer_cache.get(depth, {})

        # Draw background with darkness
        dark_bg = (8, 8, 10) if depth == 1 else (18, 18, 20)
        alpha = 0 if depth == 2 else int(255 * zone.get("darkness", 0))

        bg = self._get_bg_surface(depth, comp_width, comp_height, alpha, dark_bg)
        self.screen.blit(bg, (comp_x, comp_y))

        # Calculate layout proportions
        left_w = comp_width // 4
        center_w = comp_width // 2
        right_w = comp_width - left_w - center_w  # absorb remainder

        top_h = comp_height // 4
        center_h = comp_height // 2
        bottom_h = comp_height - top_h - center_h  # absorb remainder

        # Track if we need to render recursive corridors (must be done LAST)
        left_recursive = None
        right_recursive = None

        # Render left side
        if left_tile is None or self._is_wall(left_tile):
            # Blocked - render full perspective wall
            # Prefer cached scaled wall if available
            left_cached = cache.get('left_full')
            if left_cached:
                self.screen.blit(left_cached, (comp_x, comp_y))
            elif 'left' in layer_tiles:
                left_surf = layer_tiles['left']
                scaled_left = pygame.transform.scale(left_surf, (left_w, comp_height))
                self.screen.blit(scaled_left, (comp_x, comp_y))
        else:
            # Open corridor to the left - use flat tiles for proper grid-based rendering
            # Get base textures (not perspective-transformed)
            base_size = 512 if depth == 1 else (256 if depth == 2 else 128)
            darkness_level = self._get_layer_darkness(depth)

            ceiling_tex = self.tiles.get('ceiling', {}).get(base_size)
            # Use the actual left tile for floor texture, not forward tile
            floor_tex = self._get_floor_texture_for_tile(left_tile, base_size)
            wall_tex = self.tiles.get('wall', {}).get(base_size)

            # Top section: ceiling - flat rectangular tile
            if ceiling_tex:
                scaled_ceiling = self._get_flat_piece(ceiling_tex, left_w, top_h, "ceiling", darkness_level, depth)
                self.screen.blit(scaled_ceiling, (comp_x, comp_y))

            # Bottom section: floor - flat rectangular tile
            if floor_tex:
                scaled_floor = self._get_flat_piece(floor_tex, left_w, bottom_h, "floor", darkness_level, depth)
                self.screen.blit(scaled_floor, (comp_x, comp_y + top_h + center_h))

            # Middle section: back wall or recursive next layer
            if left_has_back_wall and wall_tex:
                # There's a wall blocking one step into the corridor - crop and render the back wall
                # Use darkness of the layer BEYOND this wall (next depth)
                next_darkness = self._get_layer_darkness(depth)
                half_back_w = center_w // 2
                tex_w, tex_h = wall_tex.get_size()

                # For left corridor, take the right half of the texture
                crop_rect = pygame.Rect(tex_w // 2, 0, tex_w // 2, tex_h)
                cropped_wall = wall_tex.subsurface(crop_rect).copy()
                scaled_wall = pygame.transform.scale(cropped_wall, (half_back_w, center_h))

                if next_darkness > 0:
                    scaled_wall = self._apply_darkness_to_surface(scaled_wall, next_darkness)

                wall_x = comp_x + left_w - half_back_w
                wall_y = comp_y + top_h
                self.screen.blit(scaled_wall, (wall_x, wall_y))
            elif not left_has_back_wall and depth < 3 and next_tiles:
                # Corridor is open with no back wall - save for rendering AFTER full-width floor/ceiling
                # Pass visible dict so recursive calls can access all depth layers
                # Also render any special contents present immediately inside the corridor (altar, chest, etc.)
                center_left_tile = tiles.get('center_left')
                if center_left_tile and not self._is_wall(center_left_tile):
                    # self._render_tile_contents(center_left_tile, comp_x, comp_y + top_h,
                    #                           left_w, center_h, darkness_level, depth)
                    pass  # TODO: fix rendering of side objects
                left_recursive = (comp_x, comp_y + top_h, left_w, center_h, depth + 1, 'left', visible)

        # Render right side
        if right_tile is None or self._is_wall(right_tile):
            # Blocked - render full perspective wall
            # Prefer cached scaled wall if available
            right_cached = cache.get('right_full')
            if right_cached:
                right_x = comp_x + left_w + center_w
                self.screen.blit(right_cached, (right_x, comp_y))
            elif 'right' in layer_tiles:
                right_surf = layer_tiles['right']
                right_x = comp_x + left_w + center_w
                scaled_right = pygame.transform.scale(right_surf, (right_w, comp_height))
                self.screen.blit(scaled_right, (right_x, comp_y))
        else:
            # Open corridor to the right - use flat tiles for proper grid-based rendering
            # Get base textures (not perspective-transformed)
            base_size = 512 if depth == 1 else (256 if depth == 2 else 128)
            darkness_level = self._get_layer_darkness(depth)

            ceiling_tex = self.tiles.get('ceiling', {}).get(base_size)
            # Use the actual right tile for floor texture, not forward tile
            floor_tex = self._get_floor_texture_for_tile(right_tile, base_size)
            wall_tex = self.tiles.get('wall', {}).get(base_size)

            # Top section: ceiling - flat rectangular tile
            if ceiling_tex:
                scaled_ceiling = self._get_flat_piece(ceiling_tex, right_w, top_h, "ceiling", darkness_level, depth)
                self.screen.blit(scaled_ceiling, (comp_x + left_w + center_w, comp_y))

            # Bottom section: floor - flat rectangular tile
            if floor_tex:
                scaled_floor = self._get_flat_piece(floor_tex, right_w, bottom_h, "floor", darkness_level, depth)
                self.screen.blit(scaled_floor, (comp_x + left_w + center_w, comp_y + top_h + center_h))

            # Middle section: back wall or recursive next layer
            if right_has_back_wall and wall_tex:
                # There's a wall blocking one step into the corridor - crop and render the back wall
                # Use darkness of the layer BEYOND this wall (next depth)
                next_darkness = self._get_layer_darkness(depth)
                half_back_w = center_w // 2
                tex_w, tex_h = wall_tex.get_size()

                # For right corridor, take the left half of the texture
                crop_rect = pygame.Rect(0, 0, tex_w // 2, tex_h)
                cropped_wall = wall_tex.subsurface(crop_rect).copy()
                scaled_wall = pygame.transform.scale(cropped_wall, (half_back_w, center_h))

                if next_darkness > 0:
                    scaled_wall = self._apply_darkness_to_surface(scaled_wall, next_darkness)

                wall_x = comp_x + left_w + center_w
                wall_y = comp_y + top_h
                self.screen.blit(scaled_wall, (wall_x, wall_y))
            elif not right_has_back_wall and depth < 3 and next_tiles:
                # Corridor is open with no back wall - save for rendering AFTER full-width floor/ceiling
                # Pass visible dict so recursive calls can access all depth layers
                # Also render any special contents present immediately inside the corridor (altar, chest, etc.)
                center_right_tile = tiles.get('center_right')
                if center_right_tile and not self._is_wall(center_right_tile):
                    # self._render_tile_contents(center_right_tile, comp_x + left_w + center_w, comp_y + top_h,
                    #                           right_w, center_h, darkness_level, depth)
                    pass  # TODO: fix rendering of side objects
                right_recursive = (comp_x + left_w + center_w, comp_y + top_h, right_w, center_h, depth + 1, 'right', visible)

        # Render floor first (bottom section - full width)
        # For special floors (FirePath), render the special texture
        # For regular floors, use the perspective-transformed floor tile
        floor_x = comp_x
        floor_y = comp_y + top_h + center_h
        
        # Determine which floor tile to render based on map position offset for this depth
        tile_for_floor = self._get_floor_source_tile(depth)
        if tile_for_floor:
            tile_type_name = type(tile_for_floor).__name__
            if 'FirePath' in tile_type_name:
                floor_key = 'floor_fire'
            elif 'UndergroundSpring' in tile_type_name:
                floor_key = 'floor_spring'
            else:
                floor_key = 'floor'
        else:
            floor_key = 'floor'
        
        # Use perspective-transformed floor tile
        floor_cached = cache.get(floor_key + '_strip')
        if floor_cached:
            self.screen.blit(floor_cached, (floor_x, floor_y))
        elif floor_key in layer_tiles:
            floor_surf = layer_tiles[floor_key]
            scaled_floor = pygame.transform.scale(floor_surf, (comp_width, bottom_h))
            self.screen.blit(scaled_floor, (floor_x, floor_y))

        # Render ceiling (top section - full width)
        ceiling_cached = cache.get('ceiling_strip')
        if ceiling_cached:
            ceiling_x = comp_x
            ceiling_y = comp_y
            self.screen.blit(ceiling_cached, (ceiling_x, ceiling_y))
        elif 'ceiling' in layer_tiles:
            ceiling_surf = layer_tiles['ceiling']
            ceiling_x = comp_x
            ceiling_y = comp_y
            scaled_ceiling = pygame.transform.scale(ceiling_surf, (comp_width, top_h))
            self.screen.blit(scaled_ceiling, (ceiling_x, ceiling_y))

        # Render back wall (center - if blocked) - fills middle section
        if center_tile is None or self._is_wall(center_tile):
            # Use darkness of the layer BEYOND this wall (next depth)
            next_darkness = self._get_layer_darkness(depth)
            back_cached = cache.get('back_center')
            if back_cached:
                back_x = comp_x + left_w
                back_y = comp_y + top_h
                # Apply next layer darkness to cached back wall
                darkened_back = self._apply_darkness_to_surface(back_cached, next_darkness)
                self.screen.blit(darkened_back, (back_x, back_y))
            elif 'back' in layer_tiles:
                back_surf = layer_tiles['back']
                # Back wall fills the center section (middle 50% both width and height)
                back_x = comp_x + left_w
                back_y = comp_y + top_h
                scaled_back = pygame.transform.scale(back_surf, (center_w, center_h))
                if next_darkness > 0:
                    scaled_back = self._apply_darkness_to_surface(scaled_back, next_darkness)
                self.screen.blit(scaled_back, (back_x, back_y))

        # Render special tile contents (doors, stairs, etc.)
        if center_tile:
            darkness_level = self._get_layer_darkness(depth)
            tile_type = type(center_tile).__name__
            
            # Special handling for OreVaultDoor - only render as door if detected or open
            if tile_type == 'OreVaultDoor':
                is_open = getattr(center_tile, 'open', False)
                is_detected = getattr(center_tile, 'detected', False)
                if is_open or is_detected:
                    # Render as door if detected or open
                    self._render_door(center_tile, comp_x + left_w, comp_y + top_h, center_w, center_h,
                                     darkness_level, depth)
                # Otherwise it's already rendered as a wall by the back wall logic above
            elif 'Door' in tile_type:
                # Regular door - render normally
                self._render_door(center_tile, comp_x + left_w, comp_y + top_h, center_w, center_h,
                                 darkness_level, depth)
            elif not self._is_wall(center_tile):
                # Open path - render tile contents (chests, stairs)
                # Pass the zone rect for proper positioning and sizing
                self._render_tile_contents(center_tile, comp_x + left_w, comp_y + top_h, 
                                          center_w, center_h, darkness_level, depth)

        # Render recursive corridors LAST so they appear on top
        if left_recursive:
            self._render_recursive_corridor(*left_recursive)
        if right_recursive:
            self._render_recursive_corridor(*right_recursive)

    def _get_closed_door_tile(self, depth):
        """Load and scale the closed door tile for the given depth."""
        size_map = {1: 512, 2: 256, 3: 128}

        # Load base image lazily
        if self._closed_door_base is None:
            door_path = os.path.join('assets', 'dungeon_tiles', 'special_tiles', 'closed_door.png')
            if os.path.exists(door_path):
                try:
                    self._closed_door_base = pygame.image.load(door_path).convert_alpha()
                except Exception as e:
                    print(f"Failed to load closed door tile {door_path}: {e}")
                    self._closed_door_base = None
            else:
                self._closed_door_base = None

        if depth not in size_map or self._closed_door_base is None:
            return None

        # Return cached scaled tile if available
        if depth in self._closed_door_cache:
            return self._closed_door_cache[depth]

        target_size = size_map[depth]
        scaled = pygame.transform.smoothscale(self._closed_door_base, (target_size, target_size))
        self._closed_door_cache[depth] = scaled
        return scaled

    def _get_open_door_tile(self, depth):
        """Load and scale the open door tile for the given depth."""
        size_map = {1: 512, 2: 256, 3: 128}

        # Load base image lazily
        if self._open_door_base is None:
            door_path = os.path.join('assets', 'dungeon_tiles', 'special_tiles', 'opened_door.png')
            if os.path.exists(door_path):
                try:
                    self._open_door_base = pygame.image.load(door_path).convert_alpha()
                except Exception as e:
                    print(f"Failed to load open door tile {door_path}: {e}")
                    self._open_door_base = None
            else:
                self._open_door_base = None

        if depth not in size_map or self._open_door_base is None:
            return None

        # Return cached scaled tile if available
        if depth in self._open_door_cache:
            return self._open_door_cache[depth]

        target_size = size_map[depth]
        scaled = pygame.transform.smoothscale(self._open_door_base, (target_size, target_size))
        self._open_door_cache[depth] = scaled
        return scaled

    def _get_stairs_up_tile(self, depth):
        """Load and scale the stairs up tile for the given depth."""
        size_map = {1: 512, 2: 256, 3: 128}

        # Load base image lazily
        if self._stairs_up_base is None:
            stairs_path = os.path.join('assets', 'dungeon_tiles', 'special_tiles', 'stairs_up.png')
            if os.path.exists(stairs_path):
                try:
                    self._stairs_up_base = pygame.image.load(stairs_path).convert_alpha()
                except Exception as e:
                    print(f"Failed to load stairs up tile {stairs_path}: {e}")
                    self._stairs_up_base = None
            else:
                self._stairs_up_base = None

        if depth not in size_map or self._stairs_up_base is None:
            return None

        # Return cached scaled tile if available
        if depth in self._stairs_up_cache:
            return self._stairs_up_cache[depth]

        target_size = size_map[depth]
        scaled = pygame.transform.smoothscale(self._stairs_up_base, (target_size, target_size))
        self._stairs_up_cache[depth] = scaled
        return scaled

    def _get_stairs_down_tile(self, depth):
        """Load and scale the stairs down tile for the given depth."""
        size_map = {1: 512, 2: 256, 3: 128}

        # Load base image lazily
        if self._stairs_down_base is None:
            stairs_path = os.path.join('assets', 'dungeon_tiles', 'special_tiles', 'stairs_down.png')
            if os.path.exists(stairs_path):
                try:
                    self._stairs_down_base = pygame.image.load(stairs_path).convert_alpha()
                except Exception as e:
                    print(f"Failed to load stairs down tile {stairs_path}: {e}")
                    self._stairs_down_base = None
            else:
                self._stairs_down_base = None

        if depth not in size_map or self._stairs_down_base is None:
            return None

        # Return cached scaled tile if available
        if depth in self._stairs_down_cache:
            return self._stairs_down_cache[depth]

        target_size = size_map[depth]
        scaled = pygame.transform.smoothscale(self._stairs_down_base, (target_size, target_size))
        self._stairs_down_cache[depth] = scaled
        return scaled

    def _render_door(self, door_tile_obj, x, y, width, height, darkness, depth):
        """Render a door (open or closed) using the appropriate pre-made tile."""
        # Determine if door is open based on door object attributes
        is_open = getattr(door_tile_obj, 'open', False)
        
        # Get the appropriate tile
        if is_open:
            door_tile = self._get_open_door_tile(depth)
        else:
            door_tile = self._get_closed_door_tile(depth)

        if door_tile:
            # Scale if needed
            if door_tile.get_width() != width or door_tile.get_height() != height:
                door_surf = pygame.transform.smoothscale(door_tile, (width, height))
            else:
                door_surf = door_tile.copy()  # Copy to avoid modifying cached tile

            # Apply darkness and blit
            door_surf = self._apply_darkness_to_surface(door_surf, darkness)
            self.screen.blit(door_surf, (x, y))
            return

        # Fallback: simple colored door if the tile is missing
        door_color = self._apply_darkness(self.colors['door'], darkness)
        frame_color = self._apply_darkness(self.colors.get('door_metal', (120, 120, 130)), darkness)
        door_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, door_color, door_rect)
        pygame.draw.rect(self.screen, frame_color, door_rect, max(2, int(width * 0.03)))

    def _render_recursive_corridor(self, x, y, width, height, depth, side, visible):
        """
        Recursively render a side corridor view showing what's at the next depth.
        This creates nested perspective by subdividing the view into ceiling/content/floor.
        Uses flat rectangular tiles, not perspective-transformed ones.

        Args:
            x, y: Position to render at
            width, height: Size of the area to fill
            depth: Current depth layer (2 or 3)
            side: 'left' or 'right' - which corridor we're rendering
            visible: Complete visible tiles dict with all depth layers
        """
        if depth > 3 or not visible or depth not in visible:
            return

        # Get tiles for this depth
        tiles_dict = visible[depth]
        
        # Get the center tile in the corridor to check for special floor types
        check_tile = tiles_dict.get(f'center_{side}')

        # Get base textures for this depth (not perspective-transformed)
        base_size = 512 if depth == 1 else (256 if depth == 2 else 128)
        darkness = self._get_layer_darkness(depth)

        ceiling_tex = self.tiles.get('ceiling', {}).get(base_size)
        offset_tile = self._get_floor_source_tile(depth)
        floor_tex = self._get_floor_texture_for_tile(offset_tile, base_size)
        wall_tex = self.tiles.get('wall', {}).get(base_size)

        if not ceiling_tex or not floor_tex:
            return

        # Subdivide the space: top 25% ceiling, middle 50% content, bottom 25% floor
        top_h = height // 4
        center_h = height // 2
        bottom_h = height - top_h - center_h

        # Render ceiling (top quarter) - flat rectangular tile
        if ceiling_tex:
            ceiling_surf = self._get_flat_piece(ceiling_tex, width, top_h, 'ceiling', darkness, depth)
            if ceiling_surf:
                self.screen.blit(ceiling_surf, (x, y))

        # Render floor (bottom quarter) - flat rectangular tile
        if floor_tex:
            floor_surf = self._get_flat_piece(floor_tex, width, bottom_h, 'floor', darkness, depth)
            if floor_surf:
                self.screen.blit(floor_surf, (x, y + top_h + center_h))

        # Middle section: check what's at this depth in the side corridor
        # Check if the corridor continues by looking for a back wall one step in
        check_tile = tiles_dict.get(f'center_{side}')
        has_wall = check_tile is None or self._is_wall(check_tile)

        # Middle section: show back wall if blocked, otherwise render contents and/or recurse deeper
        if has_wall and wall_tex:
            wall_w = width
            scaled_wall = pygame.transform.scale(wall_tex, (wall_w, center_h))

            if darkness > 0:
                scaled_wall = self._apply_darkness_to_surface(scaled_wall, darkness)

            wall_x = x + width - wall_w if side == 'left' else x
            self.screen.blit(scaled_wall, (wall_x, y + top_h))
        else:
            # Open corridor with no immediate back wall
            # First render any special contents in the immediate corridor tile (altar, chest, etc.)
            content_tile = tiles_dict.get(f'center_{side}')
            if content_tile and not self._is_wall(content_tile):
                self._render_tile_contents(content_tile, x, y + top_h, width, center_h, darkness, depth)

            # Then recurse deeper using the full middle band; if at max depth or no tiles, leave void (black)
            if depth < 3 and visible and (depth + 1) in visible:
                next_w = width
                next_h = center_h
                next_x = x
                next_y = y + top_h
                self._render_recursive_corridor(next_x, next_y, next_w, next_h, depth + 1, side, visible)

    def _get_flat_piece(self, base_tex, w, h, kind, darkness, depth):
        """
        kind: 'ceiling' or 'floor'
        """
        if base_tex is None:
            return None

        # Quantize darkness to stabilize cache keys
        d = int(darkness * 255)
        key = ("flat", depth, w, h, kind, d, id(base_tex))

        cached = self._flat_cache.get(key)
        if cached is not None:
            return cached

        surf = pygame.transform.smoothscale(base_tex, (w, h))
        # Always apply gradient to match center floor/ceiling rendering
        surf = self._apply_floor_ceiling_gradient(surf, kind, darkness, depth)
        self._flat_cache[key] = surf
        return surf

    def _render_tile_contents(self, tile, x, y, width, height, darkness, depth):
        """Render special tile contents like stairs, chests, enemies."""
        if not tile:
            return

        tile_type = type(tile).__name__

        if 'StairsUp' in tile_type:
            self._render_stairs_up(x, y, width, height, darkness, depth)
        elif 'StairsDown' in tile_type:
            self._render_stairs_down(x, y, width, height, darkness, depth)
        elif 'Chest' in tile_type:
            is_open = bool(getattr(tile, 'opened', False) or getattr(tile, 'open', False))
            is_locked = bool(getattr(tile, 'locked', False))
            self._render_chest(x, y, width, height, darkness, depth, is_open=is_open, is_locked=is_locked)
        elif 'RelicRoom' in tile_type:
            # Render altar sprite based on dungeon level (1-6 maps to relic 1-6)
            # Use player's current Z location as the relic number
            relic_num = getattr(self, 'player_char', None)
            if relic_num:
                relic_num = relic_num.location_z
            else:
                relic_num = 1  # fallback
            is_collected = bool(getattr(tile, 'read', False))
            self._render_altar(x, y, width, height, darkness, depth, relic_num, is_collected)
        elif 'UnobtainiumRoom' in tile_type:
            # Render Unobtainium ore on the ground unless already looted
            is_looted = bool(getattr(tile, 'visited', False))
            self._render_unobtainium(x, y, width, height, darkness, depth, is_looted)
        # Additional tile contents (enemies, relics, etc.) can be added here as needed

    def _render_chest(self, x, y, width, height, darkness, depth, is_open=False, is_locked=False):
        """Render a chest using pre-made tiles, bottom-aligned to sit on the floor."""
        # Select appropriate chest tile based on state
        if is_open:
            chest_tile = self._get_chest_open_tile(depth)
        elif is_locked:
            chest_tile = self._get_chest_locked_tile(depth)
        else:
            chest_tile = self._get_chest_unlocked_tile(depth)

        # Determine on-screen chest size (square) based on depth
        # Bottom-align so the chest sits on the floor line
        if depth == 1:
            size_ratio = 0.55
        elif depth == 2:
            size_ratio = 0.45
        else:
            size_ratio = 0.35
        chest_size = max(8, int(height * size_ratio))
        chest_x = x + (width - chest_size) // 2
        chest_y = y + height - chest_size

        if chest_tile:
            # Scale to square size and bottom-align
            chest_surf = pygame.transform.smoothscale(chest_tile, (chest_size, chest_size))
            chest_surf = self._apply_darkness_to_surface(chest_surf, darkness)
            self.screen.blit(chest_surf, (chest_x, chest_y))
            return

        # Fallback: simple colored rectangle if tiles are missing
        base_color = self.colors['chest']
        if is_open:
            chest_color = self._apply_darkness(self._blend_color(base_color, (255, 215, 0), 0.25), darkness)
        elif is_locked:
            chest_color = self._apply_darkness(self._blend_color(base_color, (120, 120, 130), 0.25), darkness)
        else:
            chest_color = self._apply_darkness(base_color, darkness)
        chest_rect = pygame.Rect(chest_x, chest_y, chest_size, chest_size)
        pygame.draw.rect(self.screen, chest_color, chest_rect)

    def _blend_color(self, c1, c2, t):
        """Linear blend between two RGB colors."""
        return (
            int(c1[0] * (1 - t) + c2[0] * t),
            int(c1[1] * (1 - t) + c2[1] * t),
            int(c1[2] * (1 - t) + c2[2] * t),
        )

    def _get_chest_locked_tile(self, depth):
        """Load and scale the locked chest tile for the given depth."""
        size_map = {1: 512, 2: 256, 3: 128}

        # Lazy-load base image
        if self._chest_locked_base is None:
            chest_path = os.path.join('assets', 'dungeon_tiles', 'special_tiles', 'closed_locked_chest.png')
            if os.path.exists(chest_path):
                try:
                    self._chest_locked_base = pygame.image.load(chest_path).convert_alpha()
                except Exception as e:
                    print(f"Failed to load locked chest tile {chest_path}: {e}")
                    self._chest_locked_base = None
            else:
                self._chest_locked_base = None

        if depth not in size_map or self._chest_locked_base is None:
            return None

        if depth in self._chest_locked_cache:
            return self._chest_locked_cache[depth]

        target_size = size_map[depth]
        scaled = pygame.transform.smoothscale(self._chest_locked_base, (target_size, target_size))
        self._chest_locked_cache[depth] = scaled
        return scaled

    def _get_chest_unlocked_tile(self, depth):
        """Load and scale the unlocked (closed) chest tile for the given depth."""
        size_map = {1: 512, 2: 256, 3: 128}

        if self._chest_unlocked_base is None:
            chest_path = os.path.join('assets', 'dungeon_tiles', 'special_tiles', 'closed_unlocked_chest.png')
            if os.path.exists(chest_path):
                try:
                    self._chest_unlocked_base = pygame.image.load(chest_path).convert_alpha()
                except Exception as e:
                    print(f"Failed to load unlocked chest tile {chest_path}: {e}")
                    self._chest_unlocked_base = None
            else:
                self._chest_unlocked_base = None

        if depth not in size_map or self._chest_unlocked_base is None:
            return None

        if depth in self._chest_unlocked_cache:
            return self._chest_unlocked_cache[depth]

        target_size = size_map[depth]
        scaled = pygame.transform.smoothscale(self._chest_unlocked_base, (target_size, target_size))
        self._chest_unlocked_cache[depth] = scaled
        return scaled

    def _get_chest_open_tile(self, depth):
        """Load and scale the open chest tile for the given depth."""
        size_map = {1: 512, 2: 256, 3: 128}

        if self._chest_open_base is None:
            chest_path = os.path.join('assets', 'dungeon_tiles', 'special_tiles', 'opened_chest.png')
            if os.path.exists(chest_path):
                try:
                    self._chest_open_base = pygame.image.load(chest_path).convert_alpha()
                except Exception as e:
                    print(f"Failed to load open chest tile {chest_path}: {e}")
                    self._chest_open_base = None
            else:
                self._chest_open_base = None

        if depth not in size_map or self._chest_open_base is None:
            return None

        if depth in self._chest_open_cache:
            return self._chest_open_cache[depth]

        target_size = size_map[depth]
        scaled = pygame.transform.smoothscale(self._chest_open_base, (target_size, target_size))
        self._chest_open_cache[depth] = scaled
        return scaled
    
    def _get_altar_tile(self, relic_num, depth, is_collected):
        """Load and scale the altar tile for the given relic number and depth."""
        size_map = {1: 512, 2: 256, 3: 128}
        
        # Determine which altar image to use
        if is_collected:
            altar_name = 'empty_altar.png'
        else:
            # Map relic numbers to altar names
            altar_names = {
                1: 'luna_altar.png',
                2: 'polaris_altar.png',
                3: 'triangulus_altar.png',
                4: 'quadrata_altar.png',
                5: 'hexagonum_altar.png',
                6: 'infinitas_altar.png'
            }
            altar_name = altar_names.get(relic_num, 'empty_altar.png')
        
        # Lazy-load base image for this altar type
        cache_key = altar_name
        if cache_key not in self._altar_bases:
            altar_path = os.path.join('assets', 'dungeon_tiles', 'special_tiles', altar_name)
            if os.path.exists(altar_path):
                try:
                    self._altar_bases[cache_key] = pygame.image.load(altar_path).convert_alpha()
                    self._altar_caches[cache_key] = {}
                except Exception as e:
                    print(f"Failed to load altar tile {altar_path}: {e}")
                    self._altar_bases[cache_key] = None
            else:
                self._altar_bases[cache_key] = None
        
        base_img = self._altar_bases.get(cache_key)
        if depth not in size_map or base_img is None:
            return None
        
        # Check cache for this specific altar and depth
        if cache_key not in self._altar_caches:
            self._altar_caches[cache_key] = {}
        
        if depth in self._altar_caches[cache_key]:
            return self._altar_caches[cache_key][depth]
        
        # Scale and cache
        target_size = size_map[depth]
        scaled = pygame.transform.smoothscale(base_img, (target_size, target_size))
        self._altar_caches[cache_key][depth] = scaled
        return scaled
    
    def _render_altar(self, x, y, width, height, darkness, depth, relic_num, is_collected):
        """Render an altar using pre-made tiles, bottom-aligned to sit on the floor."""
        altar_tile = self._get_altar_tile(relic_num, depth, is_collected)
        
        # Determine on-screen altar size (square) based on depth
        # Bottom-align so the altar sits on the floor line
        if depth == 1:
            size_ratio = 0.6
        elif depth == 2:
            size_ratio = 0.5
        else:
            size_ratio = 0.4
        altar_size = max(8, int(height * size_ratio))
        altar_x = x + (width - altar_size) // 2
        altar_y = y + height - altar_size
        
        if altar_tile:
            # Scale to square size and bottom-align
            altar_surf = pygame.transform.smoothscale(altar_tile, (altar_size, altar_size))
            altar_surf = self._apply_darkness_to_surface(altar_surf, darkness)
            self.screen.blit(altar_surf, (altar_x, altar_y))
            return
        
        # Fallback: simple colored rectangle if tiles are missing
        altar_color = self._apply_darkness((120, 120, 140), darkness)
        altar_rect = pygame.Rect(altar_x, altar_y, altar_size, altar_size)
        pygame.draw.rect(self.screen, altar_color, altar_rect)
        
    def _render_stairs_up(self, x, y, width, height, darkness, depth):
        """Render ascending stairs using the pre-made tile."""
        stairs_tile = self._get_stairs_up_tile(depth)

        if stairs_tile:
            # Scale if needed
            if stairs_tile.get_width() != width or stairs_tile.get_height() != height:
                stairs_surf = pygame.transform.smoothscale(stairs_tile, (width, height))
            else:
                stairs_surf = stairs_tile.copy()  # Copy to avoid modifying cached tile

            # Apply darkness and blit
            stairs_surf = self._apply_darkness_to_surface(stairs_surf, darkness)
            self.screen.blit(stairs_surf, (x, y))
            return

        # Fallback: simple colored rectangle if tile is missing
        stairs_color = self._apply_darkness(self.colors.get('stairs_up', (100, 130, 160)), darkness)
        stairs_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, stairs_color, stairs_rect)
    
    def _render_stairs_down(self, x, y, width, height, darkness, depth):
        """Render descending stairs using the pre-made tile."""
        stairs_tile = self._get_stairs_down_tile(depth)

        if stairs_tile:
            # Scale if needed
            if stairs_tile.get_width() != width or stairs_tile.get_height() != height:
                stairs_surf = pygame.transform.smoothscale(stairs_tile, (width, height))
            else:
                stairs_surf = stairs_tile.copy()  # Copy to avoid modifying cached tile

            # Apply darkness and blit
            stairs_surf = self._apply_darkness_to_surface(stairs_surf, darkness)
            self.screen.blit(stairs_surf, (x, y))
            return

        # Fallback: simple colored rectangle if tile is missing
        stairs_color = self._apply_darkness(self.colors.get('stairs_down', (160, 110, 70)), darkness)
        stairs_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, stairs_color, stairs_rect)

    def _get_unobtainium_tile(self, depth):
        """Load and scale the Unobtainium sprite for the given depth."""
        size_map = {1: 256, 2: 192, 3: 128}

        # Lazy-load base image
        if not hasattr(self, '_unobtainium_base'):
            self._unobtainium_base = None
        if not hasattr(self, '_unobtainium_cache'):
            self._unobtainium_cache = {}

        if self._unobtainium_base is None:
            ore_path = os.path.join('assets', 'sprites', 'relics', 'unobtainium.png')
            if os.path.exists(ore_path):
                try:
                    self._unobtainium_base = pygame.image.load(ore_path).convert_alpha()
                except Exception as e:
                    print(f"Failed to load unobtainium sprite {ore_path}: {e}")
                    self._unobtainium_base = None
            else:
                self._unobtainium_base = None

        if depth not in size_map or self._unobtainium_base is None:
            return None

        if depth in self._unobtainium_cache:
            return self._unobtainium_cache[depth]

        target_size = size_map[depth]
        scaled = pygame.transform.smoothscale(self._unobtainium_base, (target_size, target_size))
        self._unobtainium_cache[depth] = scaled
        return scaled

    def _render_unobtainium(self, x, y, width, height, darkness, depth, is_looted):
        """Render an Unobtainium ore on the ground, bottom-aligned to the floor line."""
        if is_looted:
            return

        ore_tile = self._get_unobtainium_tile(depth)

        # Determine on-screen size based on depth; bottom-align to sit on floor
        if depth == 1:
            size_ratio = 0.45
        elif depth == 2:
            size_ratio = 0.38
        else:
            size_ratio = 0.32
        ore_size = max(8, int(height * size_ratio))
        ore_x = x + (width - ore_size) // 2
        ore_y = y + height - ore_size

        if ore_tile:
            ore_surf = pygame.transform.smoothscale(ore_tile, (ore_size, ore_size))
            ore_surf = self._apply_darkness_to_surface(ore_surf, darkness)
            self.screen.blit(ore_surf, (ore_x, ore_y))
            return

        # Fallback: simple colored gem if sprite missing
        base_color = self._apply_darkness((100, 220, 220), darkness)
        pygame.draw.circle(self.screen, base_color, (ore_x + ore_size // 2, ore_y + ore_size // 2), ore_size // 2)
        highlight_color = self._apply_darkness((200, 255, 255), darkness)
        highlight_size = max(2, ore_size // 4)
        highlight_x = ore_x + ore_size // 3
        highlight_y = ore_y + ore_size // 3
        pygame.draw.circle(self.screen, highlight_color, (highlight_x, highlight_y), highlight_size)

    def _render_torch_light(self):
        if not self._torch_frames:
            return

        now = pygame.time.get_ticks()
        if now - self._last_torch_tick >= self._torch_anim_ms:
            self._torch_frame_idx = (self._torch_frame_idx + 1) % len(self._torch_frames)
            self._last_torch_tick = now

        self.screen.blit(self._torch_frames[self._torch_frame_idx], (0, 0))

    def _build_torch_frames(self, w, h, n=24):
        frames = []
        # Center-ish warm glow; adjust to taste
        cx = int(w * 0.5)
        cy = int(h * 0.55)
        base_radius = int(min(w, h) * 0.55)

        for k in range(n):
            surf = pygame.Surface((w, h), pygame.SRCALPHA)

            # Deterministic flicker factor
            # (no random needed; stable animation)
            flicker = 0.85 + 0.15 * math.sin((2 * math.pi * k) / n)

            # Draw a few concentric circles (like your current approach, but prebuilt)
            rings = 14
            for r in range(rings, 0, -1):
                radius = int(base_radius * (r / rings) * flicker)
                alpha = int(18 * (r / rings) ** 2)
                pygame.draw.circle(surf, (220, 200, 170, alpha), (cx, cy), radius)

            frames.append(surf)

        return frames

    def _render_vignette(self):
        if self._vignette_surf:
            self.screen.blit(self._vignette_surf, (0, 0))

    def _build_vignette_surface(self, w, h):
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        steps = 180  # adjust softness
        for i in range(steps):
            t = i / steps
            alpha = int(200 * (t * t))  # quadratic falloff
            pygame.draw.rect(surf, (0, 0, 0, alpha), (i, i, w - 2*i, h - 2*i), 1)
        return surf

    def _ensure_caches(self):
        """Rebuild scaled surfaces when view size changes."""
        key = (self.view_width, self.view_height)
        if key == self._cache_key and self._vignette_surf and self._torch_frames and self._layer_cache:
            return

        self._cache_key = key
        self._layer_cache.clear()
        self._flat_cache.clear()

        # Ensure tileset is loaded before accessing it
        self._ensure_tileset_loaded()

        # Prebuild vignette once
        self._vignette_surf = self._build_vignette_surface(self.view_width, self.view_height)

        # Prebuild torch flicker frames once
        self._torch_frames = self._build_torch_frames(
            self.view_width, self.view_height,
            n=self._torch_frame_count
        )
        self._torch_frame_idx = 0
        self._last_torch_tick = pygame.time.get_ticks()

        # Disable torch flicker in debug mode
        if not self.enable_vignette:
            self._torch_frames = []
            self._torch_frame_idx = 0
            self._torch_frame_count = 0
            self._torch_anim_ms = 0

        # Adjust darkness levels in debug mode
        if not self.enable_darkness:
            for zone in self.zones:
                zone['darkness'] = 0.0

        # Pre-scale perspective pieces for each depth (these are FIXED per depth)
        for depth in (1, 2, 3):
            layer_tiles = self.tiles.get('perspective', {}).get(depth, {})
            if not layer_tiles:
                continue

            # Match your existing comp sizing logic
            if depth == 1:
                comp_w, comp_h = self.view_width, self.view_height
            elif depth == 2:
                comp_w, comp_h = self.view_width // 2, self.view_height // 2
            else:
                comp_w, comp_h = self.view_width // 4, self.view_height // 4

            left_w = comp_w // 4
            right_w = comp_w // 4
            center_w = comp_w // 2

            top_h = comp_h // 4
            bottom_h = comp_h // 4
            center_h = comp_h // 2

            # Cache what _render_zone repeatedly scales every time you move
            self._layer_cache[depth] = {
                # side walls fill the entire comp height in your code
                "left_full": pygame.transform.smoothscale(layer_tiles["left"], (left_w, comp_h)) if "left" in layer_tiles else None,
                "right_full": pygame.transform.smoothscale(layer_tiles["right"], (right_w, comp_h)) if "right" in layer_tiles else None,
                # floor/ceiling strips
                "floor_strip": pygame.transform.smoothscale(layer_tiles["floor"], (comp_w, bottom_h)) if "floor" in layer_tiles else None,
                "floor_fire_strip": pygame.transform.smoothscale(layer_tiles["floor_fire"], (comp_w, bottom_h)) if "floor_fire" in layer_tiles else None,
                "floor_spring_strip": pygame.transform.smoothscale(layer_tiles["floor_spring"], (comp_w, bottom_h)) if "floor_spring" in layer_tiles else None,
                "ceiling_strip": pygame.transform.smoothscale(layer_tiles["ceiling"], (comp_w, top_h)) if "ceiling" in layer_tiles else None,
                # back wall fills center section only
                "back_center": pygame.transform.smoothscale(layer_tiles["back"], (center_w, center_h)) if "back" in layer_tiles else None,
            }

    def _ensure_tileset_loaded(self):
        """Ensure the tileset is loaded before rendering."""
        if self.tiles is None:
            self.tiles = self._load_tileset()

    def _is_wall(self, tile):
        """Check if a tile is a wall."""
        if not tile:
            return True

        tile_type = type(tile).__name__

        # FakeWall shows as wall until discovered
        if tile_type == 'FakeWall':
            return not getattr(tile, 'visited', False)

        # OreVaultDoor shows as wall until detected or opened
        if tile_type == 'OreVaultDoor':
            is_open = getattr(tile, 'open', False)
            is_detected = getattr(tile, 'detected', False)
            # Show as wall if not open and not detected
            return not (is_open or is_detected)

        # Wall tiles have enter=False, walkable tiles have enter=True
        # If no enter attribute, assume it's a wall (safer default)
        enter = getattr(tile, 'enter', False)
        return enter == False

    def _apply_darkness(self, color, darkness):
        """Apply darkness factor to a color."""
        factor = 1.0 - darkness
        return tuple(int(c * factor) for c in color)

    def trigger_damage_flash(self, duration_ms=700, alpha=255, color=(255, 32, 16)):
        """Kick off a brief red flash to signal incoming damage."""
        now = pygame.time.get_ticks()
        self._damage_flash_active = True
        self._damage_flash_start = now
        self._damage_flash_duration = max(1, duration_ms)
        self._damage_flash_alpha = max(0, min(255, alpha))
        self._damage_flash_color = color

    def render_damage_flash(self):
        """Render a fading damage flash overlay if active."""
        if not self._damage_flash_active:
            return

        now = pygame.time.get_ticks()
        elapsed = now - self._damage_flash_start

        if elapsed >= self._damage_flash_duration:
            self._damage_flash_active = False
            return

        t = 1.0 - (elapsed / self._damage_flash_duration)
        alpha = int(self._damage_flash_alpha * max(0.0, min(1.0, t)))
        if alpha <= 0:
            self._damage_flash_active = False
            return

        flash_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        flash_surface.fill((self._damage_flash_color[0],
                    self._damage_flash_color[1],
                    self._damage_flash_color[2],
                    alpha))

        # Render above everything, including message/hud layers
        self.screen.blit(flash_surface, (0, 0))

    def _get_layer_darkness(self, depth):
        """Return darkness for a given layer.

        Tuned to avoid overly dark appearance behind nearby objects.
        Depth 1 (one tile ahead): light dimming.
        Depth 2 (two tiles ahead): moderate dimming.
        Depth 3: max (not typically used).
        """
        if depth == 1:
            return 0.0
        elif depth == 2:
            return 0.4
        else:
            return 0.8

    def _lerp_color(self, color1, color2, t):
        """Linear interpolation between two colors."""
        t = max(0, min(1, t))
        return tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip(color1, color2))

    def render_message_area(self, messages):
        """Render message log at bottom of screen."""
        msg_height = 100

        # Semi-transparent background
        msg_surface = pygame.Surface((self.view_width, msg_height), pygame.SRCALPHA)
        msg_surface.fill((20, 20, 25, 200))
        self.screen.blit(msg_surface, (0, self.view_height - msg_height))

        # Render messages (last 4-5 messages)
        font = pygame.font.Font(None, 24)
        y_offset = self.view_height - msg_height + 10

        for msg in messages[-4:]:  # Show last 4 messages
            text_surface = font.render(msg, True, (220, 220, 220))
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 22

    def _get_bg_surface(self, depth, w, h, alpha, dark_bg):
        key = (depth, w, h, alpha, dark_bg)
        surf = self._bg_cache.get(key)
        if surf is not None:
            return surf

        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        # Fill with dark_bg but use alpha directly
        surf.fill((dark_bg[0], dark_bg[1], dark_bg[2], alpha))
        self._bg_cache[key] = surf
        return surf
