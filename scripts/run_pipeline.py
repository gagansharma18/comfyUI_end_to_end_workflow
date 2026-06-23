#!/usr/bin/env python3
import re
import os
import sys
import json
import time
import urllib.request
import urllib.parse

# Hardcoded API configuration representing workflow.json
COMFYUI_URL = "http://127.0.0.1:8188"
OUTPUT_DIR = "./output"

# Define the template for prompt generation
SYSTEM_PROMPT = """System Prompt:
You are an AI storyboard designer for a cartoon series called "Stixx Stories".
Your job is to read the user's script (narration and scene actions) and generate a single detailed visual prompt describing the static starting frame of the scene.

Apply these character consistency guidelines:
- "Bob" is a simple stick figure with a large round white circular head, small black dot eyes, thin curved black eyebrows, and a simple line mouth. Bob has messy spikes of brown hair and wears a basic flat-colored blue t-shirt.
- "Alice" is a simple stick figure with a large round white circular head, small black dot eyes, thin curved black eyebrows, and a simple line mouth. Alice has long straight black hair and wears a basic flat-colored red dress.

Aesthetic Guidelines:
- Style: A stick figure animation in the style of an animated educational webcomic or YouTube explainer video. Thick hand-drawn wobbly black outlines, flat colors, clean minimalist background with a soft warm color palette (light beige and soft green). No 3D shading, no realism, no text, no watermarks, no speech bubbles.

Read the user's script and output exactly one paragraph of prompt describing the static starting frame of the scene. Do not output anything else."""

def get_base_prompt_workflow():
    return {
        "1": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "z_image_turbo_bf16.safetensors",
                "weight_dtype": "default"
            }
        },
        "20": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": "qwen_3_4b.safetensors",
                "type": "lumina2",
                "device": "default"
            }
        },
        "21": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": "ae.safetensors"
            }
        },
        "30": {
            "class_type": "OllamaConnectivityV2",
            "inputs": {
                "url": "http://127.0.0.1:11434",
                "model": "qwen3.6",
                "keep_alive": 5,
                "keep_alive_unit": "minutes"
            }
        },
        "2": {
            "class_type": "OllamaGenerateV2",
            "inputs": {
                "system": "",
                "prompt": "",
                "think": False,
                "keep_context": False,
                "format": "text",
                "connectivity": ["30", 0]
            }
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["20", 0],
                "text": ["2", 0]
            }
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["20", 0],
                "text": "3d shading, gradient lighting, photorealistic, realistic faces, skin texture, text, labels, speech bubbles, watermarks, signature, blurry, low resolution"
            }
        },
        "7": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": 1024,
                "height": 576,
                "batch_size": 1
            }
        },
        "8": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["3", 0],
                "negative": ["6", 0],
                "latent_image": ["7", 0],
                "seed": 8439129532,
                "control_after_generate": "randomize",
                "steps": 9,
                "cfg": 1.0,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0
            }
        },
        "9": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["8", 0],
                "vae": ["21", 0]
            }
        },
        "10": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["9", 0],
                "filename_prefix": "stixx_stories_frame"
            }
        },
        "26": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "ltx-2.3-22b-dev-fp8.safetensors"
            }
        },
        "27": {
            "class_type": "LTXAVTextEncoderLoader",
            "inputs": {
                "text_encoder": "gemma_3_12B_it_fp4_mixed.safetensors",
                "ckpt_name": "ltx-2.3-22b-dev-fp8.safetensors",
                "device": "default"
            }
        },
        "24": {
            "class_type": "LoraLoader",
            "inputs": {
                "model": ["26", 0],
                "clip": ["27", 0],
                "lora_name": "ltx_2.3_22b_distilled_1.1_lora_dynamic_fro09_avg_rank_111_bf16.safetensors",
                "strength_model": 1.0,
                "strength_clip": 1.0
            }
        },
        "25": {
            "class_type": "LoraLoader",
            "inputs": {
                "model": ["24", 0],
                "clip": ["24", 1],
                "lora_name": "gemma-3-12b-it-abliterated_lora_rank64_bf16.safetensors",
                "strength_model": 1.0,
                "strength_clip": 1.0
            }
        },
        "22": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["25", 1],
                "text": ["2", 0]
            }
        },
        "23": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["25", 1],
                "text": "3d, realistic, photorealistic, bad anatomy, text, watermark"
            }
        },
        "13": {
            "class_type": "LTXVConditioning",
            "inputs": {
                "positive": ["22", 0],
                "negative": ["23", 0],
                "frame_rate": 24.0
            }
        },
        "14": {
            "class_type": "EmptyLTXVLatentVideo",
            "inputs": {
                "width": 768,
                "height": 512,
                "length": 49,
                "batch_size": 1
            }
        },
        "15": {
            "class_type": "LTXVImgToVideoConditionOnly",
            "inputs": {
                "vae": ["26", 2],
                "image": ["9", 0],
                "latent": ["14", 0],
                "denoise": 0.7,
                "bypass": False
            }
        },
        "16": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["25", 0],
                "positive": ["13", 0],
                "negative": ["13", 1],
                "latent_image": ["15", 0],
                "seed": 2984572985,
                "control_after_generate": "randomize",
                "steps": 12,
                "cfg": 1.5,
                "sampler_name": "euler",
                "scheduler": "karras",
                "denoise": 1.0
            }
        },
        "17": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["16", 0],
                "vae": ["26", 2]
            }
        },
        "18": {
            "class_type": "VHS_VideoCombine",
            "inputs": {
                "images": ["17", 0],
                "frame_rate": 24,
                "loop_count": 0,
                "filename_prefix": "",
                "format": "video/h264-mp4",
                "pingpong": True,
                "save_output": True
            }
        }
    }

