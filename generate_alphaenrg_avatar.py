#!/usr/bin/env python3
"""
Generate AlphaENRG Avatar
Options for different AI image generation services
"""

# Option 1: If ComfyUI becomes available
COMFYUI_PROMPT = """
Professional AI energy analyst avatar, sophisticated young female, sharp intelligent eyes, 
sleek dark business blazer, confident expression, subtle energy wave patterns in background, 
professional corporate headshot, institutional finance aesthetic, clean modern look with 
slight sci-fi edge, professional studio lighting, high quality portrait, SDXL style
"""

# Option 2: Midjourney prompt
MIDJOURNEY_PROMPT = """
Professional energy analyst avatar, confident intelligent woman, dark blazer, 
energy tech background, corporate headshot, institutional grade, --ar 1:1 --style professional
"""

# Option 3: DALL-E 3 prompt
DALLE_PROMPT = """
Professional corporate headshot of a confident female energy analyst, wearing a dark blazer, 
intelligent expression, subtle energy/tech background elements, high-quality business portrait 
for social media profile, institutional investment aesthetic
"""

# Option 4: Stable Diffusion prompt
SD_PROMPT = """
professional headshot portrait, confident female energy analyst, dark business attire, 
intelligent gaze, subtle energy wave background, corporate lighting, high quality, 
institutional grade aesthetic, clean modern style
"""

print("AlphaENRG Avatar Generation Options:")
print("=" * 50)
print(f"ComfyUI: {COMFYUI_PROMPT}")
print(f"\nMidjourney: {MIDJOURNEY_PROMPT}")  
print(f"\nDALL-E 3: {DALLE_PROMPT}")
print(f"\nStable Diffusion: {SD_PROMPT}")

# If we want to use ComfyUI when it's running
def generate_with_comfyui():
    """Generate avatar using ComfyUI on Mac Mini M4"""
    import requests
    import json
    
    # Load the FaceID workflow
    try:
        with open('../comfyui-workflows/faceid_portrait_sdxl.json', 'r') as f:
            workflow = json.load(f)
        
        # Modify prompt for avatar generation
        # (Would need to identify the text prompt node and update it)
        
        # Submit to ComfyUI
        comfyui_url = "http://100.98.31.10:8188"
        response = requests.post(f"{comfyui_url}/prompt", json={"prompt": workflow})
        
        if response.status_code == 200:
            print("✅ Avatar generation submitted to ComfyUI")
            return response.json()
        else:
            print(f"❌ ComfyUI error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ ComfyUI generation failed: {e}")
        return None

if __name__ == "__main__":
    print("\n🎯 Ready to generate AlphaENRG avatar!")
    print("Choose your preferred AI image generation method above.")