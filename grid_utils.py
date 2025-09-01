from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Tuple


def overlay_grid_on_image(image: Image.Image, rows: int = 4, cols: int = 3) -> Tuple[Image.Image, Dict[int, Tuple[int, int, int, int]]]:
    """
    Overlay a numbered grid on an image.
    
    Args:
        image: PIL Image to overlay grid on
        rows: Number of rows in grid
        cols: Number of columns in grid
        
    Returns:
        tuple: (grid_image, cell_mapping)
        - grid_image: Image with grid overlay
        - cell_mapping: Dict mapping cell_id to (x, y, width, height)
    """
    # Make a copy to avoid modifying original
    grid_image = image.copy()
    draw = ImageDraw.Draw(grid_image)
    
    # Calculate cell dimensions
    cell_width = image.width // cols
    cell_height = image.height // rows
    
    # Create cell mapping
    cell_mapping = {}
    cell_id = 1
    
    # Draw grid lines and add cell numbers
    for row in range(rows):
        for col in range(cols):
            # Calculate cell boundaries
            x = col * cell_width
            y = row * cell_height
            
            # Store cell mapping
            cell_mapping[cell_id] = (x, y, cell_width, cell_height)
            
            # Draw cell border
            draw.rectangle([x, y, x + cell_width, y + cell_height], outline="red", width=2)
            
            # Add cell number label
            # Try to use a reasonable font size
            font_size = min(cell_width, cell_height) // 8
            try:
                # Try to use a system font
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
            except:
                # Fall back to default font
                try:
                    font = ImageFont.load_default()
                except:
                    font = None
            
            # Calculate text position (top-left corner with small padding)
            text_x = x + 5
            text_y = y + 5
            
            # Draw cell number
            draw.text((text_x, text_y), str(cell_id), fill="red", font=font)
            
            cell_id += 1
    
    return grid_image, cell_mapping