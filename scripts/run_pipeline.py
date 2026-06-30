#!/usr/bin/env python3
import re
import os
import sys
import json
import time
import uuid
import random
import urllib.request
import urllib.parse

# Reconfigure stdout/stderr for UTF-8 to support console emojis on Windows
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

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
                "strength": 0.7,
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
    
    visual_items = []
    global_index = 1
    
    for raw in scenes_raw:
        if not raw.strip():
            continue
        
        # Extract title (first line)
        lines = raw.strip().split("\n")
        title_line = lines[0].strip()
        
        # Clean title markdown formatting
        title = re.sub(r"[\*`\[\]]", "", title_line)
        
        # Extract parent narration
        narration_match = re.search(r"NARRATOR\s*\(V\.O\.\):.*?>\s*(.*?)(?=\n\n|\n[A-Z]|\Z)", raw, re.DOTALL | re.IGNORECASE)
        if not narration_match:
            narration_match = re.search(r">\s*(.*?)(?=\n\n|\Z)", raw, re.DOTALL)
            
        narration = narration_match.group(1).strip() if narration_match else ""
        
        # Clean blockquotes and markdown
        narration = re.sub(r"^>\s*", "", narration, flags=re.MULTILINE)
        narration = re.sub(r"[\*`#]", "", narration)
        
        # Find all visuals in this section
        matches = list(re.finditer(r"\[VISUAL(?:\s*@\s*(\d+:\d+))?:\s*(.*?)\]", raw, re.DOTALL | re.IGNORECASE))
        if not matches:
            # Fallback search for brackets in case label is different
            matches = list(re.finditer(r"\[(.*?)(?:child|hominin|figure|adult|people|hunter|calendar).*?\]", raw, re.DOTALL | re.IGNORECASE))
            
        for match in matches:
            if match.lastindex and match.lastindex >= 2:
                timestamp = match.group(1) or "0_00"
                visual_text = match.group(2).strip()
            else:
                timestamp = "0_00"
                visual_text = match.group(1).strip()
                
            # Create a file-safe clean name
            clean_title = re.sub(r"[^a-zA-Z0-9_\-]", "_", title).strip("_")
            clean_timestamp = timestamp.replace(":", "_")
            
            visual_items.append({
                "index": global_index,
                "title": f"{title} - @ {timestamp}",
                "clean_title": f"{clean_title}_{clean_timestamp}",
                "visual": visual_text,
                "narration": narration,
                "timestamp": timestamp
            })
            global_index += 1
            
    return visual_items

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

def upload_image(file_path):
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    filename = os.path.basename(file_path)
    
    with open(file_path, "rb") as f:
        file_content = f.read()
        
    part_headers = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
        f"Content-Type: image/png\r\n\r\n"
    )
    payload = part_headers.encode('utf-8') + file_content + f"\r\n--{boundary}--\r\n".encode('utf-8')
    
    req = urllib.request.Request(
        f"{COMFYUI_URL}/upload/image",
        data=payload,
        headers={
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Content-Length': str(len(payload))
        }
    )
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data.get("name", filename)
    except Exception as e:
        print(f"\nError uploading image to ComfyUI: {e}")
        return filename

def wait_for_prompt(prompt_id):
    print(f"Queueing to ComfyUI (ID: {prompt_id}). Processing", end="", flush=True)
    while True:
        history = get_history(prompt_id)
        if prompt_id in history:
            print(" Done!")
            return history[prompt_id]
        print(".", end="", flush=True)
        time.sleep(3)

