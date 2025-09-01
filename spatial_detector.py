from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Tuple
from grid_utils import overlay_grid_on_image
from ai_agent import SimpleAIAgent


def categorize_confidence(raw_score: float) -> str:
    """
    Convert raw confidence percentage to categorical confidence.
    
    Args:
        raw_score: Raw confidence score (0-100)
        
    Returns:
        Categorical confidence string
    """
    if raw_score >= 90:
        return "certain"
    elif raw_score >= 75:
        return "high"
    elif raw_score >= 60:
        return "medium"
    elif raw_score >= 45:
        return "low"
    else:
        return "uncertain"


class SimpleSpatialDetector:
    """Main spatial detection class using recursive grid analysis."""
    
    def __init__(self, ai_agent: SimpleAIAgent):
        """
        Initialize the spatial detector.
        
        Args:
            ai_agent: Configured SimpleAIAgent instance
        """
        self.agent = ai_agent
        self.max_crops = 4
        self.convergence_threshold = 0.6
        
    def detect(self, image_path: str, object_description: str) -> Dict:
        """
        Detect object in image using recursive grid analysis.
        
        Args:
            image_path: Path to input image
            object_description: Description of object to detect
            
        Returns:
            Dict containing detection results
        """
        # 1. Load image
        image = Image.open(image_path).convert("RGB")
        original_image = image.copy()  # Keep reference for coordinate restoration
        
        # 2. Initialize tracking variables
        origin_coordinates = (0, 0)  # Cumulative offset from original image
        iterations = 0
        
        # 3. Iterative cropping loop
        while iterations < self.max_crops:
            # a. Check terminal condition (image too small or convergence)
            if self._is_terminal_state(image, original_image):
                break
                
            # b. Overlay 4x3 grid on current image
            grid_image, cell_mapping = overlay_grid_on_image(image, 4, 3)
            
            # c. AI analysis: get cells containing object
            ai_response = self.agent.analyze_grid(grid_image, object_description)
            
            # d. Check if AI found any confident cells
            if not ai_response['cells']:
                break
            
            # e. Convert cells to bounding box
            crop_bbox = self._cells_to_bbox(ai_response['cells'], cell_mapping)
            
            # f. Crop image to that region
            image = image.crop(crop_bbox)
            
            # g. Update cumulative coordinate offset
            origin_coordinates = (
                origin_coordinates[0] + crop_bbox[0],
                origin_coordinates[1] + crop_bbox[1]
            )
            
            iterations += 1
        
        # 4. Final detection on cropped image
        final_grid_image, final_cell_mapping = overlay_grid_on_image(image, 4, 3)
        final_response = self.agent.analyze_grid(final_grid_image, object_description)
        
        # 5. Handle case where no object is detected
        if not final_response['cells'] or not final_response['confidence_scores']:
            return {
                "bbox": (0, 0, 0, 0),
                "confidence": "uncertain",
                "confidence_score": 0,
                "iterations": iterations,
                "result_image_path": None,
                "result_image": original_image
            }
        
        # 6. Calculate final bounding box in cropped image space
        final_bbox_crop = self._cells_to_bbox(final_response['cells'], final_cell_mapping)
        
        # 7. Transform back to original image coordinates
        final_bbox_original = (
            final_bbox_crop[0] + origin_coordinates[0],
            final_bbox_crop[1] + origin_coordinates[1], 
            final_bbox_crop[2] + origin_coordinates[0],
            final_bbox_crop[3] + origin_coordinates[1]
        )
        
        # 8. Calculate overall confidence and categorize
        avg_confidence = sum(final_response['confidence_scores']) / len(final_response['confidence_scores'])
        confidence_category = categorize_confidence(avg_confidence)
        
        # 9. Create visualization and save it
        result_image = self._draw_bbox_on_original(original_image, final_bbox_original, confidence_category)
        output_path = image_path.replace('.', '_detected.')
        result_image.save(output_path)
        
        return {
            "bbox": final_bbox_original,
            "confidence": confidence_category,
            "confidence_score": avg_confidence,
            "iterations": iterations,
            "result_image_path": output_path,
            "result_image": result_image
        }
    
    def _is_terminal_state(self, current_image: Image.Image, original_image: Image.Image) -> bool:
        """
        Check if we should stop cropping.
        
        Args:
            current_image: Current cropped image
            original_image: Original input image
            
        Returns:
            True if we should stop cropping
        """
        # Calculate area ratio between current crop and original image
        current_area = current_image.width * current_image.height
        original_area = original_image.width * original_image.height
        area_ratio = current_area / original_area
        
        return (area_ratio > self.convergence_threshold or 
                (current_image.width < 512 and current_image.height < 512))
    
    def _cells_to_bbox(self, cell_ids: List[int], cell_mapping: Dict[int, Tuple[int, int, int, int]]) -> Tuple[int, int, int, int]:
        """
        Convert selected cells to bounding box coordinates.
        
        Args:
            cell_ids: List of selected cell IDs
            cell_mapping: Mapping from cell ID to (x, y, width, height)
            
        Returns:
            Bounding box as (left, top, right, bottom)
        """
        if not cell_ids:
            return (0, 0, 0, 0)
        
        # Find minimum x, y and maximum x+width, y+height across all selected cells
        min_x = float('inf')
        min_y = float('inf')
        max_x = 0
        max_y = 0
        
        for cell_id in cell_ids:
            if cell_id in cell_mapping:
                x, y, width, height = cell_mapping[cell_id]
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x + width)
                max_y = max(max_y, y + height)
        
        return (int(min_x), int(min_y), int(max_x), int(max_y))
    
    def _draw_bbox_on_original(self, image: Image.Image, bbox: Tuple[int, int, int, int], confidence_category: str) -> Image.Image:
        """
        Draw bounding box on original image for visualization.
        
        Args:
            image: Original image
            bbox: Bounding box as (left, top, right, bottom)
            confidence_category: Confidence category string
            
        Returns:
            Image with bbox and label drawn
        """
        result_image = image.copy()
        draw = ImageDraw.Draw(result_image)
        
        # Choose color based on confidence
        color_map = {
            "certain": "green",
            "high": "blue",
            "medium": "orange",
            "low": "yellow",
            "uncertain": "red"
        }
        color = color_map.get(confidence_category, "red")
        
        # Draw bounding box
        draw.rectangle(bbox, outline=color, width=3)
        
        # Add confidence label
        label = f"{confidence_category}"
        label_x, label_y = bbox[0], max(0, bbox[1] - 25)
        
        try:
            # Try to use a system font
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        except:
            # Fall back to default font
            try:
                font = ImageFont.load_default()
            except:
                font = None
        
        # Draw label background
        if font:
            bbox_text = draw.textbbox((label_x, label_y), label, font=font)
            draw.rectangle(bbox_text, fill=color)
            draw.text((label_x, label_y), label, fill="white", font=font)
        else:
            draw.text((label_x, label_y), label, fill=color)
        
        return result_image