def parse_script(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Split content by scene headers "## "
    scenes_raw = re.split(r"^##\s+", content, flags=re.MULTILINE)
    
    scenes = []
    scene_index = 1
    for raw in scenes_raw:
        if not raw.strip():
            continue
        
        # Extract title (first line)
        lines = raw.strip().split("\n")
        title_line = lines[0].strip()
        
        # Clean title markdown formatting
        title = re.sub(r"[\*`\[\]]", "", title_line)
        # Create a file-safe clean name
        clean_title = re.sub(r"[^a-zA-Z0-9_\-]", "_", title).strip("_")
        
        # Extract visual description
        visual_match = re.search(r"\[VISUAL:\s*(.*?)\]", raw, re.DOTALL | re.IGNORECASE)
        if not visual_match:
            # Fallback search for brackets in case label is different
            visual_match = re.search(r"\[(.*?)(?:child|hominin|figure|adult|people|hunter|calendar).*?\]", raw, re.DOTALL | re.IGNORECASE)
        
        visual = visual_match.group(1).strip() if visual_match else ""
        
        # Extract narration
        narration_match = re.search(r"NARRATOR\s*\(V\.O\.\):.*?>\s*(.*?)(?=\n\n|\n[A-Z]|\Z)", raw, re.DOTALL | re.IGNORECASE)
        if not narration_match:
            narration_match = re.search(r">\s*(.*?)(?=\n\n|\Z)", raw, re.DOTALL)
            
        narration = narration_match.group(1).strip() if narration_match else ""
        
        # Clean blockquotes and markdown
        narration = re.sub(r"^>\s*", "", narration, flags=re.MULTILINE)
        narration = re.sub(r"[\*`#]", "", narration)
        
        if visual or narration:
            scenes.append({
                "index": scene_index,
                "title": title,
                "clean_title": clean_title,
                "visual": visual,
                "narration": narration
            })
            scene_index += 1
            
    return scenes

def queue_prompt(prompt_workflow):
    data = json.dumps({"prompt": prompt_workflow}).encode('utf-8')
    req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def get_history(prompt_id):
    try:
        with urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}") as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {}

