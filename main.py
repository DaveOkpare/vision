from spatial_detector import SimpleSpatialDetector
from ai_agent import SimpleAIAgent
import os
import sys


def main():
    """Main entry point for the spatial reasoning vision system."""
    # Check for required arguments
    if len(sys.argv) < 3:
        print("Usage:")
        print("  Single object: python main.py <image_path> <object_description>")
        print("  Multiple objects: python main.py <image_path> --multi <obj1> <obj2> [obj3...]")
        print("\nExamples:")
        print("  python main.py test_image.jpg 'red car'")
        print("  python main.py test_image.jpg --multi 'red car' 'person' 'traffic light'")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Check if multi-object detection is requested
    if len(sys.argv) > 2 and sys.argv[2] == '--multi':
        if len(sys.argv) < 4:
            print("Error: At least one object description is required with --multi flag")
            sys.exit(1)
        multi_mode = True
        object_descriptions = sys.argv[3:]
    else:
        multi_mode = False
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
        
        # Run appropriate detection mode
        if multi_mode:
            # Multi-object detection
            print(f"Detecting {len(object_descriptions)} objects in '{image_path}':")
            for i, obj in enumerate(object_descriptions, 1):
                print(f"  {i}. {obj}")
            
            results = detector.detect_multiple(image_path, object_descriptions)
            
            # Display results
            print("\n" + "="*60)
            print("MULTI-OBJECT DETECTION RESULTS")
            print("="*60)
            
            if results:
                print(f"Successfully detected {len(results)} out of {len(object_descriptions)} objects:\n")
                
                for i, result in enumerate(results, 1):
                    print(f"{i}. Object: {result['object']}")
                    print(f"   Confidence: {result['confidence']} ({result['confidence_score']:.1f}%)")
                    print(f"   Bounding Box: {result['bbox']}")
                    print(f"   Iterations: {result['iterations']}")
                    print(f"   Individual result: {result['result_image_path']}")
                    print()
                
                if 'combined_result_image_path' in results[0]:
                    print(f"Combined visualization saved to: {results[0]['combined_result_image_path']}")
            else:
                print("No objects were detected with sufficient confidence.")
                print("Try adjusting object descriptions or using different images.")
        else:
            # Single object detection
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