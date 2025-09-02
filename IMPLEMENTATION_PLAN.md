# Simplified Spatial Reasoning Implementation Plan

## Overview
Implement a simplified version of the spatial-reasoning algorithm that uses grid-based AI analysis for object detection with recursive cropping and coordinate transformation.

## ⚠️ Important Design Note
**The code provided in this plan is for architectural guidance and conceptual understanding only.** 

The implementer should:
- **Think critically** about each design decision and consider alternatives
- **Adapt the architecture** to fit specific requirements and constraints  
- **Question assumptions** and evaluate trade-offs for each component
- **Design optimal solutions** rather than copying code verbatim
- **Consider edge cases** and error scenarios not explicitly covered

This plan outlines the conceptual framework - the actual implementation should be thoughtfully designed based on these principles.

## Core Algorithm

### Single Object Detection
**Input**: Image path + object description  
**Output**: Bounding box coordinates on original image + categorical confidence

### Multi-Object Detection  
**Input**: Image path + list of object descriptions  
**Output**: List of detection results, each containing object name, bounding box, and confidence

## Key Design Decisions to Consider

### Multi-Object Detection Strategy
**Question**: How should we handle multiple object detection?

**Options to evaluate**:
1. **Sequential single-object runs**: Simple but potentially inefficient
2. **Single AI call for all objects**: Efficient but complex parsing
3. **Hybrid approach**: Balance of efficiency and accuracy
4. **Parallel processing**: Fast but resource-intensive

**Consider**: API costs, accuracy trade-offs, implementation complexity, performance requirements

### Error Handling Philosophy  
**Question**: How aggressively should we handle edge cases?

**Design considerations**:
- Graceful degradation vs fast failure
- Retry strategies and backoff mechanisms
- Fallback detection methods when primary approach fails
- User feedback and debugging information

### Confidence Scoring Architecture
**Question**: How do we convert AI responses to reliable confidence metrics?

**Factors to consider**:
- Raw AI confidence vs. post-processed scores
- Multiple confidence sources (cell coverage, AI certainty, bbox size)
- Calibration against ground truth data
- Confidence thresholds for different use cases

### Coordinate System Management
**Question**: How do we maintain accuracy through multiple crop iterations?

**Design challenges**:
- Floating point precision vs integer coordinates
- Coordinate transformation validation
- Boundary condition handling
- Original image coordinate restoration accuracy

## Implementation Components

**Note**: The following code snippets are architectural guidance. Implementers should design optimal solutions for their specific needs.

### 1. Grid Overlay System
**Architectural Role**: Convert images to analyzable grid format for AI processing

**Key Design Questions**:
- **Grid dimensions**: Fixed 4x3 vs dynamic based on image size/content?
- **Label visibility**: How to ensure grid numbers are readable on various image types?
- **Performance**: In-memory processing vs temporary file generation?
- **Grid line styling**: Visibility without interfering with object detection?

**Conceptual Interface** (adapt as needed):
```python
def overlay_grid_on_image(image, rows=4, cols=3):
    # Design considerations:
    # - How to handle very small images where labels become unreadable?
    # - Should grid adapt to image aspect ratio?
    # - How to ensure consistent cell mapping across different image sizes?
    # - What happens if image dimensions aren't evenly divisible?
    
    return grid_image, cell_mapping
```

### 2. AI Agent Interface  
**Architectural Role**: Bridge between image analysis and AI vision capabilities

**Critical Design Decisions**:
- **Model selection**: GPT-4o vs Claude vs specialized vision models?
- **Prompt engineering**: How specific vs general should object descriptions be?
- **Response parsing**: Structured JSON vs natural language parsing?
- **Error recovery**: How to handle API failures, rate limits, malformed responses?
- **Caching strategy**: Should we cache AI responses for identical grid/object combinations?

**Key Performance Considerations**:
- Image encoding efficiency (base64 vs direct upload)
- Prompt length optimization for cost/speed
- Batch processing multiple objects in single API call
- Response validation and sanitization

**Conceptual Architecture**:
```python
class AIAgent:
    def __init__(self, model_config):
        # Design decision: How to handle different AI providers?
        # Consider: failover strategies, cost optimization, model capabilities
        pass
        
    def analyze_grid(self, grid_image, object_description):
        # Critical design questions:
        # - How do we ensure consistent AI interpretation across different images?
        # - Should confidence thresholds be dynamic based on object type?
        # - How do we handle ambiguous objects (e.g., "vehicle" vs "car")?
        # - What's the optimal balance between prompt specificity and flexibility?
        
        # Return structured data - but what format optimizes downstream processing?
        return {'cells': [], 'confidence_scores': []}
```

### 3. Confidence Categorization
**Categories**:
- `"certain"` (90-100%): Object clearly visible, unambiguous match
- `"high"` (75-89%): Strong match, minor occlusion/angle issues  
- `"medium"` (60-74%): Reasonable match, some uncertainty
- `"low"` (45-59%): Weak match, significant ambiguity
- `"uncertain"` (<45%): Very poor match, likely false positive

