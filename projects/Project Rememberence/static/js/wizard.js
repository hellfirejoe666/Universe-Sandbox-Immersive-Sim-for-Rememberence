// Character Creation Wizard for AIR-AI Oracle
// Guided 6-step spirit creation with interpretive commentary

let wizardState = {
    step: 0,
    choices: {
        animal: null,
        star: null,
        species: null,
        type: null,
        class: null,
        skill: null
    },
    preview: null
};

const wizardSteps = [
    {
        id: 'animal',
        title: 'The First Gate - Animal Signs',
        instruction: 'Twelve animal signs float before you in the deep dark space. Which calls to your spirit?',
        dataKey: 'animalSigns',
        choices: ['Rat', 'Ox', 'Tiger', 'Rabbit', 'Dragon', 'Snake', 'Horse', 'Goat', 'Monkey', 'Rooster', 'Dog', 'Boar'],
        loreFile: '0-Animal Signs.txt'
    },
    {
        id: 'star',
        title: 'The Second Gate - Star Signs',
        instruction: 'The door opens into emptiness reflecting your chosen sign. Now, constellations obscure the next door. Which draws you?',
        dataKey: 'starSigns',
        choices: ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'],
        loreFile: '0-Star Signs.txt'
    },
    {
        id: 'species',
        title: 'The Third Gate - Species',
        instruction: 'Worlds and cities take shape around you. Thirty-six spirits call from the depths. Which essence will you embody?',
        dataKey: 'species',
        choices: null, // Will be populated from JSON
        loreFile: '0-Species.txt'
    },
    {
        id: 'type',
        title: 'The Fourth Gate - Type',
        instruction: 'Another door, more solid than your surroundings. Twenty-four runes of the immaterial aspects await. What is your nature?',
        dataKey: 'types',
        choices: null, // Will be populated from JSON
        loreFile: '0-Types.txt'
    },
    {
        id: 'class',
        title: 'The Fifth Gate - Class',
        instruction: 'Memories of a lost youth fill your mind. Hints of classes and skills burned into your consciousness. What path will you walk?',
        dataKey: 'classes',
        choices: ['Melee', 'Ranged', 'Magic', 'Step', 'Special', 'Trance'],
        loreFile: 'Classes.txt'
    },
    {
        id: 'skill',
        title: 'The Sixth Gate - Skill',
        instruction: 'Learning of fists and feet, blades and chains, stones and bows, spells and sorcery. Which skill defines you?',
        dataKey: null, // Dynamic based on class
        choices: null, // Will be populated based on class choice
        loreFile: null // Dynamic
    }
];

const classSkills = {
    'Melee': ['1H', '2H', 'Whip', 'Staff', 'Fists', 'Chi'],
    'Ranged': ['Thrown', 'Bow', 'Crossbow', 'Shotgun', 'Pistol', 'Rifle'],
    'Magic': ['Earth', 'Air', 'Fire', 'Water', 'Light', 'Dark'],
    'Step': ['Flight', 'Float', 'Dash', 'Acrobat', 'Warp', 'Evade'],
    'Special': ['White', 'Blue', 'Black', 'Red', 'Green', 'None'],
    'Trance': ['Overdrive', 'Stages', 'Duration', 'Aura', 'Armor', 'Morph']
};

const classLore = {
    'Melee': 'Learning of fists and feet, blades and chains, to defend yourself at close range.',
    'Ranged': 'Of stones and bows or explosive barrels, to ward off distant threats and hunt for meet.',
    'Magic': 'Of spells and sorcery, to enlighten your mind, and commune with your nature.',
    'Step': 'To walk without walking, and take flight to distant shores.',
    'Special': 'Of special traits, inherent gifts, and deeper powers.',
    'Trance': 'Of how to unleash your Spirit from within, and endure to the very last breath.'
};

