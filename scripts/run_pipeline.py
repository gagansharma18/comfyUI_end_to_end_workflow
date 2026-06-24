#!/usr/bin/env python3
import os
import re
import sys
import json
import time
import shutil
import subprocess
import urllib.request
import urllib.parse

# Reconfigure stdout/stderr for UTF-8 to support console emojis on Windows
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Constants
COMFYUI_URL = "http://127.0.0.1:8188"
OUTPUT_DIR = "./output"

# Detect ComfyUI Input Folder paths
SHARED_INPUT_DIR = r"C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Shared\input"
LOCAL_INPUT_DIR = r"C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\input"

def get_comfyui_input_dir():
    if os.path.exists(SHARED_INPUT_DIR):
        return SHARED_INPUT_DIR
    elif os.path.exists(LOCAL_INPUT_DIR):
        return LOCAL_INPUT_DIR
    else:
        print("[WARNING] Could not locate ComfyUI input folder automatically.")
        return "./input"

def parse_cinematic_script(script_path):
    print(f"Parsing script: {script_path}...")
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract Environment Prompt
    env_match = re.search(r"## Environment\s*Prompt:\s*(.*?)(?=\n##|\Z)", content, re.DOTALL | re.IGNORECASE)
    env_prompt = env_match.group(1).strip() if env_match else ""
    # Remove newlines for a clean single-paragraph prompt
    env_prompt = re.sub(r"\s+", " ", env_prompt)

    # Extract Characters mapping
    char_section = re.search(r"## Characters\s*(.*?)(?=\n##|\Z)", content, re.DOTALL | re.IGNORECASE)
    characters = {}
    if char_section:
        lines = char_section.group(1).strip().split("\n")
        for line in lines:
            # Matches: - Character: Description. Path: filepath
            m = re.match(r"^[-*]\s*([^:]+):\s*(.*?)\.\s*Path:\s*(.*)$", line.strip())
            if m:
                char_name = m.group(1).strip()
                char_desc = m.group(2).strip()
                char_path = m.group(3).strip()
                characters[char_name] = {
                    "description": char_desc,
                    "path": char_path
                }

    # Extract Shots
    shots_raw = re.split(r"###\s+Shot\s+", content, flags=re.IGNORECASE)
    shots = []
    shot_index = 1
    for raw in shots_raw:
        if not raw.strip() or "Cinematic Storyboard" in raw:
            continue
        
        # Parse shot prompt and narration
        lines = raw.strip().split("\n")
        title = lines[0].strip()
        
        raw_body = "\n".join(lines[1:])
        prompt_match = re.search(r"Prompt:\s*(.*?)(?=\nNarration:|\n\n|\Z)", raw_body, re.DOTALL | re.IGNORECASE)
        prompt = prompt_match.group(1).strip() if prompt_match else ""
        prompt = re.sub(r"\s+", " ", prompt)

        narration_match = re.search(r"Narration:\s*(.*?)(?=\n\n|\Z)", raw_body, re.DOTALL | re.IGNORECASE)
        narration = narration_match.group(1).strip() if narration_match else ""
        narration = re.sub(r"\s+", " ", narration)

        shots.append({
            "index": shot_index,
            "title": title,
            "prompt": prompt,
            "narration": narration
        })
        shot_index += 1

    return {
        "environment": env_prompt,
        "characters": characters,
        "shots": shots
    }

def queue_prompt(prompt_workflow):
    data = json.dumps({"prompt": prompt_workflow}).encode('utf-8')
    req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def get_history(prompt_id):
    try:
        with urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}") as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception:
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

