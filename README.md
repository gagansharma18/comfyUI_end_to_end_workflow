# ComfyUI End-to-End Cartoon Storyboard Animator

An end-to-end local AI animation pipeline for producing character-consistent stickman animations from multi-scene storyboard scripts. This project combines **Z-Image-Turbo** (for fast, high-quality character-consistent starting frames) and **LTX-Video 2.3** (using motion distillation and alignment LoRAs to animate the frames).

---

## 📁 Repository Structure

* **`workflow.json`**: The complete, ready-to-run ComfyUI dual-stage animation workflow.
* **`stixx_stories_nodes.py`**: Custom ComfyUI nodes developed for this project:
  * `LoadTextFile`: Natively loads text or markdown story scripts from your ComfyUI input folder.
  * `StixxStoriesPromptBuilder`: Segregates system prompt templates, loaded scripts, and a target scene selector into a clean formatting node.
* **`episode_2.md`**: A full multi-scene script sample ("When Did We Start Being Afraid of the Dark?") to test the workflow.
* **`walkthrough.md`**: Complete, step-by-step setup guide for models, folders, and operations.
* **`implementation_plan.md`**: Architectural design blueprint for the dual-stage pipeline.
* **`task.md`**: Log of tasks accomplished during implementation.

---

## 🛠️ Setup Instructions

### 1. Install the Custom Nodes
Copy the custom node script from the repository into your local ComfyUI installation:
```bash
# Copy stixx_stories_nodes.py directly into your ComfyUI custom_nodes directory
copy stixx_stories_nodes.py C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\custom_nodes\
```
*Note: Make sure to also install `ComfyUI-LTXVideo`, `comfyui-ollama`, and `ComfyUI-VideoHelperSuite` custom node packs via the ComfyUI Manager.*

### 2. Copy the Script File
Place your script markdown file inside your ComfyUI shared input folder:
```bash
# Copy episode_2.md to the ComfyUI input directory
copy episode_2.md "C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Shared\input\"
```

### 3. Load Model Assets
Ensure the following files are downloaded and placed in your ComfyUI model directories (refer to `walkthrough.md` for details):
* **Stage 1 (Z-Image-Turbo)**:
  * `z_image_turbo_bf16.safetensors` (in `models/diffusion_models`)
  * `qwen_3_4b.safetensors` (in `models/text_encoders`)
  * `ae.safetensors` (in `models/vae`)
* **Stage 2 (LTX-Video 2.3)**:
  * `ltx-2.3-22b-dev-fp8.safetensors` (in `models/checkpoints`)
  * `gemma_3_12B_it_fp4_mixed.safetensors` (in `models/text_encoders`)
  * `ltx_2.3_22b_distilled_1.1_lora_dynamic_fro09_avg_rank_111_bf16.safetensors` (in `models/loras`)
  * `gemma-3-12b-it-abliterated_lora_rank64_bf16.safetensors` (in `models/loras`)

---

## 🎬 Running the Animator

1. Open Comfy-Desktop and drag-and-drop `workflow.json` onto the canvas.
2. In the **Load Text File 📄** node, select `episode_2.md` from the dropdown.
3. In the **Stixx Stories Prompt Builder 🛠️** node, edit the `target_scene` field to specify which scene to render:
   * E.g., set it to `Scene 1: THE MONSTER UNDER THE BED` or `Scene 2: ANCIENT PREDATORS OF THE PLEISTOCENE`.
4. Click **Queue Prompt**. 

The workflow will dynamically:
1. Parse the script file on disk to extract the visual details of the chosen target scene.
2. Direct the local Ollama LLM (Qwen 3.6) to build the visual starting frame prompt.
3. Generate the character-consistent widescreen image (Stage 1).
4. Mux the image into the LTX video latent, compile it with the LTX distill and alignment LoRAs at optimized parameters (CFG: 1.5, Steps: 12), and render the final animated video MP4!
