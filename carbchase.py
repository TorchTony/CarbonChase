import pygame
import random
import sys
import textwrap
import traceback
from math import ceil

class PixelButton:
    def __init__(self, x, y, width, height, text, font, 
                 normal_color=(180, 210, 180),  # Light green
                 hover_color=(200, 230, 200),    # Lighter green
                 text_color=(20, 40, 20),        # Very dark green
                 border_color=(50, 100, 50)):    # Dark green
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.normal_color = normal_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.selected_color = (80, 180, 80)      # Bright green
        self.is_selected = False
        self.is_hover = False

    def draw(self, surface):
        try:
            current_color = self.selected_color if self.is_selected else self.hover_color if self.is_hover else self.normal_color
            pygame.draw.rect(surface, current_color, self.rect, border_radius=2)
            pygame.draw.rect(surface, self.border_color, self.rect, 2, border_radius=2)
            
            # Split text into lines
            lines = self.text.split('\n')
            total_height = len(lines) * self.font.get_height()
            y_offset = (self.rect.height - total_height) // 2
            
            for i, line in enumerate(lines):
                text_surface = self.font.render(line, True, self.text_color)
                text_rect = text_surface.get_rect(
                    centerx=self.rect.centerx,
                    top=self.rect.top + y_offset + i * self.font.get_height()
                )
                surface.blit(text_surface, text_rect)
        except:
            pass

    def handle_event(self, event):
        try:
            if event.type == pygame.MOUSEMOTION:
                self.is_hover = self.rect.collidepoint(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return self.rect.collidepoint(event.pos)
            return False
        except:
            return False

class CarbonChaseGame:
    def __init__(self):
        try:
            pygame.init()
            self.screen_width = 1024
            self.screen_height = 768
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            pygame.display.set_caption("Carbon Chase - Sustainable Production Simulator")
            
            self.load_assets()
            
            # Game constants - Adjusted thresholds to make game more winnable
            self.BASE_EMISSION_THRESHOLD = 5000  # Base value that gets scaled with budget
            self.SEVERE_EMISSION_WARNING_RATIO = 0.7  # 70% of max emissions
            self.WARNING_EMISSION_RATIO = 0.5  # 50% of max emissions
            self.MIN_HAPPINESS_THRESHOLD = 40  # Minimum happiness percentage
            
            # Dynamic budget system - generates random budgets within ranges
            self.budget_levels = ["Struggling Startup", "Small Business", "Growing Company", 
                                "Established Firm", "Corporate Giant"]
            self.budget_ranges = {
                "Struggling Startup": (3000, 6000),
                "Small Business": (5000, 9000),
                "Growing Company": (8000, 15000),
                "Established Firm": (12000, 20000),
                "Corporate Giant": (18000, 30000)
            }
            
            # Game state
            self.processes = self.load_processes()
            self.emission_warnings = 0
            self.reset_game()
            
            # UI elements
            self.create_ui_elements()
            self.error_occurred = False
        except:
            self.handle_critical_error()

    def calculate_dynamic_thresholds(self):
        """Calculate thresholds based on current budget"""
        # Emission thresholds scale with budget (higher budget = higher allowed emissions)
        budget_factor = self.budget / 10000  # Normalize around 10k budget
        self.MAX_EMISSION_THRESHOLD = ceil(self.BASE_EMISSION_THRESHOLD * budget_factor * 1.2)
        self.SEVERE_EMISSION_THRESHOLD = ceil(self.MAX_EMISSION_THRESHOLD * self.SEVERE_EMISSION_WARNING_RATIO)
        self.WARNING_EMISSION_THRESHOLD = ceil(self.MAX_EMISSION_THRESHOLD * self.WARNING_EMISSION_RATIO)

    def handle_critical_error(self, message="A critical error occurred"):
        """Show error message and reset game"""
        try:
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220))
            self.screen.blit(overlay, (0, 0))
            
            error_text = self.pixel_font_medium.render("ERROR", True, (255, 50, 50))
            error_rect = error_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 50))
            self.screen.blit(error_text, error_rect)
            
            wrapped_msg = textwrap.wrap(f"{message}. The game will reset.", width=40)
            for i, line in enumerate(wrapped_msg):
                msg_text = self.pixel_font_small.render(line, True, (255, 255, 255))
                msg_rect = msg_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + i * 30))
                self.screen.blit(msg_text, msg_rect)
            
            pygame.display.flip()
            pygame.time.wait(3000)
        finally:
            self.reset_game()

    def load_assets(self):
        """Load fonts and other assets with fallbacks"""
        try:
            self.pixel_font_small = pygame.font.Font(None, 24)
            self.pixel_font_medium = pygame.font.Font(None, 32)
            self.pixel_font_large = pygame.font.Font(None, 48)
            
            try:
                custom_font = pygame.font.Font("assets/PressStart2P.ttf", 14)
                self.pixel_font_small = custom_font
                self.pixel_font_medium = pygame.font.Font("assets/PressStart2P.ttf", 18)
                self.pixel_font_large = pygame.font.Font("assets/PressStart2P.ttf", 24)
            except:
                pass
            
            # Load background image
            try:
                self.background_image = pygame.image.load("assets/background.png").convert()
                self.background_image = pygame.transform.scale(self.background_image, 
                                                             (self.screen_width, self.screen_height))
            except:
                self.background_image = None
        except:
            self.handle_critical_error("Asset loading failed")

        # Updated color scheme with green shades
        self.COLORS = {
            'background': (230, 245, 230),
            'panel': (200, 230, 200),
            'dark_panel': (100, 160, 100),
            'border': (50, 100, 50),
            'text': (20, 40, 20),
            'warning': (200, 180, 0),
            'danger': (200, 80, 80),
            'success': (50, 180, 50),
            'highlight': (120, 200, 120),
            'button': (180, 210, 180),
            'button_hover': (200, 230, 200),
            'button_selected': (80, 180, 80)
        }

        # Load product images and scale them for header display
        try:
            self.product_images = {}
            # Load and scale Pizza image (60x60)
            self.product_images["Pizza"] = pygame.image.load("assets/Pizza.png").convert_alpha()
            self.product_images["Pizza"] = pygame.transform.scale(self.product_images["Pizza"], (60, 60))
            
            # Load and scale E-Bike image (60x60)
            self.product_images["E-Bike"] = pygame.image.load("assets/Ebike.png").convert_alpha()
            self.product_images["E-Bike"] = pygame.transform.scale(self.product_images["E-Bike"], (60, 60))
            
            # Load and scale Smartphone image (70x70)
            self.product_images["Smartphone"] = pygame.image.load("assets/SmartPhone.png").convert_alpha()
            self.product_images["Smartphone"] = pygame.transform.scale(self.product_images["Smartphone"], (70, 70))
        except Exception as e:
            print("Error loading product images:", e)





    def load_processes(self):
        """Load all production processes with their options - now more affordable and balanced"""
        processes = {
            "Pizza": {
                "Ingredient Sourcing": {
                    "Conventional": {
                        "cost": 800, 
                        "emissions": 1000, 
                        "efficiency": 2, 
                        "happiness": 2,
                        "info": "Cheap ingredients but high emissions from transport and farming"
                    },
                    "Organic": {
                        "cost": 1200, 
                        "emissions": 600, 
                        "efficiency": 3, 
                        "happiness": 3,
                        "info": "No pesticides but lower yields increase land use"
                    },
                    "Local\nSeasonal": {  # Changed to two lines
                        "cost": 1000, 
                        "emissions": 300, 
                        "efficiency": 4, 
                        "happiness": 4,
                        "info": "Low transport emissions but limited ingredient variety"
                    },
                    "Plant Based": {
                        "cost": 1100, 
                        "emissions": 350, 
                        "efficiency": 4, 
                        "happiness": 3,
                        "info": "Lower emissions but may need more processing"
                    }
                },
                "Dough Preparation": {
                    "Mass Produced": {
                        "cost": 600, 
                        "emissions": 500, 
                        "efficiency": 3, 
                        "happiness": 2,
                        "info": "Factory-made saves labor but uses more energy"
                    },
                    "Handmade": {
                        "cost": 1000, 
                        "emissions": 200, 
                        "efficiency": 4, 
                        "happiness": 4,
                        "info": "Artisanal quality with lower energy use"
                    }
                },
                "Baking": {
                    "Gas Oven": {
                        "cost": 800, 
                        "emissions": 1200, 
                        "efficiency": 3, 
                        "happiness": 3,
                        "info": "Fast baking but burns fossil fuels"
                    },
                    "Wood Fired": {
                        "cost": 1000, 
                        "emissions": 800, 
                        "efficiency": 4, 
                        "happiness": 4,
                        "info": "Traditional method with renewable fuel"
                    },
                    "Solar": {
                        "cost": 1500, 
                        "emissions": 50, 
                        "efficiency": 5, 
                        "happiness": 3,
                        "info": "Zero emissions but weather dependent"
                    }
                },
                "Packaging": {
                    "Plastic": {
                        "cost": 300, 
                        "emissions": 800, 
                        "efficiency": 5, 
                        "happiness": 2,
                        "info": "Cheap and durable but non-biodegradable"
                    },
                    "Biodegradable": {
                        "cost": 700, 
                        "emissions": 300, 
                        "efficiency": 4, 
                        "happiness": 4,
                        "info": "Eco-friendly but more expensive"
                    }
                }
            },
            "E-Bike": {
                "Battery Production": {
                    "Lithium Mining": {
                        "cost": 2000, 
                        "emissions": 4500, 
                        "efficiency": 5, 
                        "happiness": 3,
                        "info": "High performance but destructive mining"
                    },
                    "Recycled Batteries": {
                        "cost": 1800, 
                        "emissions": 1800, 
                        "efficiency": 4, 
                        "happiness": 4,
                        "info": "Lower impact but shorter lifespan"
                    }
                },
                "Frame Production": {
                    "Aluminum": {
                        "cost": 1500, 
                        "emissions": 3000, 
                        "efficiency": 4, 
                        "happiness": 3,
                        "info": "Lightweight but energy-intensive production"
                    },
                    "Carbon Fiber": {
                        "cost": 2500, 
                        "emissions": 1500, 
                        "efficiency": 5, 
                        "happiness": 5,
                        "info": "Premium material with lower emissions"
                    }
                },
                "Assembly": {
                    "Manual": {
                        "cost": 1200, 
                        "emissions": 1000, 
                        "efficiency": 4, 
                        "happiness": 4,
                        "info": "Skilled labor with better quality control"
                    },
                    "Automated": {
                        "cost": 2000, 
                        "emissions": 500, 
                        "efficiency": 5, 
                        "happiness": 3,
                        "info": "Precise but high initial investment"
                    }
                }
            },
            "Smartphone": {
                "Component Production": {
                    "Outsource": {
                        "cost": 1500, 
                        "emissions": 3000, 
                        "efficiency": 4, 
                        "happiness": 3,
                        "info": "Cheaper labor but long supply chains"
                    },
                    "In-House": {
                        "cost": 2500, 
                        "emissions": 1500, 
                        "efficiency": 5, 
                        "happiness": 4,
                        "info": "Better oversight but higher costs"
                    }
                },
                "Distribution": {
                    "Air Freight": {
                        "cost": 2000, 
                        "emissions": 4000, 
                        "efficiency": 5, 
                        "happiness": 4,
                        "info": "Fast delivery but very high emissions"
                    },
                    "Sea Freight": {
                        "cost": 1500, 
                        "emissions": 2000, 
                        "efficiency": 4, 
                        "happiness": 3,
                        "info": "Slower but much cleaner transport"
                    }
                }
            }
        }
        return processes

    def reset_game(self):
        """Reset all game state variables with dynamic budget"""
        try:
            self.budget = 0
            self.current_emissions = 0
            self.current_happiness = 0
            self.emission_warnings = 0
            self.game_state = "playing"
            self.error_occurred = False
            
            self.player_choices = {product: {} for product in self.processes.keys()}
            
            for product, processes in self.processes.items():
                for process in processes.keys():
                    self.player_choices[product][process] = None
            
            # Generate random budget
            budget_level = random.choice(self.budget_levels)
            min_budget, max_budget = self.budget_ranges[budget_level]
            self.budget = random.randint(min_budget, max_budget)
            
            # Calculate dynamic thresholds based on budget
            self.calculate_dynamic_thresholds()
            
            self.current_product = random.choice(list(self.processes.keys()))
            self.info_message = (f"Welcome! {budget_level} budget: ${self.budget}. "
                               f"Max emissions: {self.MAX_EMISSION_THRESHOLD}. "
                               "Balance cost, emissions, and happiness.")
            
            self.create_ui_elements()
        except:
            self.handle_critical_error("Game reset failed")

    def create_ui_elements(self):
        """Create all UI buttons and elements"""
        try:
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
            
            self.create_process_buttons()
            
            self.reset_button = PixelButton(
                self.screen_width - 150, 80, 
                140, 30, 
                "Reset Game", 
                self.pixel_font_small,
                normal_color=self.COLORS['button'],
                hover_color=self.COLORS['button_hover'],
                border_color=self.COLORS['border']
            )
        except:
            self.handle_critical_error("UI creation failed")

    def create_process_buttons(self):
        """Create buttons for the current product's processes"""
        try:
            self.process_buttons = []
            y_offset = 180
            
            for process, options in self.processes[self.current_product].items():
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
                    
                    if self.player_choices[self.current_product].get(process) == option:
                        button.is_selected = True
                    
                    self.process_buttons.append(button)
                
                y_offset += 70
        except:
            self.handle_critical_error("Process buttons creation failed")

    def select_process_option(self, product, process, option):
        """Select a production option for a process"""
        try:
            if product not in self.processes or process not in self.processes[product] or option not in self.processes[product][process]:
                self.info_message = "Invalid selection. Please try again."
                return False
            
            option_data = self.processes[product][process][option]
            
            if option_data["cost"] > self.budget:
                self.info_message = f"Not enough budget for {option}! Need ${option_data['cost']}, have ${self.budget}."
                return False
            
            # Refund previous option if exists
            if self.player_choices[product].get(process) is not None:
                previous_option = self.player_choices[product][process]
                if previous_option in self.processes[product][process]:
                    previous_data = self.processes[product][process][previous_option]
                    self.budget += previous_data["cost"]
                    self.current_emissions -= previous_data["emissions"]
            
            # Apply new option
            self.player_choices[product][process] = option
            self.budget -= option_data["cost"]
            self.current_emissions += option_data["emissions"]
            self.info_message = f"{option_data['info']}\nCost: ${option_data['cost']} | Emissions: {option_data['emissions']}"
            
            self.check_emission_warnings()
            self.calculate_happiness()
            
            # Check if all processes are filled
            all_filled = all(
                self.player_choices[prod].get(proc) is not None
                for prod in self.processes
                for proc in self.processes[prod]
            )
            
            if all_filled:
                self.check_game_conditions()
            
            return True
        except Exception as e:
            self.handle_critical_error(f"Selection error: {str(e)}")
            return False

    def check_emission_warnings(self):
        """Check if emissions exceed warning thresholds"""
        try:
            if self.current_emissions > self.SEVERE_EMISSION_THRESHOLD and self.emission_warnings < 4:
                self.emission_warnings = 4
                self.game_over("Production halted! Emissions critically high (4th warning).")
            elif self.current_emissions > self.WARNING_EMISSION_THRESHOLD:
                if self.emission_warnings == 0:
                    self.emission_warnings = 1
                    self.info_message = "WARNING: Emissions approaching dangerous levels (1st warning)"
                elif self.emission_warnings == 1:
                    self.emission_warnings = 2
                    fine = ceil(self.budget * 0.05)  # Reduced to 5% fine
                    self.budget -= fine
                    self.info_message = f"WARNING: High emissions! ${fine} fine (2nd warning)."
                elif self.emission_warnings == 2:
                    self.emission_warnings = 3
                    fine = ceil(self.budget * 0.10)  # Reduced to 10% fine
                    self.budget -= fine
                    self.info_message = f"SEVERE WARNING: Emissions very high! ${fine} fine (3rd warning)."
        except:
            self.handle_critical_error("Emission check failed")

    def calculate_happiness(self):
        """Calculate overall happiness score based on selected options"""
        try:
            total_happiness = 0
            selected_options = 0
            
            for product in self.processes:
                for process in self.processes[product]:
                    if self.player_choices[product].get(process) is not None:
                        option = self.player_choices[product][process]
                        total_happiness += self.processes[product][process][option]["happiness"]
                        selected_options += 1
            
            if selected_options > 0:
                self.current_happiness = int((total_happiness / (selected_options * 5)) * 100)
            else:
                self.current_happiness = 0
        except:
            self.handle_critical_error("Happiness calculation failed")

    def check_game_conditions(self):
        """Check if game over conditions are met - with more forgiving thresholds"""
        try:
            if self.current_emissions > self.MAX_EMISSION_THRESHOLD:
                self.game_over("Game Over: Excessive Emissions! Your production emits too much CO2.")
                return
            
            if self.current_happiness < self.MIN_HAPPINESS_THRESHOLD:
                self.game_over(f"Game Over: Unhappy Customers! Only {self.current_happiness}% happiness.")
                return
            
            if self.budget < 0:
                self.game_over("Game Over: Bankrupt! You've exceeded your budget.")
                return
            
            all_filled = all(
                self.player_choices[prod].get(proc) is not None
                for prod in self.processes
                for proc in self.processes[prod]
            )
            
            if all_filled:
                emission_ratio = self.current_emissions / self.MAX_EMISSION_THRESHOLD
                if emission_ratio < 0.4:
                    self.game_over("Excellent! Highly sustainable product with low emissions!")
                elif emission_ratio < 0.7:
                    self.game_over("Good job! Sustainable product within emissions targets.")
                else:
                    self.game_over("Product complete, but emissions are higher than ideal.")
        except:
            self.handle_critical_error("Game condition check failed")

    def game_over(self, message):
        """Handle game over state"""
        try:
            self.game_state = "game_over"
            self.info_message = message
        except:
            self.handle_critical_error("Game over state failed")

    def draw_background(self):
        """Draw the game background"""
        try:
            if self.background_image:
                self.screen.blit(self.background_image, (0, 0))
            else:
                # Fallback to original grid pattern if image failed to load
                self.screen.fill(self.COLORS['background'])
                for x in range(0, self.screen_width, 20):
                    pygame.draw.line(self.screen, (220, 220, 220), (x, 0), (x, self.screen_height), 1)
                for y in range(0, self.screen_height, 20):
                    pygame.draw.line(self.screen, (220, 220, 220), (0, y), (self.screen_width, y), 1)
        except:
            self.handle_critical_error("Background drawing failed")

    def draw_header_panel(self):
        """Draw the header panel with game stats"""
        try:
            pygame.draw.rect(self.screen, self.COLORS['panel'], (10, 10, self.screen_width - 20, 100), border_radius=5)
            pygame.draw.rect(self.screen, self.COLORS['border'], (10, 10, self.screen_width - 20, 100), 2, border_radius=5)
            
            title_text = self.pixel_font_large.render("CARBON CHASE", True, self.COLORS['text'])
            self.screen.blit(title_text, (20, 15))
            
            budget_color = self.COLORS['danger'] if self.budget < 1000 else self.COLORS['text']
            budget_text = self.pixel_font_medium.render(f"Budget: ${self.budget}", True, budget_color)
            self.screen.blit(budget_text, (20, 50))
            
            emissions_color = self.COLORS['danger'] if self.current_emissions > self.WARNING_EMISSION_THRESHOLD else self.COLORS['text']
            emissions_text = self.pixel_font_medium.render(f"Emissions: {self.current_emissions}/{self.MAX_EMISSION_THRESHOLD}", True, emissions_color)
            self.screen.blit(emissions_text, (300, 50))
            
            happiness_color = self.COLORS['danger'] if self.current_happiness < self.MIN_HAPPINESS_THRESHOLD else self.COLORS['success']
            happiness_text = self.pixel_font_medium.render(f"Happiness: {self.current_happiness}%", True, happiness_color)
            self.screen.blit(happiness_text, (600, 50))
            
            product_text = self.pixel_font_medium.render(f"Product: {self.current_product}", True, self.COLORS['text'])
            self.screen.blit(product_text, (20, 80))
            
            # Draw product image in the header (positioned on the right side)
            # Draw product image in the header (positioned slightly higher)
            if hasattr(self, 'product_images') and self.current_product in self.product_images:
                header_height = 100
                image = self.product_images[self.current_product]
                image_width, image_height = image.get_size()
                
                x_pos = self.screen_width - image_width - 10
                y_pos = 12  # Shift upwards to avoid Reset Game button
                
                self.screen.blit(image, (x_pos, y_pos))

        except:
            self.handle_critical_error("Header panel drawing failed")


    def draw_info_panel(self):
        """Draw the information panel at the bottom"""
        try:
            pygame.draw.rect(self.screen, self.COLORS['panel'], (10, self.screen_height - 140, self.screen_width - 20, 130), border_radius=5)
            pygame.draw.rect(self.screen, self.COLORS['border'], (10, self.screen_height - 140, self.screen_width - 20, 130), 2, border_radius=5)
            
            title_text = self.pixel_font_medium.render("INFORMATION:", True, self.COLORS['text'])
            self.screen.blit(title_text, (20, self.screen_height - 130))
            
            wrapped_text = textwrap.wrap(self.info_message, width=80)
            for i, line in enumerate(wrapped_text[:4]):
                text = self.pixel_font_small.render(line, True, self.COLORS['text'])
                self.screen.blit(text, (20, self.screen_height - 100 + i * 25))
        except:
            self.handle_critical_error("Info panel drawing failed")

    def draw_game_over(self):
        """Draw game over overlay"""
        try:
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.pixel_font_large.render("GAME OVER", True, (255, 100, 100))
            text_rect = game_over_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 50))
            self.screen.blit(game_over_text, text_rect)
            
            result_lines = textwrap.wrap(self.info_message, width=40)
            for i, line in enumerate(result_lines):
                result_text = self.pixel_font_medium.render(line, True, (255, 255, 255))
                result_rect = result_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + i * 30))
                self.screen.blit(result_text, result_rect)
            
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
        except:
            self.handle_critical_error("Game over screen failed")
            return False

    def run(self):
        """Main game loop with error handling"""
        clock = pygame.time.Clock()
        running = True

        while running:
            try:
                mouse_pos = pygame.mouse.get_pos()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    
                    if self.game_state == "playing" and not self.error_occurred:
                        # Product tab selection
                        for button in self.product_buttons:
                            if button.handle_event(event):
                                self.current_product = button.text
                                self.create_process_buttons()
                        
                        # Process option selection
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            for i, button in enumerate(self.process_buttons):
                                if button.handle_event(event):
                                    # Skip process title buttons (they're just labels)
                                    if button.text in self.processes[self.current_product]:
                                        continue
                                    
                                    # Find which process this option belongs to
                                    process_index = 0
                                    options_count = 0
                                    process_names = list(self.processes[self.current_product].keys())
                                    
                                    for idx, process in enumerate(process_names):
                                        options = self.processes[self.current_product][process]
                                        if i < options_count + 1 + len(options):
                                            process_index = idx
                                            break
                                        options_count += 1 + len(options)
                                    
                                    process = process_names[process_index]
                                    option = button.text.split('\n')[0]
                                    
                                    self.select_process_option(self.current_product, process, option)
                                    self.create_process_buttons()
                        
                        # Reset button
                        if self.reset_button.handle_event(event):
                            self.reset_game()
                    
                    # Update hover states for all buttons
                    if self.game_state == "playing":
                        for button in self.product_buttons:
                            button.is_hover = button.rect.collidepoint(mouse_pos)
                        
                        for button in self.process_buttons:
                            button.is_hover = button.rect.collidepoint(mouse_pos)
                        
                        self.reset_button.is_hover = self.reset_button.rect.collidepoint(mouse_pos)
                
                # Drawing
                self.draw_background()
                self.draw_header_panel()
                
                for button in self.product_buttons:
                    button.draw(self.screen)
                
                if self.game_state == "playing":
                    for button in self.process_buttons:
                        button.draw(self.screen)
                    self.reset_button.draw(self.screen)
                
                self.draw_info_panel()
                
                if self.game_state == "game_over":
                    if self.draw_game_over():
                        continue
                
                pygame.display.flip()
                clock.tick(60)
            
            except Exception as e:
                self.handle_critical_error(f"Game loop error: {str(e)}")

        pygame.quit()
        sys.exit()

def main():
    game = CarbonChaseGame()
    game.run()

if __name__ == "__main__":
    main()