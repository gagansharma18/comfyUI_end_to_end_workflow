import os
import re
import folder_paths

class LoadTextFile:
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = []
        if os.path.exists(input_dir):
            files = [f for f in os.listdir(input_dir) if f.endswith('.txt') or f.endswith('.md')]
        return {
            "required": {
                "file": (sorted(files) if files else ["none"],),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "load_text"
    CATEGORY = "StixxStories"

    def load_text(self, file):
        if file == "none":
            return ("",)
        file_path = os.path.join(folder_paths.get_input_directory(), file)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return (content,)
        except Exception as e:
            return (f"Error loading file: {str(e)}",)

class StixxStoriesPromptBuilder:
    @classmethod
    def INPUT_TYPES(s):
        system_default = """System Prompt:
You are an AI storyboard designer for a cartoon series called "Stixx Stories".
Your job is to read the user's script (which may contain multiple scenes/episodes) and a final instruction indicating which specific scene, timestamp, or topic to focus on.
Generate a single detailed visual prompt describing the static starting frame of that requested scene.

Apply these character consistency guidelines:
- "Bob" is a simple stick figure with a large round white circular head, small black dot eyes, thin curved black eyebrows, and a simple line mouth. Bob has messy spikes of brown hair and wears a basic flat-colored blue t-shirt.
- "Alice" is a simple stick figure with a large round white circular head, small black dot eyes, thin curved black eyebrows, and a simple line mouth. Alice has long straight black hair and wears a basic flat-colored red dress.

Aesthetic Guidelines:
- Style: A stick figure animation in the style of an animated educational webcomic or YouTube explainer video. Thick hand-drawn wobbly black outlines, flat colors, clean minimalist background with a soft warm color palette (light beige and soft green). No 3D shading, no realism, no text, no watermarks, no speech bubbles.

Output exactly one paragraph of prompt describing the static starting frame. Do not output anything else."""
        
        return {
            "required": {
                "system_prompt": ("STRING", {"multiline": True, "default": system_default}),
                "story_script": ("STRING", {"forceInput": True}),
                "target_scene": ("STRING", {"default": "Scene 1: THE MONSTER UNDER THE BED"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "build_prompt"
    CATEGORY = "StixxStories"

    def build_prompt(self, system_prompt, story_script, target_scene):
        prompt = f"{system_prompt}\n\n---\nUser Script:\n{story_script}\n\n---\nTarget Scene to Generate:\n{target_scene}"
        return (prompt,)

class StixxStoriesScriptParser:
    @classmethod
    def INPUT_TYPES(s):
        system_default = """System Prompt:
You are an AI storyboard designer for a cartoon series called "Stixx Stories".
Your job is to read the user's script (narration and scene actions) and generate a single detailed visual prompt describing the static starting frame of the scene.

Apply these character consistency guidelines:
- "Bob" is a simple stick figure with a large round white circular head, small black dot eyes, thin curved black eyebrows, and a simple line mouth. Bob has messy spikes of brown hair and wears a basic flat-colored blue t-shirt.
- "Alice" is a simple stick figure with a large round white circular head, small black dot eyes, thin curved black eyebrows, and a simple line mouth. Alice has long straight black hair and wears a basic flat-colored red dress.

Aesthetic Guidelines:
- Style: A stick figure animation in the style of an animated educational webcomic or YouTube explainer video. Thick hand-drawn wobbly black outlines, flat colors, clean minimalist background with a soft warm color palette (light beige and soft green). No 3D shading, no realism, no text, no watermarks, no speech bubbles.

Read the user's script and output exactly one paragraph of prompt describing the static starting frame of the scene. Do not output anything else."""

        return {
            "required": {
                "story_script": ("STRING", {"forceInput": True}),
                "scene_index": ("INT", {"default": 1, "min": 1, "max": 1000, "step": 1, "control_after_generate": True}),
                "system_prompt": ("STRING", {"multiline": True, "default": system_default}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "INT", "STRING")
    RETURN_NAMES = ("prompt", "filename_prefix", "scene_title", "narration", "total_scenes", "scene_info")
    FUNCTION = "parse_and_build"
    CATEGORY = "StixxStories"

    def parse_and_build(self, story_script, scene_index, system_prompt):
        if not story_script.strip():
            return ("", "empty_scene", "No Script", "", 0, "No Script Loaded")

        # Split content by scene headers "## "
        scenes_raw = re.split(r"^##\s+", story_script, flags=re.MULTILINE)
        
        scenes = []
        parsed_index = 1
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
                    "index": parsed_index,
                    "title": title,
                    "clean_title": clean_title,
                    "visual": visual,
                    "narration": narration
                })
                parsed_index += 1
                
        total_scenes = len(scenes)
        if total_scenes == 0:
            return ("", "no_scenes_found", "No Scenes Found", "", 0, "No Scenes Found in Script")

        # Clamp scene_index to total_scenes
        target_idx = min(max(1, scene_index), total_scenes)
        scene = scenes[target_idx - 1]

        # Format prompt for Ollama
        formatted_prompt = f"{system_prompt}\n\nUser Script:\n[Visual: {scene['visual']}]\n[Narration: {scene['narration']}]"
        
        # Build filename prefix
        filename_prefix = f"scene_{scene['index']}_{scene['clean_title']}"
        scene_info = f"Scene {scene['index']} of {total_scenes}: {scene['title']}"

        return (formatted_prompt, filename_prefix, scene['title'], scene['narration'], total_scenes, scene_info)

NODE_CLASS_MAPPINGS = {
    "LoadTextFile": LoadTextFile,
    "StixxStoriesPromptBuilder": StixxStoriesPromptBuilder,
    "StixxStoriesScriptParser": StixxStoriesScriptParser,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadTextFile": "Load Text File 📄",
    "StixxStoriesPromptBuilder": "Stixx Stories Prompt Builder 🛠️",
    "StixxStoriesScriptParser": "Stixx Stories Script Parser 📋",
}

