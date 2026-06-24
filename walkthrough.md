# Cinematic AI Film Generator (Qwen-VL + Wan 2.2) - Walkthrough Guide

This guide explains how to configure and run the cinematic, shot-by-shot AI filmmaking pipeline. It uses **Qwen2.5-VL Image Edit** for consistent character scenes and **Wan 2.2 Image-to-Video** for animating the transitions between shots.

---

## 🛠️ Setup Instructions

### 1. Install ComfyUI Custom Nodes
Open the ComfyUI Manager in your browser and install the following node packs (or clone them into your local `custom_nodes/` directory):
1. **`Comfyui-QwenEditUtils`** (Provides `TextEncodeQwenImageEditPlus` and Qwen loading logic)
   - *GitHub*: `https://github.com/lrzjason/Comfyui-QwenEditUtils`
2. **`comfyui-kjnodes`** (Provides Set/Get nodes, ImageScaleToTotalPixels, ImageResizeKJv2)
   - *GitHub*: `https://github.com/kijai/comfyui-kjnodes`
3. **`rgthree-comfy`** (Provides Labels and Power Lora Loader)
   - *GitHub*: `https://github.com/rgthree/rgthree-comfy`
4. **`ComfyUI-WanVideoWrapper`** (Provides `WanVideoNAG` and `WanFirstLastFrameToVideo` nodes)
   - *GitHub*: `https://github.com/kijai/ComfyUI-WanVideoWrapper`
5. **`ComfyUI-Frame-Interpolation`** (Provides `FILM VFI` node for smooth transitions)
   - *GitHub*: `https://github.com/Fannovel16/ComfyUI-Frame-Interpolation`
6. **`ComfyUI-VideoHelperSuite`** (Provides `VHS_VideoCombine` node)
   - *GitHub*: `https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite`

---

## 📁 Local Model File Placements

Please place the required model files in your Comfy-Desktop directory structure:

### A. Stage 1: Scene Builder (Qwen-VL Image Edit)
1. **Qwen-VL GGUF Model (`Qwen-Image-Edit-2509-Q5_0.gguf`)**:
   - Place in: `C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\models\unet\gguf\` or `models/gguf/`
   - *Download link*: [HuggingFace GGUF](https://huggingface.co/QuantStack/Qwen-Image-Edit-2509-GGUF/tree/main)
2. **Qwen CLIP Text Encoder (`qwen_2.5_vl_7b_fp8_scaled.safetensors`)**:
   - Place in: `C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\models\clip\qwen\`
   - *Download link*: [HuggingFace CLIP](https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/tree/main/split_files/text_encoders)
3. **Qwen VAE (`qwen_image_vae.safetensors`)**:
   - Place in: `C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\models\vae\`
   - *Download link*: [HuggingFace VAE](https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/tree/main/split_files/vae)
4. **Scene Builder LoRAs**:
   - Place all in: `C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\models\loras\qwen\`
   - **`Qwen-Image-Lightning-4steps-V2.0.safetensors`**: [HuggingFace Lightning LoRA](https://huggingface.co/lightx2v/Qwen-Image-Lightning)
   - **`InSubject-0.5.safetensors`**: [HuggingFace InSubject LoRA](https://huggingface.co/peteromallet/Qwen-Image-Edit-InSubject)
   - **`qwen-boreal-general-discrete-low-rank.safetensors`**: [CivitAI Boring Reality LoRA](https://civitai.com/models/1927710)
   - **`next-scene_lora-v2-3000.safetensors`**: [HuggingFace Next Scene LoRA](https://huggingface.co/lovis93/next-scene-qwen-image-lora-2509)
   - **`qwen-studio-realism.safetensors`**: [CivitAI Studio Realism](https://civitai.com/models/1972643)
   - **`251018_MICKMUMPITZ_QWEN-EDIT_360_03.safetensors`**: (Already provided in `example_workflow/`)

### B. Stage 2: Wan 2.2 Img2Vid
1. **Wan 2.2 Diffusion Models**:
   - Place in: `C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\models\diffusion_models\wan\`
   - **`wan2.2_i2v_high_noise_14B_fp16.safetensors`**: [HuggingFace WanRepackaged](https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged)
   - **`wan2.2_i2v_low_noise_14B_fp16.safetensors`**: [HuggingFace WanRepackaged](https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged)
2. **Wan Text Encoder (`umt5_xxl_fp8_e4m3fn_scaled.safetensors`)**:
   - Place in: `C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\models\text_encoders\`
   - *Download link*: [HuggingFace TextEncoder](https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged)
3. **Wan VAE (`wan_2.1_vae.safetensors`)**:
   - Place in: `C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\models\vae\wan\`
   - *Download link*: [HuggingFace VAE](https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged)
4. **Wan LoRAs**:
   - Place in: `C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\models\loras\wan\`
   - **`wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors`**: [HuggingFace WanRepackaged LoRAs](https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged)
   - **`wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors`**: [HuggingFace WanRepackaged LoRAs](https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged)
5. **VFI Model (`film_net_fp32.pt`)**:
   - Place in: `C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\models\frame_interpolation\`

---

## 🎬 Running the Generator

### Option A: Using the Automated Runner (Recommended)
1. Ensure ComfyUI is running in the background.
2. Verify that your character reference images are placed at:
   - `input/characters/woman.jpg`
   - `input/characters/man.jpg`
3. Edit your storyboard script in `input/cinematic_script.md` to define prompts and narration.
4. Double-click the [`run.bat`](file:///c:/Users/gagan/stash/workflow/run.bat) file in the root of the repository.
5. Hit **Enter** to accept the default script `input/cinematic_script.md`, or type the path to a different script.
6. The runner will call ComfyUI API to generate shot keyframes, animate motion transitions, and compile the final stitched video to:
   - [`output/final_storyboard.mp4`](file:///c:/Users/gagan/stash/workflow/output/final_storyboard.mp4)

### Option B: Using the ComfyUI Web Canvas
You can load the templates directly into the ComfyUI web interface to iterate and tweak parameters visually:
1. Load **Scene Builder**: Drag-and-drop `workflows/scene_builder_workflow.json` onto the canvas.
2. Load **Img2Vid**: Drag-and-drop `workflows/img2vid_workflow.json` onto the canvas.
