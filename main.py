from spatial_detector import SimpleSpatialDetector
from ai_agent import SimpleAIAgent
import os
import sys


def main():
    """Main entry point for the spatial reasoning vision system."""
    # Check for required arguments
    if len(sys.argv) < 3:
        print("Usage: python main.py <image_path> <object_description>")
        print("Example: python main.py test_image.jpg 'red car'")
        sys.exit(1)
    
    image_path = sys.argv[1]
    object_description = sys.argv[2]
    
    # Check if image file exists
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found")
        sys.exit(1)
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is required")
        print("Set it with: export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    try:
        # Initialize AI agent with API key
        print(f"Initializing AI agent...")
        agent = SimpleAIAgent(api_key)
        
        # Create detector
        print(f"Creating spatial detector...")
        detector = SimpleSpatialDetector(agent)
        
        # Run detection
        print(f"Detecting '{object_description}' in '{image_path}'...")
        result = detector.detect(image_path, object_description)
        
        # Display results
        print("\n" + "="*50)
        print("DETECTION RESULTS")
        print("="*50)
        print(f"Object: {object_description}")
        print(f"Confidence: {result['confidence']} ({result['confidence_score']:.1f}%)")
        print(f"Bounding Box: {result['bbox']}")
        print(f"Iterations: {result['iterations']}")
        
        if result['result_image_path']:
            print(f"Result image saved to: {result['result_image_path']}")
        else:
            print("No object detected - no result image created")
        
    except Exception as e:
        print(f"Error during detection: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()