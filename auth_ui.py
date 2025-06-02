import cv2
import pygame
from pygame.locals import *

class AuthUI:
    def __init__(self):
        pygame.font.init()
        self.username = ""
        self.password = ""
        self.active_input = None
        self.message = ""
        self.message_color = (255, 150, 150)  # Softer red with more vibrancy
        self.registration_mode = False
        
        # Modern 3D color scheme with depth
        self.bg_color = (15, 20, 30)  # Darker blue-gray for better contrast
        self.card_color = (25, 35, 50)  # Base card color
        self.card_shadow = (10, 15, 25)  # Shadow color
        self.input_color = (35, 45, 65)  # Input field color
        self.active_input_color = (55, 75, 95)  # Active input
        self.text_color = (245, 245, 250)  # Brighter off-white
        self.accent_color = (80, 170, 255)  # More vibrant blue
        self.button_color = (60, 140, 210)  # Primary button
        self.button_hover_color = (80, 160, 230)  # Hover state
        self.secondary_button_color = (50, 60, 80)  # Secondary button
        self.secondary_hover_color = (70, 80, 100)
        
        # 3D effect parameters
        self.shadow_offset = 5
        self.bevel_size = 2
        self.highlight_color = (255, 255, 255, 50)
        
        # Fonts (try to load a custom font if available)
        try:
            self.title_font = pygame.font.Font("fonts/raleway-bold.ttf", 44)
            self.header_font = pygame.font.Font("fonts/raleway-semibold.ttf", 34)
            self.input_font = pygame.font.Font("fonts/raleway-regular.ttf", 30)
            self.button_font = pygame.font.Font("fonts/raleway-medium.ttf", 28)
        except:
            # Fallback to system fonts with slightly larger sizes
            self.title_font = pygame.font.Font(None, 44)
            self.header_font = pygame.font.Font(None, 34)
            self.input_font = pygame.font.Font(None, 30)
            self.button_font = pygame.font.Font(None, 28)
        
        # UI Elements
        self.title = "ALIEN INVASION"
        self.subtitle = "Player Authentication"
        self.camera_preview = None
        self.camera_rect = pygame.Rect(500, 150, 320, 240)  # Camera on right
        
        # Decorative elements with 3D effects
        self.accent_line_height = 6  # Thicker accent line
        self.card_rect = pygame.Rect(50, 80, 420, 480)  # Main content card
        self.card_elevation = 10  # How much the card appears to float
        
    def create_auth_ui(self, screen, registration_mode):
        """Draw the authentication interface with modern 3D styling"""
        screen.fill(self.bg_color)
        screen_width, screen_height = screen.get_size()
        
        # Draw decorative accent line at top with glow effect
        accent_line = pygame.Surface((screen_width, self.accent_line_height), pygame.SRCALPHA)
        pygame.draw.rect(accent_line, (*self.accent_color, 200), (0, 0, screen_width, self.accent_line_height))
        screen.blit(accent_line, (0, 0))
        
        # Draw subtle grid pattern in background
        self._draw_grid_background(screen)
        
        # Draw card shadow first (for 3D effect)
        shadow_rect = self.card_rect.move(self.shadow_offset, self.shadow_offset)
        pygame.draw.rect(screen, self.card_shadow, shadow_rect, border_radius=12)
        
        # Draw content card with 3D bevel effect
        card_surface = pygame.Surface((self.card_rect.width, self.card_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(card_surface, (*self.card_color, 240), 
                        (0, 0, self.card_rect.width, self.card_rect.height), 
                        border_radius=12)
        
        # Add bevel effect to card
        self._draw_bevel(card_surface, (0, 0, self.card_rect.width, self.card_rect.height), 
                        self.bevel_size, border_radius=12)
        
        screen.blit(card_surface, self.card_rect.topleft)
        
        # Title with two lines and subtle text shadow
        title_surf = self.title_font.render(self.title, True, self.accent_color)
        title_shadow = self.title_font.render(self.title, True, (0, 0, 0, 100))
        subtitle_surf = self.header_font.render(self.subtitle, True, self.text_color)
        subtitle_shadow = self.header_font.render(self.subtitle, True, (0, 0, 0, 100))
        
        # Draw shadows first
        screen.blit(title_shadow, (self.card_rect.x + 32, self.card_rect.y + 32))
        screen.blit(subtitle_shadow, (self.card_rect.x + 32, self.card_rect.y + 77))
        
        # Then draw main text
        screen.blit(title_surf, (self.card_rect.x + 30, self.card_rect.y + 30))
        screen.blit(subtitle_surf, (self.card_rect.x + 30, self.card_rect.y + 75))
        
        # Mode indicator with icon and glow effect
        mode_text = "REGISTER NEW PLAYER" if registration_mode else "SIGN IN"
        mode_icon = "✎" if registration_mode else "⎋"
        mode_surf = self.header_font.render(f"{mode_icon}  {mode_text}", True, self.text_color)
        
        # Create glow effect
        glow = pygame.Surface((mode_surf.get_width() + 20, mode_surf.get_height() + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*self.accent_color, 30), (0, 0, glow.get_width(), glow.get_height()), border_radius=20)
        screen.blit(glow, (self.card_rect.x + 20, self.card_rect.y + 125))
        
        screen.blit(mode_surf, (self.card_rect.x + 30, self.card_rect.y + 130))
        
        # Input fields with modern 3D styling
        self._draw_input_field(screen, "Username", self.username, 180, 
                             self.active_input == "username", "👤")
        self._draw_input_field(screen, "Password", "*" * len(self.password), 260, 
                             self.active_input == "password", "🔒")
        
        # Buttons with 3D styling
        button_x = self.card_rect.x + 30
        self._draw_button(screen, "Login", button_x, 340, not registration_mode, "→")
        self._draw_button(screen, "Register", button_x, 400, registration_mode, "+")
        self._draw_button(screen, "Capture Photo", button_x, 460, False, "📷")
        
        # Enhanced camera preview with 3D frame
        self._draw_camera_preview(screen)
        
        # Message display with icon and animation
        if self.message:
            self._draw_message(screen)
        
        # Subtle watermark with glow
        watermark = self.button_font.render("Alien Invasion v1.0", True, (120, 120, 140))
        watermark_glow = pygame.Surface((watermark.get_width() + 10, watermark.get_height() + 4), pygame.SRCALPHA)
        pygame.draw.rect(watermark_glow, (0, 0, 0, 50), (0, 0, watermark_glow.get_width(), watermark_glow.get_height()), border_radius=4)
        screen.blit(watermark_glow, (15, screen_height - 34))
        screen.blit(watermark, (20, screen_height - 30))
    
    def _draw_grid_background(self, screen):
        """Draw a subtle grid pattern for depth"""
        grid_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        cell_size = 40
        for x in range(0, screen.get_width(), cell_size):
            pygame.draw.line(grid_surface, (255, 255, 255, 5), (x, 0), (x, screen.get_height()))
        for y in range(0, screen.get_height(), cell_size):
            pygame.draw.line(grid_surface, (255, 255, 255, 5), (0, y), (screen.get_width(), y))
        screen.blit(grid_surface, (0, 0))
    
    def _draw_bevel(self, surface, rect, size, border_radius=0):
        """Draw a 3D bevel effect on a rectangle"""
        bevel_rect = pygame.Rect(rect)
        
        # Top and left highlights
        highlight = pygame.Surface((bevel_rect.width, size), pygame.SRCALPHA)
        pygame.draw.rect(highlight, self.highlight_color, (0, 0, bevel_rect.width, size), 
                        border_top_left_radius=border_radius, 
                        border_top_right_radius=border_radius)
        surface.blit(highlight, (bevel_rect.x, bevel_rect.y))
        
        highlight = pygame.Surface((size, bevel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight, self.highlight_color, (0, 0, size, bevel_rect.height), 
                        border_top_left_radius=border_radius, 
                        border_bottom_left_radius=border_radius)
        surface.blit(highlight, (bevel_rect.x, bevel_rect.y))
        
        # Bottom and right shadows
        shadow_color = (0, 0, 0, 40)
        shadow = pygame.Surface((bevel_rect.width, size), pygame.SRCALPHA)
        pygame.draw.rect(shadow, shadow_color, (0, 0, bevel_rect.width, size), 
                        border_bottom_left_radius=border_radius, 
                        border_bottom_right_radius=border_radius)
        surface.blit(shadow, (bevel_rect.x, bevel_rect.y + bevel_rect.height - size))
        
        shadow = pygame.Surface((size, bevel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, shadow_color, (0, 0, size, bevel_rect.height), 
                        border_top_right_radius=border_radius, 
                        border_bottom_right_radius=border_radius)
        surface.blit(shadow, (bevel_rect.x + bevel_rect.width - size, bevel_rect.y))
    
    def _draw_input_field(self, screen, label, value, y_pos, is_active, icon=None):
        """Draw modern 3D input fields with icons and hover effect"""
        field_rect = pygame.Rect(self.card_rect.x + 30, y_pos, 360, 50)
        
        # Field shadow for depth
        shadow_rect = field_rect.move(2, 3)
        pygame.draw.rect(screen, (0, 0, 0, 80), shadow_rect, border_radius=8)
        
        # Field background with hover effect
        color = self.active_input_color if is_active else self.input_color
        pygame.draw.rect(screen, color, field_rect, border_radius=8)
        
        # Inner bevel effect
        inner_rect = field_rect.inflate(-4, -4)
        self._draw_bevel(screen, inner_rect, 1, border_radius=4)
        
        # Left icon if provided
        if icon:
            icon_surf = self.input_font.render(icon, True, (180, 180, 220))
            screen.blit(icon_surf, (field_rect.x + 15, field_rect.y + 13))
        
        # Text input
        text_x = field_rect.x + (50 if icon else 20)
        text_color = self.text_color if value else (160, 160, 190)
        text_surf = self.input_font.render(value if value else label, True, text_color)
        
        # Text clipping and scrolling for long inputs
        if text_surf.get_width() > field_rect.width - (70 if icon else 40):
            offset = max(0, text_surf.get_width() - (field_rect.width - (70 if icon else 40)))
            screen.blit(text_surf, (text_x, field_rect.y + 13), 
                       (offset, 0, field_rect.width - (70 if icon else 40), text_surf.get_height()))
        else:
            screen.blit(text_surf, (text_x, field_rect.y + 13))
        
        # Cursor if active
        if is_active and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = text_x + (text_surf.get_width() if value else 0)
            pygame.draw.rect(screen, self.accent_color, (cursor_x, field_rect.y + 10, 2, 30))
        
        # Store reference
        if label == "Username":
            self.username_rect = field_rect
        else:
            self.password_rect = field_rect
    
    def _draw_button(self, screen, text, x, y, is_active, icon=None):
        """Draw attractive 3D buttons with optional icons"""
        button_width = 360
        button_height = 50
        button_rect = pygame.Rect(x, y, button_width, button_height)
        
        # Button shadow for depth
        shadow_rect = button_rect.move(3, 4)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=10)
        
        # Hover colors based on the mode
        if text == "Login":
            color = self.button_hover_color if is_active else self.button_color
        elif text == "Register":
            color = self.button_hover_color if is_active else self.button_color
        else:
            color = self.secondary_hover_color if is_active else self.secondary_button_color
        
        # Button base with gradient effect
        button_surface = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
        pygame.draw.rect(button_surface, color, (0, 0, button_width, button_height), border_radius=10)
        
        # Add gradient overlay
        if is_active:
            gradient = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
            pygame.draw.rect(gradient, (*self.accent_color, 30), (0, 0, button_width, button_height), border_radius=10)
            button_surface.blit(gradient, (0, 0))
        
        # Add bevel effect
        inner_rect = pygame.Rect(2, 2, button_width-4, button_height-4)
        self._draw_bevel(button_surface, inner_rect, 2, border_radius=8)
        
        screen.blit(button_surface, button_rect)
        
        # Button text with icon and shadow
        button_text = f"{icon}  {text}" if icon else text
        text_shadow = self.button_font.render(button_text, True, (0, 0, 0, 150))
        text_surf = self.button_font.render(button_text, True, self.text_color)
        
        text_pos = (
            x + button_width // 2 - text_surf.get_width() // 2, 
            y + button_height // 2 - text_surf.get_height() // 2
        )
        
        # Draw shadow first
        screen.blit(text_shadow, (text_pos[0]+1, text_pos[1]+1))
        screen.blit(text_surf, text_pos)
        
        # Store button references
        if text == "Login":
            self.login_rect = button_rect
        elif text == "Register":
            self.register_rect = button_rect
        elif text == "Capture Photo":
            self.capture_rect = button_rect
    
    def _draw_camera_preview(self, screen):
        """Draw the camera preview with stylish 3D frame"""
        # Frame shadow for depth
        shadow_rect = self.camera_rect.move(self.shadow_offset, self.shadow_offset)
        pygame.draw.rect(screen, (0, 0, 0, 150), shadow_rect.inflate(20, 20), border_radius=12)
        
        # Frame background with metallic look
        frame_rect = self.camera_rect.inflate(20, 20)
        frame_surface = pygame.Surface((frame_rect.width, frame_rect.height), pygame.SRCALPHA)
        
        # Metallic gradient
        for i in range(frame_rect.height):
            alpha = 100 + int(155 * (i / frame_rect.height))
            pygame.draw.line(frame_surface, (40, 50, 70, alpha), (0, i), (frame_rect.width, i))
        
        pygame.draw.rect(frame_surface, (0, 0, 0, 200), (0, 0, frame_rect.width, frame_rect.height), 2, border_radius=12)
        screen.blit(frame_surface, frame_rect)
        
        # Inner frame with bevel
        inner_frame = self.camera_rect.inflate(18, 18)
        pygame.draw.rect(screen, (20, 30, 40), inner_frame, border_radius=10)
        self._draw_bevel(screen, inner_frame, 3, border_radius=10)
        
        # Camera preview or placeholder
        if self.camera_preview:
            # Apply rounded corners with alpha mask
            mask = pygame.Surface(self.camera_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, *self.camera_rect.size), border_radius=8)
            self.camera_preview.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Add reflection effect
            reflection = pygame.Surface(self.camera_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(reflection, (255, 255, 255, 80), 
                           (0, 0, self.camera_rect.width, self.camera_rect.height//3), 
                           border_top_left_radius=8, border_top_right_radius=8)
            self.camera_preview.blit(reflection, (0, 0))
            
            screen.blit(self.camera_preview, self.camera_rect)
        else:
            # Stylish 3D placeholder
            placeholder = pygame.Surface(self.camera_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(placeholder, (25, 35, 50), (0, 0, *self.camera_rect.size), border_radius=8)
            
            # Add scanline effect
            for i in range(0, self.camera_rect.height, 2):
                pygame.draw.line(placeholder, (0, 0, 0, 30), (0, i), (self.camera_rect.width, i))
            
            no_cam_icon = self.button_font.render("📷", True, (100, 120, 150))
            no_cam_text = self.input_font.render("Camera Preview", True, (120, 140, 170))
            
            placeholder.blit(no_cam_icon, 
                           (self.camera_rect.width // 2 - no_cam_icon.get_width() // 2,
                            self.camera_rect.height // 2 - 30))
            placeholder.blit(no_cam_text, 
                           (self.camera_rect.width // 2 - no_cam_text.get_width() // 2,
                            self.camera_rect.height // 2 + 10))
            
            screen.blit(placeholder, self.camera_rect)
        
        # Decorative corner accents with 3D effect
        corner_size = 20
        for dx, dy in [(0, 0), (1, 0), (0, 1), (1, 1)]:
            corner_rect = pygame.Rect(
                self.camera_rect.x - 10 + dx * (self.camera_rect.width + 20 - corner_size),
                self.camera_rect.y - 10 + dy * (self.camera_rect.height + 20 - corner_size),
                corner_size, corner_size
            )
            
            # Corner shadow
            pygame.draw.rect(screen, (0, 0, 0, 100), corner_rect.move(1, 1), border_radius=4)
            
            # Corner with gradient
            corner_surface = pygame.Surface((corner_size, corner_size), pygame.SRCALPHA)
            for i in range(corner_size):
                alpha = 200 - int(150 * (i / corner_size))
                pygame.draw.line(corner_surface, (*self.accent_color, alpha), (0, i), (corner_size, i))
            
            pygame.draw.rect(corner_surface, (255, 255, 255, 30), (0, 0, corner_size, corner_size), 1, border_radius=4)
            screen.blit(corner_surface, corner_rect)
    
    def _draw_message(self, screen):
        """Draw animated message box"""
        msg_icon = "⚠" if "error" in self.message.lower() else "ℹ"
        
        # Create pulsing effect
        pulse = 1 + 0.1 * abs(pygame.time.get_ticks() % 1000 - 500) / 500
        
        # Background with animation
        msg_surf = self.input_font.render(f"{msg_icon}  {self.message}", True, self.message_color)
        msg_rect = pygame.Rect(self.card_rect.x + 30, 520, msg_surf.get_width() + 20, msg_surf.get_height() + 10)
        
        # Animated background
        msg_bg = pygame.Surface((msg_rect.width, msg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(msg_bg, (*self.message_color, 20 * pulse), 
                        (0, 0, msg_rect.width, msg_rect.height), 
                        border_radius=6)
        pygame.draw.rect(msg_bg, (*self.message_color, 80), 
                        (0, 0, msg_rect.width, msg_rect.height), 
                        1, border_radius=6)
        
        screen.blit(msg_bg, msg_rect)
        screen.blit(msg_surf, (msg_rect.x + 10, msg_rect.y + 5))
    
    def update_camera_preview(self, frame):
        """Update the camera preview with a new frame"""
        if frame is not None:
            # Convert OpenCV frame to pygame surface
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            self.camera_preview = pygame.transform.scale(frame, (self.camera_rect.width, self.camera_rect.height))
            
            # Apply rounded corners and reflection
            mask = pygame.Surface(self.camera_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, *self.camera_rect.size), border_radius=8)
            self.camera_preview.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)