def run_scene_builder(workflow_template, env_prompt, char_images, shot, prev_scene_image=None):
    # Create copy of API workflow
    workflow = json.loads(json.dumps(workflow_template))
    
    # Configure shared input folder path
    comfy_input_dir = get_comfyui_input_dir()

    # 1. Update character references
    if len(char_images) >= 1:
        workflow["213"]["inputs"]["image"] = os.path.basename(char_images[0])
    if len(char_images) >= 2:
        workflow["1284"]["inputs"]["image"] = os.path.basename(char_images[1])
        
    # Generate random seeds
    import random
    seed_val = random.randint(1, 10**15)
    
    if shot["index"] == 1:
        print(f"\n--- Stage 1: Scene Builder (First Shot) ---")
        # Update Environment Background Prompt
        workflow["1546"]["inputs"]["prompt"] = env_prompt
        # Update Scene 1 visual prompt
        workflow["1199"]["inputs"]["prompt"] = shot["prompt"]
        
        # Set seeds
        workflow["1525"]["inputs"]["seed"] = seed_val
        workflow["1542"]["inputs"]["seed"] = random.randint(1, 10**15)
        workflow["1604"]["inputs"]["seed"] = random.randint(1, 10**15)
        
        # Set output filename
        image_prefix = f"scene_{shot['index']}_image"
        workflow["208"]["inputs"]["filename_prefix"] = image_prefix
        
        # Send target output node (208)
        response = queue_prompt(workflow)
        results = wait_for_prompt(response["prompt_id"])
        
        # Download output image
        image_outputs = results.get("outputs", {}).get("208", {}).get("images", [])
        if image_outputs:
            filename = image_outputs[0]["filename"]
            local_path = os.path.join(OUTPUT_DIR, f"scene_{shot['index']}.png")
            if download_file(filename, local_path):
                print(f" Saved Scene {shot['index']} Image: {local_path}")
                # Copy to ComfyUI input folder for use as reference in next shots
                shutil.copy(local_path, os.path.join(comfy_input_dir, f"scene_{shot['index']}.png"))
                return local_path
    else:
        print(f"\n--- Stage 1: Scene Builder (Shot {shot['index']}) ---")
        # Subsequent shots use next-scene_lora and reference the previous scene's image.
        if not prev_scene_image:
            print("[ERROR] Subsequent shots require a reference to the previous scene's image!")
            sys.exit(1)
            
        # Inject custom LoadImage node loading the previous scene's image
        workflow["9999"] = {
            "class_type": "LoadImage",
            "inputs": {
                "image": os.path.basename(prev_scene_image),
                "upload": "image"
            }
        }
        
        # Connect visual prompt node (1625) image1 to our loaded previous image
        workflow["1625"]["inputs"]["image1"] = ["9999", 0]
        workflow["1625"]["inputs"]["prompt"] = shot["prompt"]
        
        # Set seed
        workflow["1629"]["inputs"]["seed"] = seed_val
        
        # Set output filename
        image_prefix = f"scene_{shot['index']}_image"
        workflow["1613"]["inputs"]["filename_prefix"] = image_prefix
        
        # Send target output node (1613)
        response = queue_prompt(workflow)
        results = wait_for_prompt(response["prompt_id"])
        
        # Download output image
        image_outputs = results.get("outputs", {}).get("1613", {}).get("images", [])
        if image_outputs:
            filename = image_outputs[0]["filename"]
            local_path = os.path.join(OUTPUT_DIR, f"scene_{shot['index']}.png")
            if download_file(filename, local_path):
                print(f" Saved Scene {shot['index']} Image: {local_path}")
                # Copy to ComfyUI input folder for use as reference in next shots
                shutil.copy(local_path, os.path.join(comfy_input_dir, f"scene_{shot['index']}.png"))
                return local_path

    return None