// Interpretive commentary for each choice
const interpretiveText = {
    animal: {
        'Rat': 'The Rat—clever, adaptable, a survivor. You navigate the unseen paths, finding opportunity where others see only walls.',
        'Ox': 'The Ox—steadfast, strong, unwavering. You are the foundation upon which others build, the quiet strength that endures.',
        'Tiger': 'The Tiger—fierce, passionate, untamed. You are the storm that clears the old growth, making way for new life.',
        'Rabbit': 'The Rabbit—gentle, quick, intuitive. You move through the world with grace, sensing danger before it strikes.',
        'Dragon': 'The Dragon—majestic, powerful, mythical. You carry the fire of creation, the potential to reshape worlds.',
        'Snake': 'The Snake—wise, transformative, mysterious. You shed old skins, emerging renewed with each trial.',
        'Horse': 'The Horse—free, swift, noble. You are the wind beneath your own wings, bound to no master but your own spirit.',
        'Goat': 'The Goat—sure-footed, determined, resilient. You climb where others cannot, reaching heights unseen.',
        'Monkey': 'The Monkey—clever, curious, mischievous. You find joy in puzzles, wisdom in play, and truth in laughter.',
        'Rooster': 'The Rooster—proud, precise, vigilant. You are the herald of dawn, calling others to awaken.',
        'Dog': 'The Dog—loyal, honest, protective. You are the guardian of truth, the companion who never abandons.',
        'Boar': 'The Boar—courageous, direct, unyielding. You charge through obstacles, trusting in your own strength.'
    },
    star: {
        'Aries': 'Aries—the pioneer, the warrior. You are the first spark, the courage to begin.',
        'Taurus': 'Taurus—the builder, the steward. You are the earth that endures, the beauty that persists.',
        'Gemini': 'Gemini—the messenger, the seeker. You are the bridge between worlds, the voice of duality.',
        'Cancer': 'Cancer—the nurturer, the protector. You are the tide that pulls hearts home, the shell that shields.',
        'Leo': 'Leo—the sovereign, the creator. You are the sun around which others orbit, the fire that inspires.',
        'Virgo': 'Virgo—the healer, the artisan. You are the hand that refines, the mind that perfects.',
        'Libra': 'Libra—the harmonizer, the diplomat. You are the scale that balances, the grace that unites.',
        'Scorpio': 'Scorpio—the transformer, the mystic. You are the death that births renewal, the depth that reveals.',
        'Sagittarius': 'Sagittarius—the explorer, the philosopher. You are the arrow that seeks truth, the horizon that calls.',
        'Capricorn': 'Capricorn—the architect, the sage. You are the mountain that stands eternal, the wisdom of ages.',
        'Aquarius': 'Aquarius—the visionary, the rebel. You are the lightning of innovation, the future made present.',
        'Pisces': 'Pisces—the dreamer, the martyr. You are the ocean that holds all memories, the sacrifice that saves.'
    }
};

// Initialize wizard
window.initWizard = function initWizard() {
    wizardState.step = 0;
    wizardState.choices = { animal: null, star: null, species: null, type: null, class: null, skill: null };
    wizardState.preview = null;
    renderWizardStep();
};

// Render current wizard step
function renderWizardStep() {
    const container = document.getElementById('wizard-container');
    if (!container) {
        console.error('Wizard container not found');
        return;
    }

    const step = wizardSteps[wizardState.step];
    const isLastStep = wizardState.step === wizardSteps.length - 1;

    let choicesHtml = '';
    
    if (step.id === 'skill') {
        // Dynamic skills based on class choice
        const selectedClass = wizardState.choices.class;
        if (!selectedClass || !classSkills[selectedClass]) {
            container.innerHTML = '<p class="error">Please go back and select a class first.</p>';
            return;
        }
        step.choices = classSkills[selectedClass];
        step.loreFile = `${selectedClass}.txt`;
    }

    step.choices.forEach(choice => {
        const interpretive = getInterpretiveText(step.id, choice);
        choicesHtml += `
            <div class="wizard-choice" onclick="window.selectWizardChoice('${choice}')">
                <h3>${choice}</h3>
                ${interpretive ? `<p class="interpretive">${interpretive}</p>` : ''}
            </div>
        `;
    });

    container.innerHTML = `
        <div class="wizard-step">
            <h2>${step.title}</h2>
            <p class="instruction">${step.instruction}</p>
            <div class="choices-grid">
                ${choicesHtml}
            </div>
            <div class="wizard-nav">
                ${wizardState.step > 0 ? '<button onclick="window.prevWizardStep()">← Back</button>' : ''}
            </div>
        </div>
    `;
}

