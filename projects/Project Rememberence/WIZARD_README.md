# Character Creation Wizard - AIR-AI Oracle

## Overview

Guided 6-step character creation wizard that walks players through the "Six Gates" of spirit creation, providing interpretive commentary at each step.

## Features

✅ **Step-by-step guided creation:**
1. Animal Sign (12 choices)
2. Star Sign (12 choices)
3. Species (36 choices)
4. Type (24 choices)
5. Class (6 choices)
6. Skill (6 choices per class)

✅ **Interpretive commentary** for Animal and Star signs (e.g., "The Rat—clever, adaptable, a survivor...")

✅ **Real-time stat preview** after zodiac choices

✅ **Final confirmation** with full character sheet summary

✅ **Integration with existing save system** (uses `generator.js` save/load)

## Files Created

- `static/js/wizard.js` - Wizard logic and state management
- `create-spirit.html` - Wizard UI page
- `app.py` - New route `/create-spirit`
- `index.html` - Added "✧ Wizard" button to nav

## How It Works

1. **Player visits `/create-spirit`**
2. **Wizard guides through 6 gates:**
   - Each step shows choices with interpretive text
   - Click a choice to select it
   - Can go back to change previous choices
3. **Final step:**
   - Enter spirit name and description
   - Review full character sheet
   - Click "Create Spirit" to save
4. **Spirit saved to existing state system**
5. **Redirects to homepage**

## Data Flow

```
User choices → wizardState.choices
     ↓
calculateBiorhythms(animal, star) → biorhythms object
     ↓
generateThoughts(biorhythms) → thoughts object
     ↓
calculateStats(biorhythms, species, type, level) → stats object
     ↓
Build spirit object with all data
     ↓
saveSpirit(spirit) → POST /save-state
     ↓
Redirect to homepage
```

## Dependencies

Uses existing functions from `generator.js`:
- `calculateBiorhythms(animal, star)`
- `calculateStats(biorhythms, species, type, level)`
- `saveSpirit(spirit)` (new wrapper around apiSave)

## Next Steps

1. **Test the wizard** - Run Flask app, visit `/create-spirit`
2. **Add more interpretive text** for Species, Types, Classes, Skills
3. **Add visual flair** - Icons, animations, sound effects
4. **Connect to Oracle chat** - Let players ask the Oracle about their choices
5. **Add shadow encounter** - After creation, guide through first dream

## Testing

```bash
cd "D:\Cards\Project Rememberence\app"
python app.py
```

Then visit: `http://127.0.0.1:5000/create-spirit`

## CSS Styling

Wizard styles are auto-injected from `wizard.js`. Can be customized or moved to `styles.css`.

Key classes:
- `.wizard-step` - Main step container
- `.wizard-choice` - Individual choice cards
- `.interpretive` - Commentary text
- `.wizard-progress` - Step indicator at top
- `.stat-preview` - Stats grid on final step

## Extending Interpretive Text

Add more commentary in `wizard.js`:

```javascript
const interpretiveText = {
    animal: { ... },
    star: { ... },
    species: {
        'Avious': 'Your description here...',
        'Merr': '...'
    },
    type: {
        'Thunder': '...'
    }
};
```