def download_file(filename, output_path):
    url = f"{COMFYUI_URL}/view?filename={urllib.parse.quote(filename)}&type=output"
    try:
        urllib.request.urlretrieve(url, output_path)
        return True
    except Exception as e:
        print(f"\nError downloading {filename}: {e}")
        return False

def wait_for_prompt(prompt_id):
    print(f"Queueing to ComfyUI (ID: {prompt_id}). Processing", end="", flush=True)
    while True:
        history = get_history(prompt_id)
        if prompt_id in history:
            print(" Done!")
            return history[prompt_id]
        print(".", end="", flush=True)
        time.sleep(3)

def run_scene(scene):
    print(f"\n==========================================")
    print(f"🎬 Scene {scene['index']}: {scene['title']}")
    print(f"==========================================")
    print(f"Visual: {scene['visual'][:100]}...")
    print(f"Narration: {scene['narration'][:100]}...")
    
    # Format prompt for Ollama Generate
    formatted_prompt = f"{SYSTEM_PROMPT}\n\nUser Script:\n[Visual: {scene['visual']}]\n[Narration: {scene['narration']}]"
    
    # Load base prompt graph
    workflow = get_base_prompt_workflow()
    
    # Update Ollama prompt
    workflow["2"]["inputs"]["prompt"] = formatted_prompt
    
    # Set seeds for randomness
    workflow["8"]["inputs"]["seed"] = random.randint(1, 1000000000)
    workflow["16"]["inputs"]["seed"] = random.randint(1, 1000000000)
    
    # Set output filename prefixes
    image_prefix = f"scene_{scene['index']}_{scene['clean_title']}_image"
    video_prefix = f"scene_{scene['index']}_{scene['clean_title']}_video"
    workflow["10"]["inputs"]["filename_prefix"] = image_prefix
    workflow["18"]["inputs"]["filename_prefix"] = video_prefix
    
    # Queue prompt
    response = queue_prompt(workflow)
    prompt_id = response["prompt_id"]
    
    # Wait for completion
    results = wait_for_prompt(prompt_id)
    
    # Download the generated assets
    print("Downloading finished assets...")
    downloaded_files = []
    
    # Save Image download
    image_outputs = results.get("outputs", {}).get("10", {}).get("images", [])
    for img in image_outputs:
        filename = img["filename"]
        local_path = os.path.join(OUTPUT_DIR, f"scene_{scene['index']}_{scene['clean_title']}.png")
        if download_file(filename, local_path):
            print(f" Saved Image: {local_path}")
            downloaded_files.append(local_path)
            
    # Video Combine download
    video_outputs = results.get("outputs", {}).get("18", {}).get("gifs", [])
    for vid in video_outputs:
        filename = vid["filename"]
        local_path = os.path.join(OUTPUT_DIR, f"scene_{scene['index']}_{scene['clean_title']}.mp4")
        if download_file(filename, local_path):
            print(f" Saved Video: {local_path}")
            downloaded_files.append(local_path)
            
    return downloaded_files

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_pipeline.py <script_file.md>")
        sys.exit(1)
        
    script_file = sys.argv[1]
    if not os.path.exists(script_file):
        print(f"Error: Script file '{script_file}' not found.")
        sys.exit(1)
        
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"Parsing script: {script_file}...")
    scenes = parse_script(script_file)
    print(f"Found {len(scenes)} scenes to generate.")
    
    for i, scene in enumerate(scenes):
        try:
            run_scene(scene)
        except Exception as e:
            print(f"\n❌ Error processing Scene {scene['index']}: {e}")
            print("Skipping to next scene...")
            
    print("\n🎉 Full script animation execution complete!")
    print(f"All saved assets are in the directory: {os.path.abspath(OUTPUT_DIR)}")

if __name__ == "__main__":
    import random
    main()