// Get interpretive text for a choice
function getInterpretiveText(stepId, choice) {
    if (stepId === 'animal' && interpretiveText.animal[choice]) {
        return interpretiveText.animal[choice];
    }
    if (stepId === 'star' && interpretiveText.star[choice]) {
        return interpretiveText.star[choice];
    }
    // For species, type, class, skill - will load from JSON/lore files
    return null;
}

// Handle choice selection
window.selectWizardChoice = async function selectWizardChoice(choice) {
    const step = wizardSteps[wizardState.step];
    wizardState.choices[step.id] = choice;

    // Update preview after each choice
    updatePreview();

    // Move to next step or finish
    if (wizardState.step < wizardSteps.length - 1) {
        wizardState.step++;
        renderWizardStep();
    } else {
        // Final step - show confirmation
        showWizardConfirmation();
    }
};

// Update stat preview
function updatePreview() {
    const { animal, star, species, type } = wizardState.choices;
    
    if (!animal || !star) {
        wizardState.preview = null;
        return;
    }

    // Calculate biorhythms
    const bios = window.calculateBiorhythms ? window.calculateBiorhythms(animal, star) : null;
    
    if (!bios) {
        wizardState.preview = null;
        return;
    }

    // Calculate thoughts
    const thoughts = window.generateThoughts ? window.generateThoughts(bios) : null;

    wizardState.preview = {
        biorhythms: bios,
        thoughts: thoughts,
        species: species,
        type: type
    };
}

// Show final confirmation
function showWizardConfirmation() {
    const container = document.getElementById('wizard-container');
    const { animal, star, species, type, class: className, skill } = wizardState.choices;
    const preview = wizardState.preview;

    let statsHtml = '';
    if (preview && species && type) {
        const stats = window.calculateStats ? window.calculateStats(preview.biorhythms, species, type, 1) : null;
        if (stats) {
            statsHtml = `
                <div class="stat-preview">
                    <h3>Spirit Stats (Level 1)</h3>
                    <div class="stats-grid">
                        <div>HP: ${stats.HP}</div>
                        <div>ATK: ${stats.ATK}</div>
                        <div>DEF: ${stats.DEF}</div>
                        <div>SPD: ${stats.SPD}</div>
                        <div>MP: ${stats.MP}</div>
                    </div>
                </div>
            `;
        }
    }

    container.innerHTML = `
        <div class="wizard-confirm">
            <h2>Your Spirit Takes Form</h2>
            <div class="spirit-summary">
                <p><strong>Animal Sign:</strong> ${animal}</p>
                <p><strong>Star Sign:</strong> ${star}</p>
                <p><strong>Species:</strong> ${species}</p>
                <p><strong>Type:</strong> ${type}</p>
                <p><strong>Class:</strong> ${className}</p>
                <p><strong>Skill:</strong> ${skill}</p>
                ${statsHtml}
            </div>
            <p class="final-instruction">As if awakening from a deep slumber, you are now greeted by your own spirit, and their world, of your own design. Give your spirit a name, and a short description.</p>
            <input type="text" id="spirit-name" placeholder="Spirit Name" class="wizard-input" />
            <textarea id="spirit-description" placeholder="Short description..." class="wizard-input" rows="3"></textarea>
            <div class="wizard-nav">
                <button onclick="window.prevWizardStep()">← Back</button>
                <button onclick="window.completeWizard()" class="primary">Create Spirit →</button>
            </div>
        </div>
    `;
}

