import pygame
import random
import sys
import textwrap

class PixelButton:
    def __init__(self, x, y, width, height, text, font, 
                 normal_color=(200, 200, 200), 
                 hover_color=(220, 220, 220), 
                 text_color=(0, 0, 0),
                 border_color=(100, 100, 100)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.normal_color = normal_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.selected_color = (50, 200, 50)  # More subtle green
        self.is_selected = False
        self.is_hover = False

    def draw(self, surface):
        # Determine current color
        if self.is_selected:
            current_color = self.selected_color
        elif self.is_hover:
            current_color = self.hover_color
        else:
            current_color = self.normal_color

        # Draw button with pixelated look
        pygame.draw.rect(surface, current_color, self.rect, border_radius=2)
        pygame.draw.rect(surface, self.border_color, self.rect, 2, border_radius=2)

        # Render text with pixelated effect
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

class CarbonChaseGame:
    def __init__(self):
        pygame.init()
        self.screen_width = 1024
        self.screen_height = 768  # Increased height for better layout
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Carbon Chase - Sustainable Production Simulator")
        
        # Load assets
        self.load_assets()
        
        # Game constants
        self.MAX_EMISSION_THRESHOLD = 1000
        self.WARNING_EMISSION_THRESHOLD = 700
        self.MIN_HAPPINESS_THRESHOLD = 50
        
        # Budget tiers
        self.budget_levels = ["Low Budget", "Medium Budget", "High Budget"]
        self.budget_values = {
            "Low Budget": 5000, 
            "Medium Budget": 10000, 
            "High Budget": 20000
        }
        
        # Game state
        self.processes = self.load_processes()
        self.reset_game()
        
        # UI elements
        self.create_ui_elements()

    def load_assets(self):
        """Load fonts and other assets with fallbacks"""
        try:
            # Try to load a pixel font
            self.pixel_font_small = pygame.font.Font("assets/PressStart2P.ttf", 14)
            self.pixel_font_medium = pygame.font.Font("assets/PressStart2P.ttf", 18)
            self.pixel_font_large = pygame.font.Font("assets/PressStart2P.ttf", 24)
        except:
            # Fallback to default fonts
            self.pixel_font_small = pygame.font.SysFont('courier', 14, bold=True)
            self.pixel_font_medium = pygame.font.SysFont('courier', 18, bold=True)
            self.pixel_font_large = pygame.font.SysFont('courier', 24, bold=True)
        
        # Color palette
        self.COLORS = {
            'background': (230, 230, 230),
            'panel': (200, 200, 200),
            'dark_panel': (150, 150, 150),
            'border': (80, 80, 80),
            'text': (20, 20, 20),
            'warning': (200, 100, 0),
            'danger': (200, 50, 50),
            'success': (50, 150, 50),
            'highlight': (100, 180, 255),
            'button': (180, 180, 180),
            'button_hover': (200, 200, 200),
            'button_selected': (80, 180, 80)
        }

    def load_processes(self):
        """Load all production processes with their options"""
        return {
            "Pizza": {
                "Ingredient Sourcing": {
                    "Conventional": {"cost": 2000, "emissions": 1800, "efficiency": 2, "happiness": 2, 
                                    "info": "Conventional agriculture emits high CO2 and methane from fertilizer and livestock."},
                    "Organic": {"cost": 3000, "emissions": 900, "efficiency": 3, "happiness": 3, 
                              "info": "Organic farming reduces chemical use, but still emits from land use."},
                    "Local Seasonal": {"cost": 2500, "emissions": 500, "efficiency": 4, "happiness": 4, 
                                     "info": "Local sourcing reduces transport emissions significantly."},
                    "Plant Based": {"cost": 2800, "emissions": 600, "efficiency": 4, "happiness": 3, 
                                  "info": "Plant-based alternatives cut methane emissions but have processing costs."}
                },
                "Dough Preparation": {
                    "Mass Produced": {"cost": 1500, "emissions": 800, "efficiency": 3, "happiness": 2, 
                                    "info": "Factory-produced dough increases emissions but is cheaper."},
                    "Handmade": {"cost": 2500, "emissions": 400, "efficiency": 4, "happiness": 4, 
                               "info": "Handmade dough requires more labor but lowers emissions."}
                },
                "Baking": {
                    "Gas Oven": {"cost": 1500, "emissions": 2500, "efficiency": 3, "happiness": 3, 
                                "info": "Gas ovens burn fossil fuels, releasing CO2."},
                    "Wood Fired": {"cost": 2000, "emissions": 1500, "efficiency": 4, "happiness": 4, 
                                  "info": "Wood-fired ovens emit CO2 but can be sustainable if sourced correctly."},
                    "Solar": {"cost": 3500, "emissions": 100, "efficiency": 5, "happiness": 3, 
                             "info": "Solar ovens have near-zero emissions."}
                },
                "Packaging": {
                    "Plastic": {"cost": 1000, "emissions": 1800, "efficiency": 5, "happiness": 2, 
                               "info": "Plastic packaging is cheap but has high emissions and waste."},
                    "Biodegradable": {"cost": 2000, "emissions": 800, "efficiency": 4, "happiness": 4, 
                                    "info": "Biodegradable packaging is more sustainable but costly."}
                }
            },
            "E-Bike": {
                "Battery Production": {
                    "Lithium Mining": {"cost": 5000, "emissions": 8500, "efficiency": 5, "happiness": 3, 
                                      "info": "Lithium mining has high emissions due to extraction and refining."},
                    "Recycled Batteries": {"cost": 4500, "emissions": 3500, "efficiency": 4, "happiness": 4, 
                                         "info": "Battery recycling reduces mining needs but requires energy-intensive processing."}
                },
                "Frame Production": {
                    "Aluminum": {"cost": 4000, "emissions": 6000, "efficiency": 4, "happiness": 3, 
                               "info": "Aluminum frames are lightweight but require high energy to produce."},
                    "Carbon Fiber": {"cost": 7000, "emissions": 3000, "efficiency": 5, "happiness": 5, 
                                   "info": "Carbon fiber reduces weight but is expensive and energy-intensive."}
                },
                "Assembly": {
                    "Manual": {"cost": 3500, "emissions": 2000, "efficiency": 4, "happiness": 4, 
                              "info": "Manual assembly ensures quality but has higher labor costs."},
                    "Automated": {"cost": 6000, "emissions": 1000, "efficiency": 5, "happiness": 3, 
                                 "info": "Automated assembly is more efficient but requires high upfront costs."}
                }
            },
            "Smartphone": {
                "Component Production": {
                    "Outsource": {"cost": 4000, "emissions": 5000, "efficiency": 4, "happiness": 3, 
                                 "info": "Outsourced production relies on high-emission supply chains."},
                    "In-House": {"cost": 6000, "emissions": 2500, "efficiency": 5, "happiness": 4, 
                                "info": "In-house production has better emission control but is expensive."}
                },
                "Distribution": {
                    "Air Freight": {"cost": 5000, "emissions": 7000, "efficiency": 5, "happiness": 4, 
                                   "info": "Air freight is the fastest but has the highest emissions."},
                    "Sea Freight": {"cost": 3500, "emissions": 4000, "efficiency": 4, "happiness": 3, 
                                  "info": "Sea freight is slower but has lower emissions than air transport."}
                }
            },
            "Sweater": {
                "Fabric Production": {
                    "Synthetic": {"cost": 2000, "emissions": 3500, "efficiency": 3, "happiness": 3, 
                                "info": "Synthetic fabrics rely on petroleum-based materials, increasing emissions."},
                    "Organic Cotton": {"cost": 3500, "emissions": 1500, "efficiency": 4, "happiness": 4, 
                                     "info": "Organic cotton reduces emissions but requires significant land use."},
                    "Recycled Wool": {"cost": 3000, "emissions": 800, "efficiency": 5, "happiness": 5, 
                                    "info": "Recycled wool minimizes new production emissions significantly."}
                },
                "Dyeing": {
                    "Chemical Dyes": {"cost": 2500, "emissions": 2500, "efficiency": 3, "happiness": 3, 
                                    "info": "Chemical dyes pollute water and increase emissions."},
                    "Plant-Based Dyes": {"cost": 4000, "emissions": 1000, "efficiency": 4, "happiness": 4, 
                                       "info": "Plant-based dyes are more sustainable but costlier."}
                }
            },
            "Toilet Paper": {
                "Material": {
                    "Virgin Paper": {"cost": 1500, "emissions": 3000, "efficiency": 4, "happiness": 4, 
                                    "info": "Virgin paper requires new trees and high energy for processing."},
                    "Recycled Paper": {"cost": 2000, "emissions": 1000, "efficiency": 3, "happiness": 3, 
                                     "info": "Recycled paper reduces tree harvesting but may be less soft."},
                    "Bamboo": {"cost": 2500, "emissions": 800, "efficiency": 4, "happiness": 4, 
                              "info": "Bamboo grows quickly and absorbs more CO2 than trees."}
                },
                "Packaging": {
                    "Plastic Wrap": {"cost": 1000, "emissions": 1500, "efficiency": 4, "happiness": 3, 
                                    "info": "Plastic wrap is waterproof but creates non-biodegradable waste."},
                    "Paper Wrap": {"cost": 1500, "emissions": 500, "efficiency": 3, "happiness": 4, 
                                  "info": "Paper wrap is biodegradable but less moisture-resistant."}
                }
            }
        }

    def create_ui_elements(self):
        """Create all UI buttons and elements"""
        # Product tabs
        self.product_buttons = []
        products = list(self.processes.keys())
        tab_width = (self.screen_width - 20) // len(products)
        
        for i, product in enumerate(products):
            button = PixelButton(
                10 + i * tab_width, 
                120, 
                tab_width, 
                40, 
                product, 
                self.pixel_font_medium,
                normal_color=self.COLORS['button'],
                hover_color=self.COLORS['button_hover'],
                border_color=self.COLORS['border']
            )
            self.product_buttons.append(button)
        
        # Create initial process buttons
        self.create_process_buttons()
        
        # Reset button
        self.reset_button = PixelButton(
            self.screen_width - 150, 80, 
            140, 30, 
            "Reset Game", 
            self.pixel_font_small,
            normal_color=self.COLORS['button'],
            hover_color=self.COLORS['button_hover'],
            border_color=self.COLORS['border']
        )

    def create_process_buttons(self):
        """Create buttons for the current product's processes"""
        self.process_buttons = []
        y_offset = 180
        
        for process, options in self.processes[self.current_product].items():
            # Process title
            title_button = PixelButton(
                10, y_offset, 
                self.screen_width - 20, 30, 
                process, 
                self.pixel_font_medium, 
                normal_color=self.COLORS['dark_panel'],
                text_color=self.COLORS['text'],
                border_color=self.COLORS['border']
            )
            self.process_buttons.append(title_button)
            y_offset += 40

            # Option buttons
            option_width = (self.screen_width - 40) // len(options)
            for i, (option, details) in enumerate(options.items()):
                button_text = f"{option}\n${details['cost']} | Em: {details['emissions']}"
                button = PixelButton(
                    20 + i * option_width, y_offset, 
                    option_width - 10, 60, 
                    button_text, 
                    self.pixel_font_small,
                    normal_color=self.COLORS['button'],
                    hover_color=self.COLORS['button_hover'],
                    text_color=self.COLORS['text'],
                    border_color=self.COLORS['border']
                )
                
                # Check if this option is already selected
                if self.player_choices[self.current_product].get(process) == option:
                    button.is_selected = True
                
                self.process_buttons.append(button)
            
            y_offset += 70

    def reset_game(self):
        """Reset all game state variables"""
        # Initialize game variables
        self.budget = 0
        self.current_emissions = 0
        self.current_happiness = 0
        self.emission_warnings = 0
        self.game_state = "playing"
        
        # Player choices
        self.player_choices = {product: {} for product in self.processes.keys()}
        
        # Initialize player choices for all products and processes
        for product, processes in self.processes.items():
            for process in processes.keys():
                self.player_choices[product][process] = ""
        
        # Random budget selection
        current_budget_tier = random.choice(self.budget_levels)
        self.budget = self.budget_values[current_budget_tier]
        
        # Set current product
        self.current_product = "Pizza"
        
        # Info message
        self.info_message = f"Welcome to Carbon Chase! {current_budget_tier} of ${self.budget}. Select production methods that balance cost, emissions, and customer happiness."

    def select_process_option(self, product, process, option):
        """Select a production option for a process"""
        option_data = self.processes[product][process][option]
        
        # Check budget
        if option_data["cost"] > self.budget:
            self.info_message = f"Not enough budget for {option}! You need ${option_data['cost']} but only have ${self.budget}."
            return False
        
        # Refund previous option if exists
        if self.player_choices[product].get(process):
            previous_option = self.player_choices[product][process]
            previous_data = self.processes[product][process][previous_option]
            self.budget += previous_data["cost"]
            self.current_emissions -= previous_data["emissions"]
            self.current_happiness -= previous_data["happiness"]
        
        # Apply new option
        self.player_choices[product][process] = option
        self.budget -= option_data["cost"]
        self.current_emissions += option_data["emissions"]
        self.current_happiness += option_data["happiness"]
        
        # Update info message
        self.info_message = option_data["info"]
        
        # Recalculate happiness
        self.calculate_happiness()
        
        # Check game conditions
        self.check_game_conditions()
        
        return True

    def calculate_happiness(self):
        """Calculate overall happiness score based on selected options"""
        total_processes = 0
        filled_processes = 0
        total_happiness = 0
        
        for product in self.processes:
            for process in self.processes[product]:
                total_processes += 1
                if self.player_choices[product].get(process):
                    filled_processes += 1
                    option = self.player_choices[product][process]
                    total_happiness += self.processes[product][process][option]["happiness"]
        
        max_possible_happiness = 5 * total_processes
        self.current_happiness = int((total_happiness / max_possible_happiness) * 100) if max_possible_happiness > 0 else 0

    def check_game_conditions(self):
        """Check if game over conditions are met"""
        # Check emissions
        if self.current_emissions > self.MAX_EMISSION_THRESHOLD:
            self.game_over("Game Over: Excessive Emissions! Your production emits too much CO2.")
            return
        
        # Check happiness
        if self.current_happiness < self.MIN_HAPPINESS_THRESHOLD:
            self.game_over("Game Over: Unhappy Customers! Your product doesn't meet quality expectations.")
            return
        
        # Check budget
        if self.budget < 0:
            self.game_over("Game Over: Bankrupt! You've exceeded your budget.")
            return
        
        # Check if all processes are filled
        all_filled = True
        for product in self.processes:
            for process in self.processes[product]:
                if not self.player_choices[product].get(process):
                    all_filled = False
                    break
            if not all_filled:
                break
        
        if all_filled:
            if self.current_emissions < self.MAX_EMISSION_THRESHOLD // 2:
                self.game_over("Congratulations! You created a sustainable product with low emissions!")
            else:
                self.game_over("Product Complete! You've finished production, but could reduce emissions further.")

    def game_over(self, message):
        """Handle game over state"""
        self.game_state = "game_over"
        self.info_message = message

    def draw_background(self):
        """Draw the game background"""
        self.screen.fill(self.COLORS['background'])
        
        # Add subtle grid pattern for pixel effect
        for x in range(0, self.screen_width, 20):
            pygame.draw.line(self.screen, (220, 220, 220), (x, 0), (x, self.screen_height), 1)
        for y in range(0, self.screen_height, 20):
            pygame.draw.line(self.screen, (220, 220, 220), (0, y), (self.screen_width, y), 1)

    def draw_header_panel(self):
        """Draw the header panel with game stats"""
        pygame.draw.rect(self.screen, self.COLORS['panel'], (10, 10, self.screen_width - 20, 100), border_radius=5)
        pygame.draw.rect(self.screen, self.COLORS['border'], (10, 10, self.screen_width - 20, 100), 2, border_radius=5)
        
        # Title
        title_text = self.pixel_font_large.render("CARBON CHASE", True, self.COLORS['text'])
        self.screen.blit(title_text, (20, 15))
        
        # Budget
        budget_color = self.COLORS['danger'] if self.budget < 1000 else self.COLORS['text']
        budget_text = self.pixel_font_medium.render(f"Budget: ${self.budget}", True, budget_color)
        self.screen.blit(budget_text, (20, 50))
        
        # Emissions
        emissions_color = self.COLORS['danger'] if self.current_emissions > self.WARNING_EMISSION_THRESHOLD else self.COLORS['text']
        emissions_text = self.pixel_font_medium.render(f"Emissions: {self.current_emissions} CO2", True, emissions_color)
        self.screen.blit(emissions_text, (300, 50))
        
        # Happiness
        happiness_color = self.COLORS['danger'] if self.current_happiness < self.MIN_HAPPINESS_THRESHOLD else self.COLORS['success']
        happiness_text = self.pixel_font_medium.render(f"Happiness: {self.current_happiness}%", True, happiness_color)
        self.screen.blit(happiness_text, (600, 50))
        
        # Current product
        product_text = self.pixel_font_medium.render(f"Product: {self.current_product}", True, self.COLORS['text'])
        self.screen.blit(product_text, (20, 80))

    def draw_info_panel(self):
        """Draw the information panel at the bottom"""
        pygame.draw.rect(self.screen, self.COLORS['panel'], (10, self.screen_height - 140, self.screen_width - 20, 130), border_radius=5)
        pygame.draw.rect(self.screen, self.COLORS['border'], (10, self.screen_height - 140, self.screen_width - 20, 130), 2, border_radius=5)
        
        # Info title
        title_text = self.pixel_font_medium.render("INFORMATION:", True, self.COLORS['text'])
        self.screen.blit(title_text, (20, self.screen_height - 130))
        
        # Render info message with word wrap
        wrapped_text = textwrap.wrap(self.info_message, width=80)
        for i, line in enumerate(wrapped_text[:4]):  # Limit to 4 lines
            text = self.pixel_font_small.render(line, True, self.COLORS['text'])
            self.screen.blit(text, (20, self.screen_height - 100 + i * 25))

    def draw_game_over(self):
        """Draw game over overlay"""
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # Game over message
        game_over_text = self.pixel_font_large.render("GAME OVER", True, (255, 100, 100))
        text_rect = game_over_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 50))
        self.screen.blit(game_over_text, text_rect)
        
        # Result message
        result_lines = textwrap.wrap(self.info_message, width=40)
        for i, line in enumerate(result_lines):
            result_text = self.pixel_font_medium.render(line, True, (255, 255, 255))
            result_rect = result_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + i * 30))
            self.screen.blit(result_text, result_rect)
        
        # Restart button
        restart_button = PixelButton(
            self.screen_width//2 - 100, self.screen_height//2 + 100, 
            200, 50, 
            "Play Again", 
            self.pixel_font_medium,
            normal_color=(100, 200, 100),
            hover_color=(120, 220, 120),
            text_color=(255, 255, 255)
        )
        restart_button.draw(self.screen)
        
        # Check for restart click
        mouse_pos = pygame.mouse.get_pos()
        restart_button.is_hover = restart_button.rect.collidepoint(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and restart_button.rect.collidepoint(event.pos):
                self.reset_game()
                return True
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        return False

    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        running = True

        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.game_state == "playing":
                    # Product tab selection
                    for button in self.product_buttons:
                        if button.handle_event(event):
                            self.current_product = button.text
                            self.create_process_buttons()
                    
                    # Process option selection
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        for i, button in enumerate(self.process_buttons):
                            if button.handle_event(event):
                                # Skip title buttons
                                if i % (len(self.processes[self.current_product]) + 1) == 0:
                                    continue
                                
                                # Find which process this option belongs to
                                process_index = (i - 1) // (len(self.processes[self.current_product]) + 1)
                                process = list(self.processes[self.current_product].keys())[process_index]
                                option = button.text.split('\n')[0]
                                
                                # Select the process option
                                self.select_process_option(self.current_product, process, option)
                                self.create_process_buttons()
                    
                    # Reset button
                    if self.reset_button.handle_event(event):
                        self.reset_game()
                
            # Draw everything
            self.draw_background()
            self.draw_header_panel()
            
            # Draw product tabs
            for button in self.product_buttons:
                button.draw(self.screen)
            
            # Draw process buttons if in playing state
            if self.game_state == "playing":
                for button in self.process_buttons:
                    button.draw(self.screen)
                
                # Draw reset button
                self.reset_button.draw(self.screen)
            
            self.draw_info_panel()
            
            # Draw game over screen if needed
            if self.game_state == "game_over":
                if self.draw_game_over():
                    continue  # Game was restarted
            
            # Update display
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()

def main():
    game = CarbonChaseGame()
    game.run()

if __name__ == "__main__":
    main()