def run_stage1(scene):
    print(f"\n==========================================")
    print(f"🎬 Scene {scene['index']}: {scene['title']} (Stage 1)")
    print(f"==========================================")
    print(f"Visual: {scene['visual'][:100]}...")
    print(f"Narration: {scene['narration'][:100]}...")
    
    # Format prompt for Ollama Generate
    formatted_prompt = f"{SYSTEM_PROMPT}\n\nUser Script:\n[Visual: {scene['visual']}]\n[Narration: {scene['narration']}]"
    
    # Load base prompt graph
    workflow = get_base_prompt_workflow()
    
    # Filter for Stage 1 nodes only
    stage1_nodes = ["1", "20", "21", "30", "2", "3", "6", "7", "8", "9", "10"]
    workflow_stage1 = {k: v for k, v in workflow.items() if k in stage1_nodes}
    
    # Update Ollama prompt
    workflow_stage1["2"]["inputs"]["prompt"] = formatted_prompt
    
    # Set seed for Stage 1 randomness
    workflow_stage1["8"]["inputs"]["seed"] = random.randint(1, 1000000000)
    
    # Set output filename prefix
    image_prefix = f"scene_{scene['index']}_{scene['clean_title']}_image"
    workflow_stage1["10"]["inputs"]["filename_prefix"] = image_prefix
    
    # Queue Stage 1 prompt
    print(">>> Running Stage 1: Image Generation")
    response = queue_prompt(workflow_stage1)
    prompt_id = response["prompt_id"]
    
    # Wait for completion
    results = wait_for_prompt(prompt_id)
    
    # Download the generated image
    image_outputs = results.get("outputs", {}).get("10", {}).get("images", [])
    local_image_path = None
    
    for img in image_outputs:
        filename = img["filename"]
        local_image_path = os.path.join(OUTPUT_DIR, f"scene_{scene['index']}_{scene['clean_title']}.png")
        if download_file(filename, local_image_path):
            print(f" Saved Image: {local_image_path}")
            break
            
    if not local_image_path or not os.path.exists(local_image_path):
        print("❌ Error: Stage 1 image generation failed or could not be downloaded.")
        return None
        
    # Get the text prompt generated by Ollama
    ollama_outputs = results.get("outputs", {}).get("2", {})
    prompt_text = ""
    if "text" in ollama_outputs:
        if isinstance(ollama_outputs["text"], list) and len(ollama_outputs["text"]) > 0:
            prompt_text = ollama_outputs["text"][0]
        elif isinstance(ollama_outputs["text"], str):
            prompt_text = ollama_outputs["text"]
            
    # Fallback if Ollama output not found
    if not prompt_text:
        print("Warning: Could not retrieve generated text prompt from Ollama. Using visual description as fallback.")
        prompt_text = scene['visual']
    else:
        print(f"Generated Visual Prompt: {prompt_text[:120]}...")
        
    return {
        "local_image_path": local_image_path,
        "prompt_text": prompt_text
    }