**Heuristics for Each Category:**
- **`certain`**: Object dominates multiple grid cells, clear boundaries
- **`high`**: Object visible in several cells, good shape/color match
- **`medium`**: Object partially visible, some occlusion or similarity issues
- **`low`**: Questionable match, poor visibility or ambiguous features
- **`uncertain`**: Barely detectable, high chance of false positive

```python
def categorize_confidence(raw_score: float) -> str:
    # Convert raw percentage to category using thresholds above
```

### 4. Spatial Detector Main Class
**File**: `spatial_detector.py`
```python
class SimpleSpatialDetector:
    def __init__(self, ai_agent: SimpleAIAgent):
        self.agent = ai_agent
        self.max_crops = 3
        self.convergence_threshold = 0.6
        
    def detect(self, image_path: str, object_description: str) -> dict:
        # 1. Load image (let provider handle scaling)
        image = PIL.Image.open(image_path).convert("RGB")
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
            
            # d. Convert cells to bounding box
            crop_bbox = self._cells_to_bbox(ai_response['cells'], cell_mapping)
            
            # e. Crop image to that region
            image = image.crop(crop_bbox)
            
            # f. Update cumulative coordinate offset
            origin_coordinates = (
                origin_coordinates[0] + crop_bbox[0],
                origin_coordinates[1] + crop_bbox[1]
            )
            
            iterations += 1
        
        # 4. Final detection on cropped image (using same AI agent)
        final_grid_image, final_cell_mapping = overlay_grid_on_image(image, 4, 3)
        final_response = self.agent.analyze_grid(final_grid_image, object_description)
        
        # 5. Calculate final bounding box in cropped image space
        final_bbox_crop = self._cells_to_bbox(final_response['cells'], final_cell_mapping)
        
        # 6. Transform back to original image coordinates
        final_bbox_original = (
            final_bbox_crop[0] + origin_coordinates[0],
            final_bbox_crop[1] + origin_coordinates[1], 
            final_bbox_crop[2] + origin_coordinates[0],
            final_bbox_crop[3] + origin_coordinates[1]
        )
        
        # 7. Calculate overall confidence and categorize
        avg_confidence = sum(final_response['confidence_scores']) / len(final_response['confidence_scores'])
        confidence_category = categorize_confidence(avg_confidence)
        
        # 8. Create visualization and save it
        result_image = self._draw_bbox_on_original(original_image, final_bbox_original)
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
    
    def detect_multiple(self, image_path: str, object_descriptions: list[str]) -> list[dict]:
        # Multi-object detection using multiple single-object runs
        # 1. Load original image once
        original_image = PIL.Image.open(image_path).convert("RGB")
        
        # 2. Run single detection for each object
        detections = []
        for i, obj_desc in enumerate(object_descriptions):
            detection = self.detect(image_path, obj_desc)
            
            # 3. Add object identifier to result
            detection["object"] = obj_desc
            detection["detection_id"] = i
            
            # 4. Only include confident detections to reduce false positives
            if detection["confidence"] not in ["uncertain", "low"]:
                detections.append(detection)
        
        # 5. Create combined visualization image
        if detections:
            combined_result_image = self._draw_multiple_bboxes_on_original(
                original_image, detections
            )
            combined_output_path = image_path.replace('.', '_multi_detected.')
            combined_result_image.save(combined_output_path)
            
            # Add combined visualization to all detections
            for detection in detections:
                detection["combined_result_image_path"] = combined_output_path
                detection["combined_result_image"] = combined_result_image
        
        return detections
```

### 5. Helper Methods
```python
def _is_terminal_state(self, current_image: PIL.Image, original_image: PIL.Image) -> bool:
    # Calculate area ratio between current crop and original image
    area_ratio = (current_image.width * current_image.height) / (original_image.width * original_image.height)
    return area_ratio > self.convergence_threshold or (current_image.width < 512 and current_image.height < 512)

def _cells_to_bbox(self, cell_ids: list, cell_mapping: dict) -> tuple:
    # Find minimum x, y and maximum x+width, y+height across all selected cells
    # Return (left, top, right, bottom) bounding box
    
def _draw_bbox_on_original(self, image: PIL.Image, bbox: tuple) -> PIL.Image:
    # Draw bounding box on original image for visualization
    # Use PIL.ImageDraw to draw rectangle with colored border
    # Add confidence category text label near bounding box
    # Return image with bbox and label drawn

def _draw_multiple_bboxes_on_original(self, image: PIL.Image, detections: list[dict]) -> PIL.Image:
    # Draw multiple bounding boxes on original image
    # Use different colors for each object type
    # Add object name and confidence labels for each detection
    # Ensure labels don't overlap by staggering positions
    # Return image with all bboxes and labels drawn
```

### 6. AI Prompting Strategy
**Grid Analysis Prompt**:
```
"You are analyzing an image with a numbered grid overlay. Your task is to identify which grid cells contain any part of: [object_description]

Look at each numbered cell and determine:
1. Does this cell contain any portion of the target object?
2. What's your confidence percentage (0-100%)?

Return ONLY this format:
{
    'cells': [cell_numbers_with_object],
    'confidence_scores': [confidence_for_each_cell]
}

Confidence guidelines:
- 90-100%: Most of cell contains object
- 80-89%: About half the cell contains object  
- 70-79%: Substantial portion but less than half
- 60-69%: Small edge or corner of object
- Below 60%: Too uncertain - omit cell

Only include cells with confidence ≥60%. Sort cell numbers in ascending order."
```

