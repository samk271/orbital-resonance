# Orbital Resonance

**Orbital Resonance** is an audio sample generation and visualization tool that turns your sound library into a dynamic solar system. Generate AI-based audio samples, edit sequences like a MIDI editor, and watch your orchestra orbit the sun.

> ⚠️ **Note**: This program currently only has support for  **Windows**.

---

## 🛠 Installation

1. Clone the repository.
2. Navigate to the `resources` folder.
3. Run:

```bash
requirements.bat
```

---

## 🚀 Features

### 🎵 Sample Editor
- **AI Input**: Generate audio samples from text prompts.
- **Audio Display**: Visualize and crop generated audio.
- **Sample Settings**: Name your sample and adjust pitch.
- **File Handling**:
  - Load `.wav` files
  - Save samples (overwrite if name matches, or create a new one)
  - Playback samples

### 🪐 Sequence Editor
- Functions like a traditional MIDI editor.
- **Row**: Determines pitch.
- **Column**: Controls orbital offset and period.
- **Note Structure**:
  - Topmost selection = planet
  - Other selections = moons (up to `n - 1`)
- **Interactions**:
  - Right-click to change planet color
  - Click/drag to add/remove bars
  - Click to toggle bar on/off
  - Ctrl+Click: Focus with zoom
  - Shift+Click: Focus without zoom
- Planet plays sound and its moons when it reaches the top of its orbit.

### ☀️ Sun Settings
- Adjust the sun’s shape, size, and color.

### 📂 Sample List
- View all created/imported samples.
- Select, copy, delete, or adjust volume.
- Open associated editors by selecting a sample.

### 🌌 Planetary Display
- **Navigation Controls**:
  - 🐢 Slow down playback
  - 🐇 Speed up playback
  - ➕➖ Zoom in/out
  - ⬆⬇⬅➡ Move camera
  - 🏠 Center on sun
- **Menus**:
  - Toggle visibility with arrows
  - File operations: New, Open, Save, Save As, Undo, Redo
- **Interactions**:
  - Click: Focus planet
  - Ctrl+Click: Focus with zoom
  - Click+Drag or Arrow keys: Move view
  - Scroll: Zoom to mouse pointer
  - Focused zoom follows planet orbit

---

### ⌨️ Keybinds

| Action              | Key Combination         |
|---------------------|-------------------------|
| New File            | `Ctrl + N`              |
| Open File           | `Ctrl + O`              |
| Save                | `Ctrl + S`              |
| Save As             | `Ctrl + Shift + S`      |
| Undo                | `Ctrl + Z`              |
| Redo                | `Ctrl + Y`              |
| Zoom In             | `Ctrl + +`              |
| Zoom Out            | `Ctrl + -`              |
| Speed Up            | `Ctrl + Shift + +`      |
| Slow Down           | `Ctrl + Shift + -`      |

---

## 🎤 Using the AI Sample Generator

**Orbital Resonance** leverages the power of [`cvssp/audioldm2`](https://huggingface.co/cvssp/audioldm2) to generate audio samples directly from text prompts. This lets you create custom sounds without recording or downloading samples.

### ⚙️ How It Works

The AI model (`cvssp/audioldm2`) converts your written descriptions into `.wav` files using a powerful diffusion-based audio generation process. These samples can then be edited and sequenced within the app.

### 📝 How to Use

1. Open the **Sample Editor**.
2. Enter a descriptive **text prompt** in the AI Input field (e.g., _"deep synth bass with a rising tone"_).
3. Click **Generate**.
4. The AI will return a sample which you can:
   - Preview
   - Crop
   - Name
   - Adjust pitch and volume
   - Save to your sample library

> 💡 You can generate multiple variations by editing your prompt slightly or clicking Generate again with the same prompt.

### ✍️ Prompt Tips

To get the best results from the AI, try the following:

| Prompt Type         | Examples                                                                 |
|---------------------|--------------------------------------------------------------------------|
| Instruments         | `"solo violin"`, `"electric guitar strumming"`, `"ambient piano chords"` |
| Style + Instrument  | `"lo-fi hip-hop drum beat"`, `"orchestral brass hits"`                   |
| Ambience/Effects    | `"windy forest with bird chirps"`, `"sci-fi alert signal"`               |
| Actions/Changes     | `"rising synth arpeggio"`, `"descending bass line with distortion"`      |
| Emotions/Textures   | `"eerie ambient drone"`, `"bright shimmering bell tones"`                |

> 🎯 Be as specific as possible. Including **instrument, tone, effect, and motion** (e.g., rising, fading, pulsing) helps guide the model.

### 📌 Notes

- Generation may take a few seconds depending on your system specs.
- Internet access or a pre-downloaded model may be required.
- Generated files are stored temporarily until saved to your library.

> ⚠️ **Note**: The AI does not work for all GPUs in which case "blank" audio will be generated. If this occurs the user will need to use the CPU which is significantly slower.

---

## 📁 File Association

You can associate `.orbres` files with **Orbital Resonance** so that double-clicking them launches the app with the selected file.

### 📂 Required Folder Structure

```
C:\Project
│
├── orbital-resonance
│   ├── resources
│   │   └── file association
│   │       └── orbital resonance.bat
│   ├── src
│   │   └── main.py
│
├── venv
│   └── Scripts
│       └── activate.bat
```

1. Right-click any `.orbres` file.
2. Select **Open with...** → **More apps** → **Look for another app on this PC**.
3. Check the box for **Always use this app to open .orbres files**.
4. Navigate to the file:
```
orbital-resonance/resources/file association/orbital resonance.bat
```
5. Select the `.bat` file.

> ✅ From now on, opening a `.orbres` file will automatically launch **Orbital Resonance** with the file loaded.

---

## 💾 File Format

All projects in **Orbital Resonance** are saved as `.orbres` files.

### 📦 What’s Inside a `.orbres` File

Each `.orbres` file contains:

- 🎵 All generated or imported audio samples for that save
- 🪐 Sequence editor layout, including:
  - Moons and planets
  - Pitch, period and orbital offset data
- ⚙️ Sample metadata such as:
  - Volume
  - Pitch
  - Sample name

---

## Credit

A special thanks to the following royalty-free sample websites for providing the prebuilt samples included in this repo:

https://freewavesamples.com/

https://samplefocus.com/
