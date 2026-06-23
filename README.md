# ComfyUI End-to-End Cartoon Storyboard Animator

An end-to-end local AI animation pipeline for producing character-consistent stickman animations from multi-scene storyboard scripts. This project combines **Z-Image-Turbo** (for fast, high-quality character-consistent starting frames) and **LTX-Video 2.3** (using motion distillation and alignment LoRAs to animate the frames).

---

## 📁 Repository Structure

We have organized the files into standard ComfyUI folders to make copying and pasting them as straightforward as possible:

* **`custom_nodes/`**: Custom ComfyUI python scripts.
  * [stixx_stories_nodes.py](file:///c:/Users/gagan/stash/workflow/custom_nodes/stixx_stories_nodes.py): Custom nodes (`LoadTextFile`, `StixxStoriesPromptBuilder`) for script parsing and prompt compilation.
* **`input/`**: Script files to load inside ComfyUI.
  * [episode_2.md](file:///c:/Users/gagan/stash/workflow/input/episode_2.md): The full Episode 2 storyboard script.
  * [episode_2_sample.md](file:///c:/Users/gagan/stash/workflow/input/episode_2_sample.md): A truncated script sample for testing.
* **`workflows/`**: Packaged workflow JSON files.
  * [workflow.json](file:///c:/Users/gagan/stash/workflow/workflows/workflow.json): Ready-to-import ComfyUI dual-stage animation workflow.
* **`scripts/`**: Automation helper scripts.
  * [run_pipeline.py](file:///c:/Users/gagan/stash/workflow/scripts/run_pipeline.py): CLI tool to batch process multi-scene scripts programmatically.
* **`walkthrough.md`**: Complete, step-by-step setup guide for models, folders, and operations.
* **`implementation_plan.md`**: Architectural design blueprint for the dual-stage pipeline.
* **`task.md`**: Log of tasks accomplished during implementation.

---

## 🛠️ Setup Instructions

### 1. Install the Custom Nodes
Copy the custom node script from the repository's `custom_nodes` folder directly into your local ComfyUI installation:
```bash
# Copy custom nodes folder content directly into ComfyUI custom_nodes
copy custom_nodes\stixx_stories_nodes.py C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\custom_nodes\
```
*Note: Make sure to also install `ComfyUI-LTXVideo`, `comfyui-ollama`, and `ComfyUI-VideoHelperSuite` custom node packs via the ComfyUI Manager.*

### 2. Copy the Script Files
Place the script files from the repository's `input` folder inside your ComfyUI shared input folder:
```bash
# Copy script markdown files to the ComfyUI input directory
copy input\episode_2*.md "C:\Users\gagan\AppData\Local\Comfy-Desktop\ComfyUI-Shared\input\"
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

### Option A: Using the ComfyUI Web Interface (Recommended)
1. Open Comfy-Desktop and drag-and-drop `workflows/workflow.json` onto the canvas.
2. In the **Load Text File 📄** node, select `episode_2.md` from the dropdown.
3. In the **Stixx Stories Prompt Builder 🛠️** node, edit the `target_scene` field to specify which scene to render (e.g., `Scene 1: THE MONSTER UNDER THE BED` or `Scene 2: ANCIENT PREDATORS OF THE PLEISTOCENE`).
4. Click **Queue Prompt**.

### Option B: Batch Processing & Full Movie Concatenation (Recommended for full scripts)
To render all scenes from your script sequentially and automatically stitch them into a single movie:
1. Make sure ComfyUI is running in the background.
2. Double-click the [`run.bat`](file:///c:/Users/gagan/stash/workflow/run.bat) file in the root of the repository.
3. Hit **Enter** to accept the default script (`input/episode_2.md`) or type the path to a different markdown script file.
4. The runner will process each scene sequentially and output a final combined movie file to:
   [`output/final_storyboard.mp4`](file:///c:/Users/gagan/stash/workflow/output/final_storyboard.mp4) (perfect for adding voice-over overlays).