// Go back a step
window.prevWizardStep = function prevWizardStep() {
    if (wizardState.step > 0) {
        wizardState.step--;
        renderWizardStep();
    }
};

// Complete wizard and save spirit
window.completeWizard = async function completeWizard() {
    const nameInput = document.getElementById('spirit-name');
    const descInput = document.getElementById('spirit-description');
    
    const name = nameInput.value.trim();
    const description = descInput.value.trim();

    if (!name) {
        alert('Please give your spirit a name.');
        return;
    }

    const { animal, star, species, type, class: className, skill } = wizardState.choices;
    const preview = wizardState.preview;

    // Build spirit object
    const spirit = {
        name: name,
        description: description,
        animal: animal,
        star: star,
        species: species,
        type: type,
        class: className,
        skill: skill,
        createdAt: Date.now(),
        level: 1
    };

    // Add biorhythms and thoughts if available
    if (preview) {
        spirit.biorhythms = preview.biorhythms;
        spirit.thoughts = preview.thoughts;
    }

    // Calculate final stats if function available
    if (window.calculateStats && preview && species && type) {
        spirit.stats = window.calculateStats(preview.biorhythms, species, type, 1);
    }

    // Save spirit
    const saved = await window.saveSpirit(spirit);
    
    if (saved) {
        alert(`Spirit ${name} created successfully!`);
        // Redirect to spirit sheet or home
        window.location.href = '/';
    } else {
        alert('Failed to save spirit. Please try again.');
    }
};

// CSS styles (will be injected or added to styles.css)
const wizardStyles = `
.wizard-step {
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem;
}

.wizard-step h2 {
    font-size: 2rem;
    margin-bottom: 0.5rem;
    color: #ffd700;
}

.wizard-step .instruction {
    font-size: 1.1rem;
    color: #ccc;
    margin-bottom: 2rem;
    font-style: italic;
}

.choices-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.wizard-choice {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
}

.wizard-choice:hover {
    background: rgba(255, 215, 0, 0.1);
    border-color: #ffd700;
    transform: translateY(-2px);
}

.wizard-choice h3 {
    margin: 0 0 0.5rem 0;
    color: #ffd700;
}

.wizard-choice .interpretive {
    font-size: 0.9rem;
    color: #aaa;
    margin: 0;
    line-height: 1.4;
}

.wizard-nav {
    display: flex;
    justify-content: space-between;
    margin-top: 2rem;
}

.wizard-nav button {
    padding: 0.75rem 1.5rem;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #fff;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.wizard-nav button:hover {
    background: rgba(255, 215, 0, 0.2);
    border-color: #ffd700;
}

.wizard-nav button.primary {
    background: rgba(255, 215, 0, 0.3);
    border-color: #ffd700;
}

.wizard-input {
    width: 100%;
    padding: 0.75rem;
    margin: 0.5rem 0 1rem 0;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    color: #fff;
    font-size: 1rem;
}

.wizard-input:focus {
    outline: none;
    border-color: #ffd700;
}

.stat-preview {
    background: rgba(255, 215, 0, 0.1);
    border: 1px solid #ffd700;
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0.5rem;
    text-align: center;
    font-weight: bold;
}

.wizard-confirm {
    max-width: 700px;
    margin: 0 auto;
    padding: 2rem;
}

.spirit-summary {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 1.5rem;
    margin: 1rem 0;
}

.spirit-summary p {
    margin: 0.5rem 0;
}

.final-instruction {
    font-style: italic;
    color: #ccc;
    margin: 1.5rem 0;
}
`;

// Inject styles on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        const styleEl = document.createElement('style');
        styleEl.textContent = wizardStyles;
        document.head.appendChild(styleEl);
    });
} else {
    const styleEl = document.createElement('style');
    styleEl.textContent = wizardStyles;
    document.head.appendChild(styleEl);
}
