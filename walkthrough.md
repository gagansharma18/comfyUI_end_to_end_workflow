# ComfyUI Stickman Animator (Z-Image-Turbo + LTX-2.3) - Walkthrough Guide

We have created the finalized [workflow.json](file:///c:/Users/gagan/stash/workflow/workflows/workflow.json) file in your project directory under `workflows/` (`c:\Users\gagan\stash\workflow\workflows\workflow.json`). This guide explains how to import and use it in Comfy-Desktop.

---

## 1. Local Model File Placements

Please place the required model files in your Comfy-Desktop directory structure:

### A. Stage 1: Z-Image-Turbo (Image Generation)
1. **Diffusion Model (`z_image_turbo_bf16.safetensors`)**:
   - Place in: `C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\models\diffusion_models\`
2. **Text Encoder (`qwen_3_4b.safetensors`)**:
   - Place in: `C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\models\text_encoders\`
3. **VAE (`ae.safetensors` - Flux 1 VAE)**:
   - Place in: `C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\models\vae\`

### B. Stage 2: LTX-Video 2.3 (Video Generation)
1. **LTX Checkpoint (`ltx-2.3-22b-dev-fp8.safetensors`)**:
   - Place in: `C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\models\checkpoints\`
2. **LTXV Audio Text Encoder (`gemma_3_12B_it_fp4_mixed.safetensors`)**:
   - Place in: `C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\models\text_encoders\`
3. **LTX Distill LoRA (`ltx_2.3_22b_distilled_1.1_lora_dynamic_fro09_avg_rank_111_bf16.safetensors`)**:
   - Place in: `C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\models\loras\`
4. **Gemma Text Encoder LoRA (`gemma-3-12b-it-abliterated_lora_rank64_bf16.safetensors`)**:
   - Place in: `C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\models\loras\`

---

## 2. Pre-Loaded Assets

To make the workflow immediately runnable:
- **Sample Script**: The Ollama LLM node has been pre-configured with a script about Bob finding a giant hovering banana.

---

## 3. Running the Workflow

1. **Load the Workflow**:
   - Drag and drop [workflow.json](file:///c:/Users/gagan/stash/workflow/workflows/workflow.json) directly into your Comfy-Desktop web canvas.
2. **Setup Loaders**:
   - **CLIPLoader (Node 20)**: Loads `qwen_3_4b.safetensors` with its type set to `lumina2` (as it's a Qwen-based Lumina-Next model text encoder).
   - **CheckpointLoaderSimple (Node 26)**: Loads `ltx-2.3-22b-dev-fp8.safetensors`.
   - **LTXV Audio Text Encoder Loader (Node 27)**: Loads `gemma_3_12B_it_fp4_mixed.safetensors` alongside `ltx-2.3-22b-dev-fp8.safetensors`. This loads the required LTX text encoder since the quantized FP8 checkpoint does not contain it.
3. **Upload and select script details**:
   - Save your script markdown (`.md`) or text (`.txt`) file directly inside your ComfyUI input folder:
     `C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Shared\input\`
     *(We have pre-saved `episode_2.md` there for you!)*
   - Locate the **Load Text File 📄** node (Node 28) and click Refresh in ComfyUI, then select your file name from the dropdown.
   - Locate the **Stixx Stories Prompt Builder 🛠️** node (Node 29). Type the name/index of the scene you want to generate in the `target_scene` text box (e.g., `Scene 1: THE MONSTER UNDER THE BED` or `Scene 2: ANCIENT PREDATORS OF THE PLEISTOCENE`).
4. **Queue generation**:
   - Click **Queue Prompt**.
   - **Stage 1 (Z-Image-Turbo)** will render the character-consistent starting frame image using optimal fast settings (9 steps, 1.0 CFG, Euler/Simple).
   - **Stage 2 (LTX-Video 2.3)** will inject the starting frame into the latent video space, load the FP8 model with sequential LoRAs applied, sample the motion, and output the final MP4/GIF video in the **Video Combine** node.