def run_img2vid(workflow_template, start_img, end_img, index):
    print(f"\n--- Stage 2: Wan 2.2 Img2Vid (Shot {index} Transition) ---")
    workflow = json.loads(json.dumps(workflow_template))
    
    # Configure input images
    workflow["199"]["inputs"]["image"] = os.path.basename(start_img)
    workflow["204"]["inputs"]["image"] = os.path.basename(end_img)
    
    # Generate random seeds
    import random
    seed_val = random.randint(1, 10**15)
    workflow["168"]["inputs"]["noise_seed"] = seed_val
    workflow["169"]["inputs"]["noise_seed"] = seed_val
    
    # Configure output prefix
    clip_prefix = f"clip_{index}"
    workflow["194"]["inputs"]["filename_prefix"] = clip_prefix
    
    # Queue prompt
    response = queue_prompt(workflow)
    results = wait_for_prompt(response["prompt_id"])
    
    # Download output video
    video_outputs = results.get("outputs", {}).get("194", {}).get("gifs", [])
    if video_outputs:
        filename = video_outputs[0]["filename"]
        local_path = os.path.join(OUTPUT_DIR, f"clip_{index}.mp4")
        if download_file(filename, local_path):
            print(f" Saved Clip {index} Video: {local_path}")
            return local_path
            
    return None

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Cinematic AI Film Pipeline Runner")
    parser.add_argument("script_file", help="Path to the cinematic script markdown file")
    args = parser.parse_args()
    
    script_file = args.script_file
    if not os.path.exists(script_file):
        print(f"Error: Script file '{script_file}' not found.")
        sys.exit(1)
        
    # Check if ComfyUI is listening
    try:
        urllib.request.urlopen(COMFYUI_URL, timeout=3)
    except Exception:
        print(f"[ERROR] ComfyUI server is not running or accessible at {COMFYUI_URL}")
        print("Please launch ComfyUI and try again.")
        sys.exit(1)

    # Load workflows
    try:
        with open("workflows/scene_builder_api.json", "r", encoding="utf-8") as f:
            scene_builder_workflow = json.load(f)
        with open("workflows/img2vid_api.json", "r", encoding="utf-8") as f:
            img2vid_workflow = json.load(f)
    except FileNotFoundError as e:
        print(f"[ERROR] Required API workflow files not found: {e}")
        print("Ensure scene_builder_api.json and img2vid_api.json exist in workflows/")
        sys.exit(1)

    # Parse script
    script_data = parse_cinematic_script(script_file)
    env_prompt = script_data["environment"]
    characters = script_data["characters"]
    shots = script_data["shots"]
    
    print(f"\n==========================================")
    print(f"🎬 CINEMATIC AI FILMMAKING PIPELINE")
    print(f"==========================================")
    print(f"Environment: {env_prompt[:80]}...")
    print(f"Characters found: {list(characters.keys())}")
    print(f"Total shots parsed: {len(shots)}")
    print(f"==========================================\n")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    comfy_input_dir = get_comfyui_input_dir()
    os.makedirs(comfy_input_dir, exist_ok=True)

    # Copy character images to ComfyUI input folder
    char_images = []
    for char_name, char_info in characters.items():
        src_path = char_info["path"]
        if os.path.exists(src_path):
            dest_path = os.path.join(comfy_input_dir, os.path.basename(src_path))
            shutil.copy(src_path, dest_path)
            char_images.append(dest_path)
            print(f"Copied character '{char_name}' reference image to: {dest_path}")
        else:
            print(f"[WARNING] Character reference image '{src_path}' not found on disk.")

    # Stage 1: Generate keyframe images for all scenes
    scene_images = {}
    prev_image = None
    for shot in shots:
        scene_img = run_scene_builder(scene_builder_workflow, env_prompt, char_images, shot, prev_image)
        if scene_img:
            scene_images[shot["index"]] = scene_img
            prev_image = scene_img
        else:
            print(f"[ERROR] Failed to generate keyframe image for Shot {shot['index']}.")
            sys.exit(1)

    # Stage 2: Animate transitions between adjacent shots
    clip_videos = []
    num_shots = len(shots)
    for i in range(1, num_shots):
        start_img = scene_images[i]
        end_img = scene_images[i+1]
        clip_vid = run_img2vid(img2vid_workflow, start_img, end_img, i)
        if clip_vid:
            clip_videos.append(clip_vid)
            
    # Animate the final frame to itself to create a gentle ending shot
    if num_shots > 0:
        last_idx = num_shots
        last_img = scene_images[last_idx]
        clip_vid = run_img2vid(img2vid_workflow, last_img, last_img, last_idx)
        if clip_vid:
            clip_videos.append(clip_vid)

    # Stage 3: Merge clips together using ffmpeg
    if clip_videos:
        print(f"\n🎬 Stitching all {len(clip_videos)} scene videos into the final movie...")
        try:
            # Try to get ffmpeg path from imageio_ffmpeg
            try:
                import imageio_ffmpeg
                ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            except ImportError:
                ffmpeg_path = "ffmpeg"
                
            list_path = os.path.join(OUTPUT_DIR, "video_list.txt")
            with open(list_path, "w", encoding="utf-8") as f:
                for path in clip_videos:
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
            
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                print(f"\n🎉 SUCCESS! Combined cinematic movie saved to: {os.path.abspath(final_output_path)}")
            else:
                print(f"\n❌ Error combining videos: {result.stderr}")
                
            if os.path.exists(list_path):
                os.remove(list_path)
        except Exception as e:
            print(f"\n❌ Failed to combine videos: {e}")

if __name__ == "__main__":
    main()
