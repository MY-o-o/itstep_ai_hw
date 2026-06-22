# AI Image Generation

A small project comparing text-to-image results for the same character prompt across local Stable Diffusion models and cloud AI tools.

## Concept

**Dr Elara Voss** — a time surgeon in a 1920s alternate-history steampunk setting: androgynous, one emerald and one milky blind eye, glowing blue biomechanical scar tattoos, vintage surgeon coat with clockwork details, Victorian operating theater with floating pocket watches.

## Project structure

```
prompt/
  prompt.txt       # Positive prompt
  neg_prompt.txt   # Negative prompt (quality and style exclusions)
results/
  local(dreamshaper).png
  local(JuggernautXL).png
  local(realisticVision).png
  Gemini.png
  ChatGPT.png
```

## Usage

1. Copy the prompts from `prompt/prompt.txt` and `prompt/neg_prompt.txt`.
2. Generate an image with your chosen model or service.
3. Save the output in `results/` using a clear filename (model or tool name).

## Models compared

| Source | Model / tool |
|--------|----------------|
| Local  | DreamShaper, Juggernaut XL, Realistic Vision |
| Cloud  | Google Gemini, ChatGPT |
