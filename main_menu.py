import pygame
import sys
from carbchase import CarbonChaseGame

class MainMenu:
    def __init__(self):
        pygame.init()
        self.screen_width = 1024
        self.screen_height = 768
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Carbon Chase - Main Menu")
        
        # Load assets
        self.load_assets()
        
        # Color palette (matching the game)
        self.COLORS = {
            'background': (230, 230, 230),
            'panel': (200, 200, 200),
            'border': (80, 80, 80),
            'text': (20, 20, 20),
            'button': (180, 180, 180),
            'button_hover': (200, 200, 200),
        }

        self.load_assets()
    

    def load_assets(self):
        """Load images and scale them down"""
        # Calculate scaling factors
        original_width, original_height = 1920, 1080
        scale_factor_width = self.screen_width / original_width
        scale_factor_height = self.screen_height / original_height

        # Load and scale background image
        original_background = pygame.image.load("assets/background.png")
        self.background_img = pygame.transform.scale(original_background, (self.screen_width, self.screen_height))

        # Load and scale title image
        original_title = pygame.image.load("assets/title.png")
        title_width = int(original_title.get_width() * scale_factor_width)
        title_height = int(original_title.get_height() * scale_factor_height)
        self.title_img = pygame.transform.scale(original_title, (title_width, title_height))

        # Load and scale play button image
        self.play_button_img = pygame.image.load("assets/play_button.png")
        button_width = 530  # Measured width of scaled button
        button_height = 154  # Measured height of scaled button
        self.play_button_img = pygame.transform.scale(self.play_button_img, (button_width, button_height))

        # Calculate centered position for the button
        self.button_x = (self.screen_width - button_width) // 2
        self.button_y = (self.screen_height - button_height) // 2 + 200  # Adjusted vertical position (+200 instead of +150)

        # Create rect for play button at the EXACT same position as the image
        self.play_button = pygame.Rect(self.button_x, self.button_y, button_width, button_height)

    def draw(self):
        """Draw the main menu"""
        # Draw background
        self.screen.blit(self.background_img, (0, 0))
        
        # Draw title
        title_rect = self.title_img.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
        self.screen.blit(self.title_img, title_rect)
        
        # Draw play button at the SAME position as its rect
        self.screen.blit(self.play_button_img, (self.button_x, self.button_y))

        # Debug: Draw the clickable area rectangle to verify alignment
        pygame.draw.rect(self.screen, (255, 0, 0), self.play_button, 2)  # Red outline with a width of 2 pixels





    
    def run(self):
        """Main menu loop"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Check for button click
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.play_button.collidepoint(event.pos):
                        # Start the game
                        game = CarbonChaseGame()
                        game.run()
                        # When game exits, return to menu
                        pygame.display.set_caption("Carbon Chase - Main Menu")
            
            # Draw the menu
            self.draw()
            
            pygame.display.flip()
            clock.tick(60)
    


def main():
    while(1):
        menu = MainMenu()
        menu.run()

if __name__ == "__main__":
    main()
