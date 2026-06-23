import os
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

NODE_CLASS_MAPPINGS = {
    "LoadTextFile": LoadTextFile,
    "StixxStoriesPromptBuilder": StixxStoriesPromptBuilder,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadTextFile": "Load Text File 📄",
    "StixxStoriesPromptBuilder": "Stixx Stories Prompt Builder 🛠️",
}
