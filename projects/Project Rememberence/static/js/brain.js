// js/brain.js
let isInitialized = false;

async function apiLoad() {
    try {
        const res = await fetch('/load-state');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        return {
            spirits: data.spirits || [],
            posts: data.posts || [],
            postCounters: data.postCounters || { lastId: 0 },
            lastSaved: data.lastSaved || 0
        };
    } catch (err) {
        console.error("apiLoad failed:", err);
        return { spirits: [], posts: [], postCounters: { lastId: 0 } };
    }
}

async function apiSave(state) {
    try {
        const res = await fetch('/save-state', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(state)
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return true;
    } catch (err) {
        console.error("apiSave failed:", err);
        return false;
    }
}



// Load one spirit by name
async function loadSpirit(name) {
    const path = `saves/${name}.json`;
    try {
        const res = await fetch(`/load-spirit?path=${path}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (err) {
        console.warn(`Spirit ${name} not found in saves/`);
        return null;
    }
}

// Save one spirit (overwrites its file)
async function saveSpirit(spirit) {
    const path = `saves/${spirit.name}.json`;
    try {
        const res = await fetch('/save-spirit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path, spirit })
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        console.log(`Saved spirit ${spirit.name} to ${path}`);
        return true;
    } catch (err) {
        console.error(`Failed to save spirit ${spirit.name}:`, err);
        return false;
    }
}

// List all saved spirits (for dropdown, sidebar)
async function listSavedSpirits() {
    try {
        const res = await fetch('/list-spirits');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json(); // returns array of names or full summaries
    } catch (err) {
        console.error('Failed to list spirits:', err);
        return [];
    }
}





window.initBrain = function initBrain() {
    if (isInitialized) return;
    const required = ['animalSigns', 'starSigns', 'bioToVerse', 'narrativeMatrix'];
    const missing = required.filter(c => !window[c]);
    if (missing.length) return;
    isInitialized = true;
}
initBrain();




window.selectBiorhythm = function selectBiorhythm(bios, abstraction) {
    const bioKeys = ['MNF', 'SPL', 'BEU', 'STR', 'FND', 'KNO', 'UND', 'WIS', 'VIT', 'SEX', 'DIV', 'EGO'];
    const bioValues = bioKeys.map(key => bios[key] || 0);
    const allZero = bioValues.every(val => val === 0);
    if (allZero) {
        const primaryIndex = Math.floor(Math.random() * bioKeys.length);
        let secondaryIndex = Math.floor(Math.random() * (bioKeys.length - 1));
        if (secondaryIndex >= primaryIndex) secondaryIndex++;
        return {
            primary: { key: bioKeys[primaryIndex], value: 5 },
            secondary: { key: bioKeys[secondaryIndex], value: 3 }
        };
    }
    
    const weights = bioValues.map(value => {
        if (abstraction >= 50) {
            return Math.max(0, 10 - Math.abs(value));
        } else if (abstraction <= -50) {
            return Math.max(0, Math.abs(value));
        } else {
            return 1;
        }
    });
    const totalWeight = weights.reduce((sum, w) => sum + w, 0) || 1;
    let randomWeight = Math.random() * totalWeight;
    let primaryIndex = 0;
    for (let i = 0; i < weights.length; i++) {
        randomWeight -= weights[i];
        if (randomWeight <= 0) {
            primaryIndex = i;
            break;
        }
    }
    const primaryBio = bioKeys[primaryIndex];
    
    const secondaryWeights = weights.map((w, i) => i === primaryIndex ? 0 : w);
    const secondaryTotalWeight = secondaryWeights.reduce((sum, w) => sum + w, 0) || 1;
    randomWeight = Math.random() * secondaryTotalWeight;
    let secondaryIndex = 0;
    for (let i = 0; i < secondaryWeights.length; i++) {
        randomWeight -= secondaryWeights[i];
        if (randomWeight <= 0) {
            secondaryIndex = i;
            break;
        }
    }
    const secondaryBio = bioKeys[secondaryIndex];
    
    return {
        primary: { key: primaryBio, value: bios[primaryBio] || 0 },
        secondary: { key: secondaryBio, value: bios[secondaryBio] || 0 }
    };
}


// ——— LOYALTY RANK SYSTEM ———

window.applyLoyaltyRank = function applyLoyaltyRank(spirit, target, delta) {
    if (!spirit.loyaltyMap) spirit.loyaltyMap = {};
    if (!spirit.loyaltyRank) spirit.loyaltyRank = {};

    let loyalty = spirit.loyaltyMap[target] || 0;
    let rank = spirit.loyaltyRank[target] || 0;

    loyalty = Math.max(-100, Math.min(100, loyalty + delta)); // CLAMP FIRST

    while (loyalty >= 100) { loyalty -= 100; rank++; }
    while (loyalty <= -100) { loyalty += 100; rank--; }

    spirit.loyaltyMap[target] = loyalty;
    spirit.loyaltyRank[target] = rank;

    console.log(`${spirit.name} → ${target}: Rank ${rank} @ ${loyalty}`);
}




window.decayThoughts = function decayThoughts(spirit) {
    let bios = window.calculateBiorhythms?.(spirit.animal, spirit.star) || 
               { MNF: 5, SPL: 0, BEU: 0, STR: 0, FND: 0, KNO: 0, UND: 0, WIS: 0, VIT: 0, SEX: 0, DIV: 0, EGO: 0 };
    const baseThoughts = window.generateThoughts(bios);
    spirit.thoughts = spirit.thoughts || baseThoughts;
    
    const stateMagnitude = Math.abs(spirit.thoughts.State || 0);
    const stateFactor = 5 + (stateMagnitude / 100);
    
    for (const key in spirit.thoughts) {
        if (key !== 'State') {
            const currentValue = spirit.thoughts[key] || 0;
            const baseValue = baseThoughts[key] || 0;
            if (currentValue !== baseValue) {
                const valueDistance = Math.abs(currentValue - baseValue);
                const decayRate = Math.round(1 + (valueDistance / 50) * stateFactor);
                const decay = currentValue > baseValue ? -decayRate : decayRate;
                spirit.thoughts[key] = Math.max(-100, Math.min(100, Math.round(currentValue + decay)));
            }
        }
    }
    spirit.thoughts.State = Math.round(Object.values(spirit.thoughts).slice(0, -1).reduce((sum, val) => sum + val, 0));
    return spirit;
}




window.decayLoyalty = function decayLoyalty(spirit) {
    spirit.loyaltyMap = spirit.loyaltyMap || {};
    const stateValue = spirit.thoughts?.State || 0;
    const stateMagnitude = Math.abs(stateValue);
    const isPositiveState = stateValue > 0;
    const isNegativeState = stateValue < 0;
    
    for (const target in spirit.loyaltyMap) {
        let currentValue = spirit.loyaltyMap[target];
        if (!currentValue || Math.abs(currentValue) < 5) continue;

        const valueDistance = Math.abs(currentValue);
        const isNegativeLoyalty = currentValue < 0;
        const stateFactor = 1 + (stateMagnitude / 100);
        const decayRate = Math.max(1, Math.round((valueDistance / 100) * stateFactor));
        const decay = currentValue > 0 ? -decayRate : decayRate;

        window.applyLoyaltyRank(spirit, target, decay);
    }
    return spirit;
}






window.cleanupLoyaltyData = async function cleanupLoyaltyData() {
    console.log("cleanupLoyaltyData STARTED — checking if new code is running...");

    try {
        const data = await apiLoad();
        let spirits = data.spirits || [];   // Always defined at top of try

        if (spirits.length === 0) {
            console.log('No spirits to clean — aether is empty.');
            return;
        }

        const validNames = new Set(spirits.map(s => s.name));

        let changesMade = false;
        spirits = spirits.map((spirit) => {   // ← arrow function preserves lexical scope
            spirit.loyaltyMap = spirit.loyaltyMap || {};
            spirit.loyaltyRank = spirit.loyaltyRank || {};
            const validMap = Object.fromEntries(
                Object.entries(spirit.loyaltyMap).filter(([name]) => validNames.has(name))
            );
            const validRank = Object.fromEntries(
                Object.entries(spirit.loyaltyRank).filter(([name]) => validNames.has(name))
            );
            if (Object.keys(spirit.loyaltyMap).length !== Object.keys(validMap).length ||
                Object.keys(spirit.loyaltyRank).length !== Object.keys(validRank).length) {
                spirit.loyaltyMap = validMap;
                spirit.loyaltyRank = validRank;
                console.log(`${spirit.name}: purged ghost loyalty/rank entries`);
                changesMade = true;
            }
            return spirit;
        });

        if (changesMade) {
            const success = await apiSave({ ...data, spirits });
            if (success) {
                console.log('Loyalty cleanup complete — aether refreshed.');
            } else {
                console.warn('Loyalty cleanup failed to save.');
            }
        } else {
            console.log('No ghost loyalties found — aether already clean.');
        }
    } catch (err) {
        console.error('cleanupLoyaltyData failed:', err);
        console.log("The aether trembles... loyalty cleanup could not complete.");
    }





window.selectVerse = function selectVerse(spirit, state) {
    const bios = calculateBiorhythms(spirit.animal, spirit.star);
    const { primary } = selectBiorhythm(bios, spirit.thoughts?.Abstraction || 0);
    const bioKey = primary.key;
    const verseState = state > 0 ? 'dominant' : 'recessive';

    // 1. Bio-driven verse (30% chance)
    if (Math.random() < 0.3) {
        const verse = bioToVerse[bioKey]?.[verseState] || 'Prologue';
        return { topic: verse, type: 'verse' };
    }

    // 2. Bio → Thought → Skill Weight
    const thoughts = spirit.thoughts || {};
    const bioThought = bioToThought[bioKey] || { key: 'State', sign: 1 };
    const thoughtValue = Math.max(-100, Math.min(100, (thoughts[bioThought.key] || 0) * bioThought.sign));
    const skillBoost = Math.max(0, thoughtValue) / 50;

    // 3. Topic Pool — single 'skill' bucket
    const topicPool = [
        { type: 'animal',   value: [spirit.animal].filter(Boolean),             weight: 1 },
        { type: 'star',     value: [spirit.star].filter(Boolean),               weight: 1 },
        { type: 'species',  value: [spirit.species, spirit.species2].filter(Boolean), weight: 1 },
        { type: 'type',     value: [spirit.type, spirit.type2].filter(Boolean), weight: 1 },
        { type: 'skill',    value: [
            spirit.meleeSkill, spirit.rangedSkill, spirit.magicSkill,
            spirit.stepSkill, spirit.specialSkill, spirit.tranceSkill
        ].filter(Boolean), weight: 1 + skillBoost }
    ].filter(t => t.value.length > 0);

    if (topicPool.length === 0) return { topic: 'Prologue', type: 'verse' };

    const totalWeight = topicPool.reduce((sum, t) => sum + t.weight, 0);
    let r = Math.random() * totalWeight;
    let selected = topicPool[0];
    for (const t of topicPool) {
        r -= t.weight;
        if (r <= 0) { selected = t; break; }
    }

    const topicValue = selected.value[Math.floor(Math.random() * selected.value.length)];
    return { topic: topicValue, type: selected.type };
}







window.replyToPost = async function replyToPost(postId, spiritName) {
    if (!spiritName) {
        alert('Please select a spirit to reply as.');
        return;
    }

    const data = await apiLoad();
    const spirits = data.spirits || [];
    const responder = spirits.find(s => s.name.toLowerCase() === spiritName.toLowerCase());
    if (!responder) {
        alert('Spirit not found. Please choose a valid spirit name.');
        return;
    }

    const posts = data.posts || [];
    const targetPost = posts.find(p => p.id === postId);
    if (!targetPost || targetPost.author === 'Player') {
        console.warn('Invalid target post or Player post.');
        return;
    }

    const initiator = spirits.find(s => s.name === targetPost.author);
    if (!initiator) {
        console.warn('Initiator spirit not found.');
        return;
    }

    // Compute biorhythms
    const initiatorBios = calculateBiorhythms(initiator.animal, initiator.star) || { MNF: 5, SPL: 0, BEU: 0, STR: 0, FND: 0, KNO: 0, UND: 0, WIS: 0, VIT: 0, SEX: 0, DIV: 0, EGO: 0 };
    const responderBios = calculateBiorhythms(responder.animal, responder.star) || { MNF: 5, SPL: 0, BEU: 0, STR: 0, FND: 0, KNO: 0, UND: 0, WIS: 0, VIT: 0, SEX: 0, DIV: 0, EGO: 0 };

    // Biorhythm selection
    const initiatorSelection = selectBiorhythm(initiatorBios, responder.thoughts?.Abstraction || 0);
    const responderSelection = selectBiorhythm(responderBios, responder.thoughts?.Abstraction || 0);

    const posterDomKey = responderSelection.primary.key;      // spirit (poster)
    const posterRecKey = responderSelection.secondary.key;
    const responderDomKey = initiatorSelection.primary.key;   // initiator (target)
    const responderRecKey = initiatorSelection.secondary.key;

    // Dual delta calculations
    const posterDomValue = responderBios[posterDomKey] || 0;
    const responderRecValue = initiatorBios[responderRecKey] || 0;
    const posterToResponderDelta = (posterDomValue - responderRecValue) + (responder.thoughts?.State || 0);

    const responderDomValue = initiatorBios[responderDomKey] || 0;
    const posterRecValue = responderBios[posterRecKey] || 0;
    const responderToPosterDelta = (responderDomValue - posterRecValue) + (initiator.thoughts?.State || 0);

    // Apply loyalty ranks
    applyLoyaltyRank(responder, targetPost.author, Math.round(posterToResponderDelta));
    applyLoyaltyRank(initiator, responder.name, Math.round(responderToPosterDelta));

    // Update responder thoughts (spirit)
    responder.thoughts = responder.thoughts || generateThoughts(responderBios);
    const thoughtKey = bioToThought?.[posterDomKey]?.key || 'State';
    const thoughtSign = bioToThought?.[posterDomKey]?.sign || 1;
    responder.thoughts[thoughtKey] = Math.max(-100, Math.min(100, Math.round((responder.thoughts[thoughtKey] || 0) + thoughtSign * Math.abs(posterDomValue))));
    responder.thoughts.State = Math.round(Object.values(responder.thoughts).slice(0, -1).reduce((sum, val) => sum + val, 0));

    // Update initiator thoughts (target post author)
    initiator.thoughts = initiator.thoughts || generateThoughts(initiatorBios);
    const initiatorThoughtKey = bioToThought?.[responderDomKey]?.key || 'State';
    const initiatorThoughtSign = bioToThought?.[responderDomKey]?.sign || 1;
    initiator.thoughts[initiatorThoughtKey] = Math.max(-100, Math.min(100, Math.round((initiator.thoughts[initiatorThoughtKey] || 0) + initiatorThoughtSign * Math.abs(responderDomValue))));
    initiator.thoughts.State = Math.round(Object.values(initiator.thoughts).slice(0, -1).reduce((sum, val) => sum + val, 0));

    // Save both updated spirits
    let updatedSpirits = spirits.map(s => {
        if (s.name === responder.name) return responder;
        if (s.name === initiator.name) return initiator;
        return s;
    });
    const success = await apiSave({ ...data, spirits: updatedSpirits });
    if (!success) {
        console.warn('Spirit state update failed during reply.');
    }

    // Generate and save reply post
    const { topic, type } = selectVerse(responder, responder.thoughts.State, responder.thoughts.Emotion || 0);
    const content = `${responder.name}: "${topic}" (Dominant: ${posterDomKey}=${posterDomValue}, Recessive: ${posterRecKey}=${responderBios[posterRecKey]}, Type: ${type})`;
    const newPostId = await savePost(content, postId, responder.name);

    // UI updates
    const newCount = getReplyCount(postId);
    const replyButton = document.querySelector(`#post-${postId} .reply-button`);
    if (replyButton) replyButton.textContent = `${newCount} repl${newCount === 1 ? 'y' : 'ies'}`;

    if (newPostId && activePostId === postId) {
        await showSelectedPost(postId);
    } else if (newPostId && !activePostId && activeView === 'timeline') {
        await loadTimeline();
    }

    await updateSpiritPosts(responder.name);
    if (activeView === 'sheet' && activeSpirit === responder.name && activeSpiritView === 'replies') {
        await updateSpiritReplies(responder.name);
    }
};
}