def run_stage2(scene, local_image_path, prompt_text):
    print(f"\n==========================================")
    print(f"🎬 Scene {scene['index']}: {scene['title']} (Stage 2)")
    print(f"==========================================")
    
    # Stage 2: Video Generation
    print(">>> Running Stage 2: Video Generation")
    
    # Upload the image back to ComfyUI input folder
    print("Uploading image to ComfyUI...")
    comfyui_image_name = upload_image(local_image_path)
    
    # Load base prompt graph
    workflow = get_base_prompt_workflow()
    
    # Filter for Stage 2 nodes only
    stage2_nodes = ["26", "27", "24", "25", "22", "23", "13", "14", "15", "16", "17", "18"]
    workflow_stage2 = {k: v for k, v in workflow.items() if k in stage2_nodes}
    
    # Replace connection to Ollama text with actual string
    workflow_stage2["22"]["inputs"]["text"] = prompt_text
    
    # Add LoadImage node (Node 99)
    workflow_stage2["99"] = {
        "class_type": "LoadImage",
        "inputs": {
            "image": comfyui_image_name
        }
    }
    
    # Connect Node 15 to Node 99
    workflow_stage2["15"]["inputs"]["image"] = ["99", 0]
    
    # Set seed for Stage 2 randomness
    workflow_stage2["16"]["inputs"]["seed"] = random.randint(1, 1000000000)
    
    # Set output filename prefix
    video_prefix = f"scene_{scene['index']}_{scene['clean_title']}_video"
    workflow_stage2["18"]["inputs"]["filename_prefix"] = video_prefix
    
    # Queue Stage 2 prompt
    response = queue_prompt(workflow_stage2)
    prompt_id = response["prompt_id"]
    
    # Wait for completion
    results = wait_for_prompt(prompt_id)
    
    # Download the generated video
    downloaded_files = []
    video_outputs = results.get("outputs", {}).get("18", {}).get("gifs", [])
    for vid in video_outputs:
        filename = vid["filename"]
        local_video_path = os.path.join(OUTPUT_DIR, f"scene_{scene['index']}_{scene['clean_title']}.mp4")
        if download_file(filename, local_video_path):
            print(f" Saved Video: {local_video_path}")
            downloaded_files.append(local_video_path)
            
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
    
    # Stage 1: Generate all images first
    print("\n==========================================")
    print("🚀 STARTING STAGE 1: IMAGE GENERATION FOR ALL SCENES")
    print("==========================================")
    
    stage1_results = {}
    for scene in scenes:
        try:
            result = run_stage1(scene)
            if result:
                stage1_results[scene['index']] = result
        except Exception as e:
            print(f"\n❌ Error processing Stage 1 for Scene {scene['index']}: {e}")
            
    if not stage1_results:
        print("\n❌ No Stage 1 images were generated successfully. Exiting.")
        sys.exit(1)
        
    # Prompt user once to proceed to Stage 2 for all scenes
    user_choice = ""
    while user_choice not in ["y", "yes", "n", "no"]:
        user_choice = input(f"\nAll Stage 1 images generated successfully ({len(stage1_results)}/{len(scenes)}). Do you want to proceed with Stage 2 (Video Animation) for all scenes? (y/n) [default: y]: ").strip().lower()
        if user_choice == "":
            user_choice = "y"
            
    if user_choice in ["n", "no"]:
        print("\nSkipping Stage 2 for all scenes. Exiting.")
        sys.exit(0)
        
    # Stage 2: Generate all animations
    print("\n==========================================")
    print("🚀 STARTING STAGE 2: VIDEO ANIMATION FOR ALL SCENES")
    print("==========================================")
    
    video_paths = []
    for scene in scenes:
        idx = scene['index']
        if idx not in stage1_results:
            print(f"\nSkipping Scene {idx} because Stage 1 failed.")
            continue
            
        try:
            result = stage1_results[idx]
            downloaded = run_stage2(scene, result['local_image_path'], result['prompt_text'])
            for path in downloaded:
                if path.endswith(".mp4"):
                    video_paths.append(path)
        except Exception as e:
            print(f"\n❌ Error processing Stage 2 for Scene {idx}: {e}")
            print("Skipping to next scene...")
            
    print("\n🎉 Full script animation execution complete!")
    print(f"All saved individual assets are in the directory: {os.path.abspath(OUTPUT_DIR)}")

    if len(video_paths) > 1:
        print("\n🎬 Concatenating all generated scenes into a final movie...")
        try:
            import subprocess
            # Try to get ffmpeg path from imageio_ffmpeg
            try:
                import imageio_ffmpeg
                ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            except ImportError:
                ffmpeg_path = "ffmpeg"
                
            # Write files list
            list_path = os.path.join(OUTPUT_DIR, "video_list.txt")
            with open(list_path, "w", encoding="utf-8") as f:
                for path in video_paths:
                    abs_path = os.path.abspath(path).replace("\\", "/")
                    f.write(f"file '{abs_path}'\n")
            
            final_output_path = os.path.join(OUTPUT_DIR, "final_storyboard.mp4")
            cmd = [
                ffmpeg_path,
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", list_path,
                "-c", "copy",
                final_output_path
            ]
            
            # Execute ffmpeg command
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                print(f"🎉 Success! Combined video saved to: {os.path.abspath(final_output_path)}")
            else:
                print(f"❌ Error combining videos: {result.stderr}")
                
            # Clean up text file
            if os.path.exists(list_path):
                os.remove(list_path)
                
        except Exception as combine_err:
            print(f"❌ Failed to combine videos: {combine_err}")

if __name__ == "__main__":
    main()
