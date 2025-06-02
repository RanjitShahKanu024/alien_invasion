import pygame
from pygame.sprite import Group
from pygame.locals import *
import cv2
import sys
import time
import os

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
import game_functions as gf
from hand_control import HandController
from player_auth import PlayerAuth
from auth_ui import AuthUI

def run_game():
    # Initialize pygame and authentication
    pygame.init()
    auth = PlayerAuth()
    auth_ui = AuthUI()
    
    # Show authentication screen
    auth_screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption(auth_ui.title)
    
    authenticated = False
    current_player = None
    registration_mode = False
    last_capture_time = 0
    capture_cooldown = 1
    
    # Authentication loop
    clock = pygame.time.Clock()
    while not authenticated:
        preview_frame = auth.get_camera_frame(mirror=True)
        if preview_frame is not None:
            auth_ui.update_camera_preview(preview_frame)
        
        auth_ui.create_auth_ui(auth_screen, registration_mode)
        pygame.display.flip()
        
        current_time = time.time()
        events = pygame.event.get()
        
        for event in events:
            if event.type == QUIT:
                auth.release_camera()
                pygame.quit()
                sys.exit()
                
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    auth.release_camera()
                    pygame.quit()
                    sys.exit()
                    
                # Handle text input
                if auth_ui.active_input == "username":
                    if event.key == K_BACKSPACE:
                        auth_ui.username = auth_ui.username[:-1]
                    elif event.unicode.isalnum() and len(auth_ui.username) < 15:
                        auth_ui.username += event.unicode
                elif auth_ui.active_input == "password":
                    if event.key == K_BACKSPACE:
                        auth_ui.password = auth_ui.password[:-1]
                    elif event.unicode.isprintable() and len(auth_ui.password) < 20:
                        auth_ui.password += event.unicode
                        
                elif event.key == K_RETURN and current_time - last_capture_time > capture_cooldown:
                    last_capture_time = current_time
                    auth_ui.message = "Capturing photo..."
                    auth_ui.message_color = (255, 255, 0)
                    pygame.display.flip()
                    
                    photo = auth.capture_photo()
                    if photo is not None:
                        cv2.imshow("Verification Photo", photo)
                        cv2.waitKey(1)
                        
                        success = False
                        if registration_mode:
                            success = auth.register_player(auth_ui.username, auth_ui.password, photo)
                            auth_ui.message = "Registration successful!" if success else "Username exists or no face detected!"
                        else:
                            success = auth.verify_player(auth_ui.username, auth_ui.password, photo)
                            auth_ui.message = "Login successful!" if success else "Invalid credentials or face mismatch!"
                        
                        auth_ui.message_color = (0, 255, 0) if success else (255, 0, 0)
                        
                        if success:
                            pygame.display.flip()
                            time.sleep(1)
                            authenticated = True
                            current_player = auth_ui.username
                            cv2.destroyWindow("Verification Photo")
            
            if event.type == MOUSEBUTTONDOWN and current_time - last_capture_time > capture_cooldown:
                mouse_pos = pygame.mouse.get_pos()
                
                if auth_ui.username_rect.collidepoint(mouse_pos):
                    auth_ui.active_input = "username"
                    auth_ui.message = ""
                elif auth_ui.password_rect.collidepoint(mouse_pos):
                    auth_ui.active_input = "password"
                    auth_ui.message = ""
                elif auth_ui.login_rect.collidepoint(mouse_pos):
                    registration_mode = False
                    auth_ui.message = ""
                elif auth_ui.register_rect.collidepoint(mouse_pos):
                    registration_mode = True
                    auth_ui.message = ""
                elif auth_ui.capture_rect.collidepoint(mouse_pos):
                    last_capture_time = current_time
                    auth_ui.message = "Capturing photo..."
                    auth_ui.message_color = (255, 255, 0)
                    pygame.display.flip()
                    
                    photo = auth.capture_photo()
                    if photo is not None:
                        cv2.imshow("Verification Photo", photo)
                        cv2.waitKey(1)
                        
                        success = False
                        if registration_mode:
                            success = auth.register_player(auth_ui.username, auth_ui.password, photo)
                            auth_ui.message = "Registration successful!" if success else "Username exists or no face detected!"
                        else:
                            success = auth.verify_player(auth_ui.username, auth_ui.password, photo)
                            auth_ui.message = "Login successful!" if success else "Invalid credentials or face mismatch!"
                        
                        auth_ui.message_color = (0, 255, 0) if success else (255, 0, 0)
                        
                        if success:
                            pygame.display.flip()
                            time.sleep(1)
                            authenticated = True
                            current_player = auth_ui.username
                            cv2.destroyWindow("Verification Photo")
        
        clock.tick(30)
    
    # Initialize game after authentication
    ai_settings = Settings()
    screen = pygame.display.set_mode((ai_settings.screen_width, ai_settings.screen_height))
    pygame.display.set_caption(f"Alien Invasion - Player: {current_player}")
    
    # Initialize game components
    hand_controller = HandController()
    play_button = Button(ai_settings, screen, "Play")
    stats = GameStats(ai_settings)
    stats.player_name = current_player
    
    # Load player data
    player_data = auth.get_player_data(current_player)
    if player_data and 'high_score' in player_data:
        stats.high_score = player_data['high_score']
    
    sb = Scoreboard(ai_settings, screen, stats)
    ship = Ship(ai_settings, screen)
    bullets = Group()
    aliens = Group()
    gf.create_fleet(ai_settings, screen, ship, aliens)

    # Main game loop
    running = True
    while running:
        # Get hand landmarks
        hand_landmarks, camera_frame = hand_controller.get_hand_landmarks()
        
        # Show camera feed
        if camera_frame is not None:
            cv2.imshow('Hand Controls', camera_frame)
            cv2.waitKey(1)
        
        # Handle gestures and events
        gf.check_hand_gesture(hand_landmarks, ai_settings, screen, ship, bullets, hand_controller)
        
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
        
        # Pass events to game functions
        gf.check_events(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets, events)
        
        if stats.game_active:
            ship.update()
            gf.update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets)
            gf.update_aliens(ai_settings, screen, stats, sb, ship, aliens, bullets)
            
            # Update high score
            if stats.score > stats.high_score:
                stats.high_score = stats.score
                if auth.update_high_score(current_player, stats.score):
                    sb.prep_high_score()
        
        gf.update_screen(ai_settings, screen, stats, sb, ship, aliens, bullets, play_button)

    # Cleanup
    hand_controller.release()
    cv2.destroyAllWindows()
    auth.release_camera()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_game()