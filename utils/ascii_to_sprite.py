#!/usr/bin/env python3
"""
Convert ASCII art files to sprite images.
Reads .txt files from ascii_files/ directory and generates PNG sprites.
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw


class ASCIIToSprite:
    """Convert ASCII art to sprite images."""
    
    # Character to color/brightness mapping
    # Characters ordered from darkest to brightest
    CHAR_MAP = {
        ' ': 0,      # Empty/background
        '.': 30,     # Very dark
        ':': 60,     # Dark
        '-': 90,     # Medium-dark
        '=': 120,    # Medium
        '+': 150,    # Medium-light
        '*': 180,    # Light
        '#': 210,    # Very light
        '%': 230,    # Brighter
        '@': 255,    # Brightest
    }
    
    def __init__(self, pixel_size=4, color_scheme='monochrome'):
        """
        Initialize the converter.
        
        Args:
            pixel_size: Size of each character in pixels
            color_scheme: 'monochrome', 'green', 'red', 'blue', 'orange', 'purple'
        """
        self.pixel_size = pixel_size
        self.color_scheme = color_scheme
    
    def get_color(self, char):
        """
        Get color for a character based on brightness and color scheme.
        
        Args:
            char: ASCII character
            
        Returns:
            RGB tuple
        """
        brightness = self.CHAR_MAP.get(char, 128)
        
        if self.color_scheme == 'monochrome':
            return (brightness, brightness, brightness)
        elif self.color_scheme == 'green':
            return (brightness // 3, brightness, brightness // 3)
        elif self.color_scheme == 'red':
            return (brightness, brightness // 3, brightness // 3)
        elif self.color_scheme == 'blue':
            return (brightness // 3, brightness // 3, brightness)
        elif self.color_scheme == 'orange':
            return (brightness, int(brightness * 0.65), brightness // 4)
        elif self.color_scheme == 'purple':
            return (int(brightness * 0.8), brightness // 3, brightness)
        else:
            return (brightness, brightness, brightness)
    
    def load_ascii_art(self, filepath):
        """
        Load ASCII art from file.
        
        Args:
            filepath: Path to ASCII art file
            
        Returns:
            List of strings (lines)
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Remove trailing newlines but preserve spacing
        lines = [line.rstrip('\n\r') for line in lines]
        
        # Remove completely empty lines at start and end
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        
        return lines
    
    def convert_to_sprite(self, ascii_lines, output_path, 
                         bg_transparent=True, custom_colors=None):
        """
        Convert ASCII art to sprite image.
        
        Args:
            ascii_lines: List of ASCII art lines
            output_path: Path to save PNG file
            bg_transparent: Make background transparent
            custom_colors: Optional dict mapping characters to RGB tuples
        """
        if not ascii_lines:
            return
        
        # Calculate dimensions
        max_width = max(len(line) for line in ascii_lines)
        height = len(ascii_lines)
        
        # Create image
        width_px = max_width * self.pixel_size
        height_px = height * self.pixel_size
        
        # Create RGBA image for transparency
        image = Image.new('RGBA', (width_px, height_px), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw each character
        for y, line in enumerate(ascii_lines):
            for x, char in enumerate(line):
                if char == ' ':
                    continue  # Skip spaces (transparent)
                
                # Get color
                if custom_colors and char in custom_colors:
                    color = custom_colors[char]
                else:
                    color = self.get_color(char)
                
                # Add alpha channel (fully opaque)
                color = color + (255,)
                
                # Draw rectangle (character pixel)
                x1 = x * self.pixel_size
                y1 = y * self.pixel_size
                x2 = x1 + self.pixel_size
                y2 = y1 + self.pixel_size
                
                draw.rectangle([x1, y1, x2, y2], fill=color)
        
        # Save as PNG
        image.save(output_path, 'PNG')
        print(f"Created: {output_path}")
    def convert_all_ascii_files(self, input_dir='ascii_files', 
                                output_dir='assets/sprites',
                                sizes=[32, 64, 128]):
        """
        Convert all ASCII files in directory to sprites at multiple sizes.
        
        Args:
            input_dir: Directory containing ASCII art files
            output_dir: Directory to save sprite images
            sizes: List of pixel sizes to generate
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        # Create output directory
        output_path.mkdir(exist_ok=True)
        
        # Process each .txt file
        for ascii_file in sorted(input_path.glob('*.txt')):
            if ascii_file.name == 'test.txt':
                continue  # Skip test file
            
            print(f"\nProcessing: {ascii_file.name}")
            
            # Load ASCII art
            ascii_lines = self.load_ascii_art(ascii_file)
            
            if not ascii_lines:
                print(f"  Skipped (empty file)")
                continue
            
            # Base name without extension
            base_name = ascii_file.stem
            
            # Generate sprites at different sizes
            for size in sizes:
                self.pixel_size = size // max(len(ascii_lines), 
                                             max(len(line) for line in ascii_lines))
                
                # Ensure minimum pixel size
                self.pixel_size = max(1, self.pixel_size)
                
                output_file = output_path / f"{base_name}_{size}.png"
                self.convert_to_sprite(ascii_lines, str(output_file))


def main():
    """Generate sprites from ASCII art files."""
    print("ASCII Art to Sprite Converter")
    print("=" * 50)
    
    converter = ASCIIToSprite(pixel_size=4, color_scheme='monochrome')
    
    # Convert all files at 32x32, 64x64, and 128x128
    converter.convert_all_ascii_files(
        input_dir='ascii_files',
        output_dir='assets/sprites',
        sizes=[32, 64, 128]
    )
    
    print("\n" + "=" * 50)
    print("Sprite generation complete!")
    print("Check the 'assets/sprites/' directory for output.")


if __name__ == '__main__':
    main()