## Key Implementation Details

### Coordinate System Management
- **Track cumulative offset** via `origin_coordinates` 
- **Each crop updates offset**: New offset = old offset + crop position
- **Final transformation**: Add cumulative offset to final detection coordinates
- **Result**: Bounding box coordinates work on user's original input image

### Convergence & Termination
- **Area ratio check**: Stop when current crop is >60% of original image area
- **Size limit**: Stop when image <512x512 pixels
- **Safety limit**: Maximum 3 crop iterations
- **Early termination**: If AI finds no confident cells

### Error Handling
- **API failures**: Retry with exponential backoff (from BaseAgent)
- **Parse failures**: Handle malformed AI responses gracefully
- **Invalid cells**: Filter out cell IDs outside grid range
- **Empty detection**: Return empty bbox with "uncertain" confidence

### Dependencies Required
- `pydantic-ai` for AI agent interface
- `PIL` (Pillow) for image processing
- `OpenAI` API access
- `base64` for image encoding (if needed for API)

## File Structure
```
vision/
├── grid_utils.py          # Grid overlay functionality
├── ai_agent.py           # AI agent interface
├── spatial_detector.py   # Main detection class
└── main.py              # Entry point and testing
```

## Entry Point Implementation
**File**: `main.py`
```python
from spatial_detector import SimpleSpatialDetector
from ai_agent import SimpleAIAgent
import os

def main():
    # Initialize AI agent with API key
    api_key = os.getenv("OPENAI_API_KEY")
    agent = SimpleAIAgent(api_key)
    
    # Create detector
    detector = SimpleSpatialDetector(agent)
    
    # Single object detection example
    single_result = detector.detect("test_image.jpg", "red car")
    print(f"Single detection: Found {single_result['confidence']} confidence at {single_result['bbox']}")
    print(f"Result image saved to: {single_result['result_image_path']}")
    
    # Multi-object detection example  
    multi_results = detector.detect_multiple("test_image.jpg", ["red car", "person", "traffic light"])
    print(f"\nMulti-object detection found {len(multi_results)} objects:")
    for result in multi_results:
        print(f"- {result['object']}: {result['confidence']} confidence at {result['bbox']}")
    if multi_results:
        print(f"Combined visualization saved to: {multi_results[0]['combined_result_image_path']}")

if __name__ == "__main__":
    main()
```

## Testing Strategy

### Single Object Detection
1. **Clear single objects**: Test with obvious, well-defined objects
2. **Multi-iteration scenarios**: Test with small objects in large images
3. **Edge cases**: Very small images, no objects present
4. **Confidence validation**: Verify categorical confidence makes sense

### Multi-Object Detection
1. **Multiple distinct objects**: Test with clearly separated objects (car, person, sign)
2. **Overlapping objects**: Test with objects that might overlap (person in car)
3. **Mixed confidence levels**: Some objects clear, others ambiguous
4. **Performance testing**: Measure detection time vs number of objects
5. **False positive filtering**: Verify low-confidence detections are excluded

### Combined Testing
1. **Visualization quality**: Ensure multi-object visualizations are clear and readable
2. **Coordinate accuracy**: Verify all bounding boxes map correctly to original image
3. **Memory usage**: Test with large lists of object descriptions

## System Architecture Principles

This plan provides a **conceptual framework** for spatial reasoning object detection. The actual implementation should be thoughtfully designed based on:

### Design Philosophy
- **Modularity**: Each component should be independently testable and replaceable
- **Flexibility**: System should adapt to different image types, object categories, and performance requirements  
- **Robustness**: Graceful handling of edge cases and error conditions
- **Extensibility**: Easy to add new detection strategies, AI models, or output formats

### Critical Implementation Decisions

**Performance vs Accuracy Trade-offs**:
- How many crop iterations provide optimal results for your use case?
- Should confidence thresholds vary by object type or remain constant?
- Is speed or precision more important for your application?

**Scalability Considerations**:
- How will the system perform with hundreds of concurrent requests?
- Should you implement request queuing, caching, or distributed processing?
- What are the cost implications of your AI model choices?

**User Experience Design**:
- How should the system communicate confidence and uncertainty to users?
- What level of debugging information helps without overwhelming?
- How do you handle cases where no objects are detected?

### Final Implementation Guidance

**Remember**: This plan outlines the conceptual approach. Your implementation should:
1. **Evaluate each design decision** against your specific requirements
2. **Prototype critical components** before full system implementation  
3. **Measure performance** and iterate on bottlenecks
4. **Test edge cases** thoroughly, especially coordinate transformations
5. **Consider alternative approaches** where this framework may not be optimal

The goal is not to copy this architecture verbatim, but to understand the spatial reasoning principles and implement them optimally for your specific context.