# Project Transition & Conversation Backup

This document serves as a permanent, portable backup of our active conversation and setup details (Session ID: `96acad3d-fc9e-44ca-b2a5-d238fc359ae8`). You can reference this file at any time after renaming the workspace directory.

---

## 📋 What We Have Done So Far

1. **Created Git Ignore rules**:
   * Created [`.gitignore`](file:///.gitignore) to exclude python caches, OS metadata, and generated pipeline outputs.
   * Updated it to ignore the `example_workflow/` folder containing the `251018_MICKMUMPITZ_QWEN-EDIT_360_03.safetensors` model checkpoint (approx. 295MB), preventing large binary files from clogging Git.
2. **Updated Git Remote Repository URL**:
   * Renamed the remote URL to the new path:
     `https://github.com/gagansharma18/Stixx_images_videos_workflow.git`
3. **Updated Documentation**:
   * Replaced the repository URL reference inside [`memory.md`](file:///memory.md).

---

## 🛠️ Step-by-Step Workspace Renaming Guide

To rename your project folder safely without losing this state:

1. **Close the IDE/Editor** to release all active file locks on the `workflow` folder.
2. **Rename the folder** using your terminal or File Explorer:
   * **Old Path**: `C:\Users\gagan\stash\workflow`
   * **New Path**: `C:\Users\gagan\stash\Stixx_images_videos_workflow`
3. **Reopen the folder** in your IDE.
4. **Accessing this conversation history**:
   * The actual chat data is stored globally outside the project directory in your user directory:
     `C:\Users\gagan\.gemini\antigravity-ide\brain\96acad3d-fc9e-44ca-b2a5-d238fc359ae8\`
   * When you open the renamed folder in the IDE, you can view your conversation history menu to resume, or reference this backup file directly.

---

## 🎬 How to Run the Pipeline

Once you have renamed the folder, you can run the generator using:

### Option A: Automated CLI (Recommended)
1. Ensure ComfyUI is running in the background.
2. Run the Windows batch file [`run.bat`](file:///run.bat) by double-clicking it.
3. Accept the default script `input/episode_2.md` or type a custom script path.
4. The pipeline will process all scenes, save individual assets to `output/`, and stitch them together into `output/final_storyboard.mp4`.

### Option B: ComfyUI Web GUI
1. Load [`workflows/workflow.json`](file:///workflows/workflow.json) into ComfyUI.
2. Select `episode_2.md` inside **Load Text File 📄**.
3. Set `scene_index` to `1` and set its control to `increment` on the parser node.
4. Set the **Batch Count** to the number of scenes and click **Queue Prompt**.
