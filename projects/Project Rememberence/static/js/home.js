let spiritPostInterval = null;
let spiritReplyIntervals = [];
let activePostId = null;
let lastSpiritCount = 0;
let sidebarUpdateInterval = null;
let activeView = 'timeline';
let activeSpirit = null;
let activeSpiritView = 'posts';


window.getPosts = async function getPosts() {
    const data = await apiLoad();
    return data.posts || [];
};

window.getSpirits = async function getSpirits() {
    const data = await apiLoad();
    return data.spirits || [];
};


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
        console.error("Cannot load state:", err);
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
        console.log("State saved");
        return true;
    } catch (err) {
        console.error("Save failed:", err);
        return false;
    }
}




// ——— AUTO-REFRESH DROPDOWN ———
async function refreshSpiritDropdown() {
    const select = document.getElementById('spirit-select');
    if (!select) return;

    const currentValue = select.value;
    
    const state = await apiLoad();                    // ← new
    const spirits = state.spirits || [];              // ← new
    const spiritNames = spirits.map(s => s.name);

    const currentNames = Array.from(select.options).slice(1).map(opt => opt.value);
    if (JSON.stringify(currentNames) === JSON.stringify(spiritNames)) {
        return;
    }

    select.innerHTML = `<option value="">Select Spirit</option>` +
        spiritNames.map(name => `<option value="${name}">${name}</option>`).join('');

    if (currentValue && spiritNames.includes(currentValue)) {
        select.value = currentValue;
    }

    if (spirits.length !== lastSpiritCount) {
        lastSpiritCount = spirits.length;
        updateSpiritReplyIntervals();   // keep — assuming it exists
    }

    console.log('Dropdown refreshed:', spirits.length, 'spirits');
}


// ——— INITIAL SETUP ———
function initHomeHub() {
    const hub = document.getElementById('home-hub');
    if (!hub) return;

    hub.innerHTML = `
        <div class="spirit-sidebar" id="spirit-sidebar"></div>
        <div class="post-section">
            <div style="display: flex; justify-content: center; margin-bottom: 10px;">
                <select id="spirit-select" style="padding: 5px; width: 200px;">
                    <option value="">Select Spirit</option>
                </select>
            </div>
            <div class="button-group" style="display: flex; flex-direction: row; gap: 10px; margin: 10px 0; justify-content: center;">
                <button id="post-command">Post as Spirit</button>
                <button id="refresh-timeline">Timeline</button>
                <button id="clear-timeline">Clear</button>
                <button id="load-spirit">Load Spirit</button>
            </div>
            <div id="timeline"></div>
            <div id="selected-post" style="display: none;"></div>
        </div>
    `;

    // ——— EVENT LISTENERS ———
    hub.addEventListener('click', (e) => {
        const spiritName = document.getElementById('spirit-select')?.value || '';
        const target = e.target;  // ← Define target once at the top for clarity

        if (target.id === 'post-command') {
            if (!spiritName) { alert('Please select a spirit.'); return; }
            postToTimeline(spiritName);
        } else if (target.id === 'refresh-timeline') {
            activeView = 'timeline'; activeSpirit = null; activeSpiritView = 'posts';
            loadTimeline();
        } else if (target.id === 'clear-timeline') {
            activeView = 'timeline'; activeSpirit = null; activeSpiritView = 'posts';
            clearTimeline();
        } else if (target.id === 'load-spirit') {
            if (!spiritName) { alert('Please select a spirit.'); return; }
            activeView = 'sheet'; activeSpirit = spiritName; activeSpiritView = 'posts';
            loadSpiritSheet(spiritName);
        } else if (e.target.classList.contains('reply-button')) {
    const postId = e.target.getAttribute('data-post-id');
    const responderName = document.getElementById('spirit-select')?.value || '';

    if (!responderName) {
        alert('Select a spirit to reply with.');
        return;
    }
    if (!postId) {
        console.warn('Reply button clicked but missing data-post-id');
        return;
    }

    console.log('[Spirit Reply Triggered] From:', responderName, '→ Post:', postId);

    // Directly invoke the existing function — no addReply, no prompt
    replyToPost(postId, responderName);
} else if (target.id === 'recent-posts-btn') {
            activeSpiritView = 'posts';
            updateSpiritPosts(activeSpirit);
        } else if (target.id === 'recent-replies-btn') {
            activeSpiritView = 'replies';
            updateSpiritReplies(activeSpirit);
        } else if (target.closest('.post-box')) {
            const postId = target.closest('.post-box').id.replace('post-', '');
            activeView = 'post'; activeSpiritView = 'posts';
            showSelectedPost(postId);
        }
    });

    // ——— INITIAL LOAD ———
    refreshSpiritDropdown();
    activeView = 'timeline';
    loadTimeline();
    if (!spiritPostInterval) updateSpiritPostInterval();
    if (spiritReplyIntervals.length === 0) updateSpiritReplyIntervals();
    // ——— AUTO-REFRESH EVERY 2 SECONDS ———
    setInterval(refreshSpiritDropdown, 2000);
    cleanupLoyaltyData();
    console.log('Home Hub initialized: Auto-refresh enabled');
}




async function updateSpiritPosts(spiritName) {
    if (activeView !== 'sheet' || activeSpirit !== spiritName) return;

    const postsContainer = document.querySelector('#spirit-posts-container');
    if (!postsContainer) return;

    try {
        const state = await apiLoad();
        const allPosts = state.posts || [];

        const spiritPosts = allPosts
            .filter(p => p.author === spiritName && !p.parentId)
            .sort((a, b) => b.timestamp - a.timestamp);

        postsContainer.innerHTML = '';

        if (spiritPosts.length === 0) {
            postsContainer.innerHTML = '<p>No top-layer posts found for this spirit.</p>';
        } else {
            for (const post of spiritPosts) {
                const postElement = await createPostElement(post, false);  // note: await if createPostElement becomes async later
                postElement.style.marginBottom = '10px';
                postsContainer.appendChild(postElement);
            }
        }

        document.getElementById('recent-posts-btn')?.classList.add('active');
        document.getElementById('recent-replies-btn')?.classList.remove('active');

        console.log(`Updated posts for ${spiritName}: ${spiritPosts.length} top-layer posts`);
    } catch (err) {
        console.error("Failed to load posts for sheet:", err);
        postsContainer.innerHTML = '<p style="color: #ff6666;">Could not load posts from the weave...</p>';
    }
}





async function updateSpiritReplies(spiritName) {
    if (activeView !== 'sheet' || activeSpirit !== spiritName) return;

    const postsContainer = document.querySelector('#spirit-posts-container');
    if (!postsContainer) return;

    try {
        const state = await apiLoad();
        const allPosts = state.posts || [];

        const spiritReplies = allPosts
            .filter(p => p.author === spiritName && p.parentId)
            .sort((a, b) => b.timestamp - a.timestamp);

        postsContainer.innerHTML = '';

        if (spiritReplies.length === 0) {
            postsContainer.innerHTML = '<p>No replies found for this spirit.</p>';
        } else {
            for (const reply of spiritReplies) {
                const postElement = await createPostElement(reply, false);
                postElement.style.marginBottom = '10px';
                postsContainer.appendChild(postElement);
            }
        }

        document.getElementById('recent-posts-btn')?.classList.remove('active');
        document.getElementById('recent-replies-btn')?.classList.add('active');

        console.log(`Updated replies for ${spiritName}: ${spiritReplies.length} replies`);
    } catch (err) {
        console.error("Failed to load replies for sheet:", err);
        postsContainer.innerHTML = '<p style="color: #ff6666;">Could not load replies from the weave...</p>';
    }
}




async function loadSpiritSheet(spiritName) {
    try {
        const state = await apiLoad();
        const spirits = state.spirits || [];

        if (spirits.length === 0) {
            console.warn('No saved spirits found on server');
            alert('No saved spirits found.');
            return;
        }

        const spiritIndex = spirits.findIndex(s => s.name.toLowerCase() === spiritName.toLowerCase());
        if (spiritIndex === -1) {
            console.warn(`No spirit found with name: ${spiritName}`);
            alert('No spirit found with that name.');
            activeView = 'timeline';
            activeSpirit = null;
            activeSpiritView = 'posts';
            await loadTimeline();
            return;
        }

        let spirit = { ...spirits[spiritIndex] }; // copy to avoid mutating original directly

        // Update thoughts if missing
        const bios = calculateBiorhythms?.(spirit.animal, spirit.star) || {};
        if (!spirit.thoughts) {
            spirit.thoughts = generateThoughts?.(bios) || {};
        }

        // Save updated spirit back
        spirits[spiritIndex] = spirit;
        const updatedState = { ...state, spirits };
        await apiSave(updatedState);

        // ── Render UI ───────────────────────────────────────────────────────────────
        const selectedPostContainer = document.getElementById('selected-post');
        const timeline = document.getElementById('timeline');
        if (!selectedPostContainer || !timeline) return;

        timeline.style.display = 'none';
        selectedPostContainer.style.display = 'block';
        selectedPostContainer.innerHTML = '';

        const wrapper = document.createElement('div');
        wrapper.style.padding = '20px';
        wrapper.style.maxWidth = '600px';
        wrapper.style.margin = '0 auto';
        wrapper.innerHTML = `
            <div class="data-card">
                <h3>${spirit.name}'s Profile</h3>
                <p><strong>Description:</strong> ${spirit.description || 'No description'}</p>
                <p><strong>Animal Sign:</strong> ${spirit.animal || 'Rat'}</p>
                <p><strong>Star Sign:</strong> ${spirit.star || 'Aries'}</p>
                <p><strong>Species:</strong> ${spirit.species || 'None'} / ${spirit.species2 || 'None'}</p>
                <p><strong>Species Active Skill:</strong> ${spirit.speciesActive || 'None'}</p>
                <p><strong>Type:</strong> ${spirit.type || 'None'} / ${spirit.type2 || 'None'}</p>
                <p><strong>Type Active Skill:</strong> ${spirit.typeActive || 'None'}</p>
                <h4>Skills:</h4>
                <ul>
                    <li><strong>Melee:</strong> ${spirit.meleeSkill || 'None'}</li>
                    <li><strong>Ranged:</strong> ${spirit.rangedSkill || 'None'}</li>
                    <li><strong>Magic:</strong> ${spirit.magicSkill || 'None'}</li>
                    <li><strong>Step:</strong> ${spirit.stepSkill || 'None'}</li>
                    <li><strong>Special:</strong> ${spirit.specialSkill || 'None'}</li>
                    <li><strong>Trance:</strong> ${spirit.tranceSkill || 'None'}</li>
                </ul>
                <p><strong>Level:</strong> ${spirit.level || 1}</p>
            </div>
            <div class="spirit-posts" style="margin-top: 20px;">
                <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                    <button id="recent-posts-btn" class="active">Recent Posts</button>
                    <button id="recent-replies-btn">Recent Replies</button>
                </div>
                <div id="spirit-posts-container"></div>
            </div>
        `;
        selectedPostContainer.appendChild(wrapper);

        if (activeSpiritView === 'posts') {
            updateSpiritPosts(spiritName);
        } else {
            updateSpiritReplies(spiritName);
        }

        if (sidebarUpdateInterval) {
            clearInterval(sidebarUpdateInterval);
        }
        showSpiritSidebar(spirit.name, null);
        sidebarUpdateInterval = setInterval(() => {
            showSpiritSidebar(spirit.name, null);
        }, 1000);

        console.log(`Loaded spirit ${spirit.name} — thoughts updated, ${state.posts?.filter?.(p => p.author === spirit.name && !p.parentId)?.length || 0} top-layer posts`);

    } catch (err) {
        console.error('Failed to load spirit sheet:', err);
        alert('The aether is veiled — could not load the spirit.');
    }
}



async function showSpiritSidebar(author, postId) {
    const sidebar = document.getElementById('spirit-sidebar');
    if (!sidebar || author === 'Player') {
        hideSpiritSidebar();
        return;
    }

    try {
        const state = await apiLoad();
        const spirits = state.spirits || [];
        const spirit = spirits.find(s => s.name === author);

        if (!spirit) {
            hideSpiritSidebar();
            return;
        }

        let bios = calculateBiorhythms?.(spirit.animal, spirit.star) || {
            MNF: 5, SPL: 0, BEU: 0, STR: 0, FND: 0, KNO: 0, UND: 0, WIS: 0, VIT: 0, SEX: 0, DIV: 0, EGO: 0
        };

        let updated = false;
        if (!spirit.thoughts) {
            spirit.thoughts = generateThoughts?.(bios) || {};
            updated = true;
        }

        // Optional: loyalty cleanup if needed
        // spirit = cleanupLoyaltyData([spirit])[0];   // ← if you want to keep this

        if (updated) {
            const updatedSpirits = spirits.map(s => s.name === spirit.name ? spirit : s);
            await apiSave({ ...state, spirits: updatedSpirits });
        }

        const thoughts = spirit.thoughts || {};
        const loyaltyMap = spirit.loyaltyMap || {};
        const loyaltyRank = spirit.loyaltyRank || {};

        const formatCross = (main, cross) => main && cross ? `${main} / ${cross}` : main || cross || 'None';

        sidebar.innerHTML = `
            <h3>${spirit.name}</h3>
            <p><strong>Animal:</strong> ${spirit.animal || '?'}</p>
            <p><strong>Star:</strong> ${spirit.star || '?'}</p>
            <p><strong>Species:</strong> ${formatCross(spirit.species, spirit.species2)}</p>
            <p><strong>Type:</strong> ${formatCross(spirit.type, spirit.type2)}</p>
            <h4>Biorhythms:</h4>
            <ul>
                ${Object.entries(bios).map(([k, v]) => `<li>${k}: ${v}</li>`).join('')}
            </ul>
            <h4>Thoughts:</h4>
            <ul>
                ${Object.entries(thoughts).map(([k, v]) => `<li>${k}: ${v}</li>`).join('')}
            </ul>
            <h4>Loyalties:</h4>
            <ul>
                ${(() => {
                    const allNames = new Set([...Object.keys(loyaltyMap), ...Object.keys(loyaltyRank)]);
                    return Array.from(allNames).map(name => {
                        const value = loyaltyMap[name] ?? 0;
                        const rank = loyaltyRank[name] ?? 0;
                        const rankText = rank > 0 ? `+${rank}` : rank < 0 ? `${rank}` : '0';
                        return `<li>${name}: ${value} <strong>[R${rankText}]</strong></li>`;
                    }).join('') || '<li>No loyalties recorded</li>';
                })()}
            </ul>
        `;

        sidebar.style.display = 'block';
        sidebar.style.opacity = '0';
        setTimeout(() => {
            sidebar.style.opacity = '1';
            sidebar.style.transform = 'translateX(0)';
        }, 10);

    } catch (err) {
        console.error('Failed to show spirit sidebar:', err);
        hideSpiritSidebar();
    }
}



function hideSpiritSidebar() {
    const sidebar = document.getElementById('spirit-sidebar');
    if (sidebar) {
        sidebar.style.opacity = '0';
        sidebar.style.transform = 'translateX(-20px)';
        setTimeout(() => {
            sidebar.style.display = 'none';
            sidebar.innerHTML = '';
        }, 300);
    }
}

async function getReplyCount(postId) {
    const state = await apiLoad();
    const posts = state.posts || [];
    return posts.filter(p => p.parentId === postId).length;
}



async function showSelectedPost(postId) {
    console.log('showSelectedPost called with postId:', postId);

    const timeline = document.getElementById('timeline');
    const container = document.getElementById('selected-post');
    if (!timeline || !container) return;

    document.getElementById('spirit-sidebar')?.style.setProperty('display', 'block');

    if (sidebarUpdateInterval) {
        clearInterval(sidebarUpdateInterval);
        sidebarUpdateInterval = null;
    }

    timeline.style.display = 'none';
    container.style.display = 'block';
    container.innerHTML = '<p>Loading post...</p>';

    try {
        const state = await apiLoad();
        const posts = state.posts || [];

        const post = posts.find(p => p.id === postId);
        if (!post) {
            container.innerHTML = '<p>Post not found in the weave.</p>';
            return;
        }

        // Build thread upwards (parents)
        const parentPosts = [];
        let current = post;
        while (current.parentId) {
            const parent = posts.find(p => p.id === current.parentId);
            if (parent) {
                parentPosts.unshift(parent);
                current = parent;
            } else break;
        }

        const wrapper = document.createElement('div');
        wrapper.style.padding = '20px';
        wrapper.style.maxWidth = '600px';
        wrapper.style.margin = '0 auto';

        // Parents
        for (const parent of parentPosts) {
            const el = await createPostElement(parent, false);
            wrapper.appendChild(el);
        }

        // Main post
        const mainEl = await createPostElement(post, true);
        mainEl.classList.add('highlight');
        wrapper.appendChild(mainEl);

        container.innerHTML = '';
        container.appendChild(wrapper);

        // Scroll
        setTimeout(() => {
            const target = document.getElementById(`post-${postId}`);
            if (target) target.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);

        activePostId = postId;

        // Sidebar (assuming showSpiritSidebar exists)
        showSpiritSidebar?.(post.author, postId);

        if (post.author !== 'Player') {
            sidebarUpdateInterval = setInterval(() => {
                showSpiritSidebar?.(post.author, postId);
            }, 1000);
        }

    } catch (err) {
        console.error('Error showing selected post:', err);
        container.innerHTML = '<p style="color:#ff6666">Could not retrieve this thread...</p>';
    }
}




async function loadTimeline() {
    if (activeView !== 'timeline') return;

    const timeline = document.getElementById('timeline');
    const selected = document.getElementById('selected-post');
    if (!timeline) return;

    // Simple CSS hide instead of missing hideSpiritSidebar()
    document.getElementById('spirit-sidebar')?.style.setProperty('display', 'none');

    if (sidebarUpdateInterval) {
        clearInterval(sidebarUpdateInterval);
        sidebarUpdateInterval = null;
    }

    timeline.style.display = 'grid';
    timeline.style.gridTemplateColumns = 'repeat(3, 1fr)';
    timeline.style.gap = '10px';
    if (selected) selected.style.display = 'none';

    activePostId = null;
    timeline.innerHTML = '<p>Loading timeline...</p>';

    try {
        const state = await apiLoad();
        const posts = state.posts || [];

        timeline.innerHTML = '';

        const roots = posts
            .filter(p => !p.parentId)
            .sort((a, b) => b.timestamp - a.timestamp);

        if (roots.length === 0) {
            timeline.innerHTML = '<p>The weave is silent for now...</p>';
            return;
        }

        for (const post of roots) {
            const el = await createPostElement(post, false);   // await — future-proof
            timeline.appendChild(el);
        }
    } catch (err) {
        console.error('Timeline load failed:', err);
        timeline.innerHTML = '<p style="color:#ff6666">Could not load the timeline...</p>';
    }
}



async function clearTimeline() {
    console.log('Clearing timeline from server');
    const state = await apiLoad();
    const updated = {
        ...state,
        posts: [],
        postCounters: { lastId: 0 }
    };
    await apiSave(updated);
    await loadTimeline();
}



async function createPostElement(post, includeReplies = true) {
    const postElement = document.createElement('div');
    postElement.id = `post-${post.id}`;
    postElement.className = `post-box ${post.parentId ? 'reply' : ''}`;

    let replyCount = 0;
    if (includeReplies) {
        replyCount = await getReplyCount(post.id);   // ← await the async version
    }

    let name, dominantBio, recessiveBio, topic, topicType, topicDesc;
    let dominantDesc = 'No description available.';
    let recessiveDesc = 'No description available.';

    console.log('createPostElement: Processing post:', post.id, post.content);

    if (post.author !== 'Player') {
        const match = post.content.match(/^([^:]+): "([^"]*)"\s*\(Dominant: (\w+)=([-]?\d+), Recessive: (\w+)=([-]?\d+), Type: (\w+)\)$/);
        if (match) {
            name = match[1];
            topic = match[2] || 'Unknown';
            dominantBio = `${match[3]}=${match[4]}`;
            recessiveBio = `${match[5]}=${match[6]}`;
            topicType = match[7];

            // Descriptions (keep your existing logic)
            if (includeReplies) {
                // ... your biorhythms / narrativeMatrix / animalSigns / etc. logic remains the same ...
                // just remove any localStorage lookups inside (e.g. for skill lookup)
            } else {
                topicDesc = topic;
            }
        } else {
            // fallback
            name = post.author;
            topic = 'Prologue';
            topicType = 'verse';
            topicDesc = includeReplies ? (narrativeMatrix?.['Prologue']?.desc || 'The beginning...') : 'Prologue';
            dominantBio = 'None=0';
            recessiveBio = 'None=0';
        }
    } else {
        name = post.author;
        topic = post.content.replace(/^Player: "(.*)"$/, '$1') || 'Unknown';
        topicType = 'custom';
        topicDesc = includeReplies ? (narrativeMatrix?.[topic]?.desc || 'A mortal’s voice...') : topic;
        dominantBio = 'None=0';
        recessiveBio = 'None=0';
    }

    const bioDetails = includeReplies ? `
        <p>${dominantBio}</p>
        <p style="font-style: italic;">${dominantDesc}</p>
        <p>${recessiveBio}</p>
        <p style="font-style: italic;">${recessiveDesc}</p>
        <p><strong>${topicType.charAt(0).toUpperCase() + topicType.slice(1)}:</strong> ${topic}</p>
        <p style="font-style: italic;">${topicDesc}</p>
    ` : `
        <p><strong>Dominant Bio:</strong> ${dominantBio}</p>
        <p><strong>Recessive Bio:</strong> ${recessiveBio}</p>
        <p><strong>Topic:</strong> ${topic}</p>
    `;

    postElement.innerHTML = `
        <div class="post-frame" style="border:none; padding:0; background:transparent; border-radius:8px; transition:transform 0.2s ease, box-shadow 0.2s ease;">
            <div class="data-card">
                <p><strong>Name:</strong> ${name}</p>
                ${bioDetails}
            </div>
            <div class="post-actions">
                <button class="reply-button" data-post-id="${post.id}">${replyCount} repl${replyCount === 1 ? 'y' : 'ies'}</button>
            </div>
        </div>
        <div class="replies-container"></div>
    `;

    if (includeReplies) {
        const repliesContainer = postElement.querySelector('.replies-container');
        const state = await apiLoad();
        const allPosts = state.posts || [];
        const replies = allPosts
            .filter(p => p.parentId === post.id)
            .sort((a, b) => b.timestamp - a.timestamp);

        for (const reply of replies) {
            const replyEl = await createPostElement(reply, false);   // recursive, but false → no nested replies
            repliesContainer.appendChild(replyEl);
        }
    }

    console.log('createPostElement output:', postElement.outerHTML);
    return postElement;
}




function buildThreadedPosts(posts) {
    return posts.filter(post => !post.parentId);
}



async function savePost(content, parentId, author) {
    try {
        // 1. Load current state from server
        const state = await apiLoad();

        // 2. Calculate next ID
        let nextId = (state.postCounters?.lastId || 0) + 1;

        // 3. Create the new post object
        const newPost = {
            id: nextId.toString(),
            content,
            parentId: parentId || null,   // make sure it's null for root posts
            author,
            timestamp: Date.now(),
            replies: []                   // kept for compatibility, though not strictly needed
        };

        // 4. Build updated state
        const updatedState = {
            ...state,
            posts: [...(state.posts || []), newPost],
            postCounters: { lastId: nextId }
        };

        // 5. Save to server
        const success = await apiSave(updatedState);

        if (!success) {
            console.error("Failed to save new post to server");
            alert("Could not preserve this message in the weave...");
            return null;
        }

        console.log('Post saved to server:', newPost, 'Total posts now:', updatedState.posts.length);
        return newPost.id;

    } catch (err) {
        console.error("Error while saving post:", err);
        alert("The aether trembled — message could not be anchored.");
        return null;
    }
}






async function updateSpiritPostInterval() {
    if (window.spiritPostInterval) {
        clearInterval(window.spiritPostInterval);
        window.spiritPostInterval = null;
    }

    const data = await apiLoad();
    const spirits = data.spirits || [];
    if (spirits.length === 0) {
        console.log('No spirits to post — interval not set.');
        return;
    }

    // Compute averages safely
    const totalState = spirits.reduce((sum, s) => sum + Math.abs(s.thoughts?.State || 0), 0);
    const totalEnvironment = spirits.reduce((sum, s) => sum + (s.thoughts?.Environment || 0), 0);
    const averageState = totalState / spirits.length;
    const averageEnvironment = totalEnvironment / spirits.length;

    // Interval calculation (5000ms base, modulated by averages)
    const stateFactor = 0.3 * (averageState / 600);
    const environmentFactor = 0.2 * (averageEnvironment / 100);
    const postInterval = 5000 * Math.max(0.5, Math.min(1.5, 1 - stateFactor - environmentFactor));

    // Schedule interval
    window.spiritPostInterval = setInterval(async () => {
        const currentData = await apiLoad();
        const currentSpirits = currentData.spirits || [];
        if (currentSpirits.length === 0) return;

        const randomSpirit = currentSpirits[Math.floor(Math.random() * currentSpirits.length)];
        await simulateSpiritPosts(randomSpirit);
    }, postInterval);

    console.log('Spirit post interval set:', postInterval, 'ms');
}async function updateSpiritPostInterval() {
    if (window.spiritPostInterval) {
        clearInterval(window.spiritPostInterval);
        window.spiritPostInterval = null;
    }

    const data = await apiLoad();
    const spirits = data.spirits || [];
    if (spirits.length === 0) {
        console.log('No spirits to post — interval not set.');
        return;
    }

    // Compute averages safely
    const totalState = spirits.reduce((sum, s) => sum + Math.abs(s.thoughts?.State || 0), 0);
    const totalEnvironment = spirits.reduce((sum, s) => sum + (s.thoughts?.Environment || 0), 0);
    const averageState = totalState / spirits.length;
    const averageEnvironment = totalEnvironment / spirits.length;

    // Interval calculation (5000ms base, modulated by averages)
    const stateFactor = 0.3 * (averageState / 600);
    const environmentFactor = 0.2 * (averageEnvironment / 100);
    const postInterval = 5000 * Math.max(0.5, Math.min(1.5, 1 - stateFactor - environmentFactor));

    // Schedule interval
    window.spiritPostInterval = setInterval(async () => {
        const currentData = await apiLoad();
        const currentSpirits = currentData.spirits || [];
        if (currentSpirits.length === 0) return;

        const randomSpirit = currentSpirits[Math.floor(Math.random() * currentSpirits.length)];
        await simulateSpiritPosts(randomSpirit);
    }, postInterval);

    console.log('Spirit post interval set:', postInterval, 'ms');
}




async function updateSpiritReplyIntervals() {
    // Clear any old intervals safely
    if (window.spiritReplyIntervals && window.spiritReplyIntervals.length > 0) {
        window.spiritReplyIntervals.forEach(id => clearInterval(id));
        window.spiritReplyIntervals = [];
    }

    const data = await apiLoad();
    const spirits = data.spirits || [];
    if (spirits.length === 0) {
        console.log('No spirits to reply — intervals cleared.');
        return;
    }

    window.spiritReplyIntervals = [];   // ← reset to real array

    for (const spirit of spirits) {
        // Immediate decay + thought generation
        let currentSpirit = await decayThoughts(spirit);
        currentSpirit = await decayLoyalty(currentSpirit);

        const bios = calculateBiorhythms(currentSpirit.animal, currentSpirit.star) || 
                     { MNF: 5, SPL: 0, BEU: 0, STR: 0, FND: 0, KNO: 0, UND: 0, WIS: 0, VIT: 0, SEX: 0, DIV: 0, EGO: 0 };

        if (!currentSpirit.thoughts) {
            currentSpirit.thoughts = generateThoughts(bios);
        }

        const stateMagnitude = Math.abs(currentSpirit.thoughts.State || 0);
        const environmentValue = currentSpirit.thoughts.Environment || 0;
        const stateFactor = 0.3 * (stateMagnitude / 600);
        const environmentFactor = 0.2 * (environmentValue / 100);
        const intervalMs = 15000 * Math.max(0.5, Math.min(1.5, 1 - stateFactor - environmentFactor));

        // Create and store the REAL interval ID
        const replyIntervalId = setInterval(async () => {
            try {
                let currentData = await apiLoad();
                let currentSpirits = currentData.spirits || [];
                let updatedSpirit = currentSpirits.find(s => s.name === currentSpirit.name);
                if (!updatedSpirit) return;

                updatedSpirit = await decayThoughts(updatedSpirit);
                updatedSpirit = await decayLoyalty(updatedSpirit);

                await simulateSpiritReplies(updatedSpirit);

                // Save the updated spirit back
                currentSpirits = currentSpirits.map(s => 
                    s.name === updatedSpirit.name ? updatedSpirit : s
                );
                const success = await apiSave({ ...currentData, spirits: currentSpirits });
                if (success) {
                    await window.cleanupLoyaltyData();
                }
            } catch (err) {
                console.error("Reply interval error:", err);
            }
        }, intervalMs);

        window.spiritReplyIntervals.push(replyIntervalId);
    }

    console.log(`Reply intervals restored for ${spirits.length} spirits`);
}




async function simulateSpiritPosts(spirit = null) {
    try {
        const data = await apiLoad();
        let spirits = data.spirits || [];
        if (spirits.length === 0) return;

        // Select spirit (provided or random)
        const selectedSpirit = spirit || spirits[Math.floor(Math.random() * spirits.length)];
        const bios = calculateBiorhythms(selectedSpirit.animal, selectedSpirit.star);

        // Compute dominant/recessive bio
        const selection = selectBiorhythm(bios, selectedSpirit.thoughts?.Abstraction || 0);
        let dominantBioKey = selection.primary.value >= selection.secondary.value ? selection.primary.key : selection.secondary.key;
        let dominantBioValue = selection.primary.value >= selection.secondary.value ? selection.primary.value : selection.secondary.value;
        let recessiveBioKey = selection.primary.value >= selection.secondary.value ? selection.secondary.key : selection.secondary.key;
        let recessiveBioValue = selection.primary.value >= selection.secondary.value ? selection.secondary.value : selection.secondary.value;

        // Ensure thoughts exist
        selectedSpirit.thoughts = selectedSpirit.thoughts || generateThoughts(bios);
        const thoughtKey = bioToThought?.[dominantBioKey]?.key || 'State';
        const thoughtSign = bioToThought?.[dominantBioKey]?.sign || 1;
        selectedSpirit.thoughts[thoughtKey] = Math.max(-100, Math.min(100, Math.round((selectedSpirit.thoughts[thoughtKey] || 0) + thoughtSign * Math.abs(dominantBioValue))));
        selectedSpirit.thoughts.State = Math.round(Object.values(selectedSpirit.thoughts).slice(0, -1).reduce((sum, val) => sum + val, 0));

        // Clean loyalty data
        selectedSpirit.loyaltyMap = selectedSpirit.loyaltyMap || {};
        selectedSpirit.loyaltyRank = selectedSpirit.loyaltyRank || {};

        // Update spirit in state
        spirits = spirits.map(s => s.name === selectedSpirit.name ? selectedSpirit : s);

        // Save updated spirits
        const success = await apiSave({ ...data, spirits });
        if (!success) {
            console.warn('Spirit state update failed during simulation.');
        }

        // Generate and save post
        const { topic, type } = selectVerse(selectedSpirit, selectedSpirit.thoughts.State, selectedSpirit.thoughts.Emotion || 0);
        const content = `${selectedSpirit.name}: "${topic}" (Dominant: ${dominantBioKey}=${dominantBioValue}, Recessive: ${recessiveBioKey}=${recessiveBioValue}, Type: ${type})`;
        const postId = await savePost(content, null, selectedSpirit.name);

        if (postId) {
            console.log('Spirit post created:', postId, 'content:', content);
        }

        // Refresh UI if needed
        if (!activePostId && activeView === 'timeline') {
            await loadTimeline();
        }
        await updateSpiritPosts(selectedSpirit.name);
    } catch (err) {
        console.error('simulateSpiritPosts failed:', err);
        alert("The aether trembles... spirit could not post.");
    }
}





window.simulateSpiritReplies = async function simulateSpiritReplies(spirit) {
    try {
        const data = await apiLoad();
        const posts = data.posts || [];
        const eligiblePosts = posts.filter(p => p.author !== spirit.name && p.author !== 'Player');
        if (eligiblePosts.length === 0) return;

        const subconsciousValue = spirit.thoughts?.Subconscious || 0;
        if (Math.random() >= 0.5 + 0.5 * (subconsciousValue / 100)) return;

        spirit.loyaltyMap = spirit.loyaltyMap || {};

        // Filter posts with known loyalty
        const loyaltyPosts = eligiblePosts.filter(p => spirit.loyaltyMap[p.author] !== undefined);
        const perceptionFactor = (spirit.thoughts?.Perception || 0) / 100;
        let targetPost;

        if (loyaltyPosts.length > 0) {
            if (perceptionFactor >= 0.5) {
                const maxLoyalty = Math.max(...loyaltyPosts.map(p => Math.abs(spirit.loyaltyMap[p.author] || 0)));
                const maxLoyaltyPosts = loyaltyPosts.filter(p => Math.abs(spirit.loyaltyMap[p.author] || 0) === maxLoyalty);
                targetPost = maxLoyaltyPosts[Math.floor(Math.random() * maxLoyaltyPosts.length)];
            } else {
                const totalWeight = loyaltyPosts.reduce((sum, post) => sum + Math.abs(spirit.loyaltyMap[post.author] || 0), 0);
                let randomWeight = Math.random() * totalWeight;
                for (const post of loyaltyPosts) {
                    randomWeight -= Math.abs(spirit.loyaltyMap[post.author] || 0);
                    if (randomWeight <= 0) {
                        targetPost = post;
                        break;
                    }
                }
                if (!targetPost) targetPost = loyaltyPosts[loyaltyPosts.length - 1];
            }
        } else {
            targetPost = eligiblePosts[Math.floor(Math.random() * eligiblePosts.length)];
        }

        const initiator = data.spirits.find(s => s.name === targetPost.author);
        if (!initiator) return;

        // Biorhythms & deltas (unchanged)
        const initiatorBios = calculateBiorhythms(initiator.animal, initiator.star);
        const responderBios = calculateBiorhythms(spirit.animal, spirit.star);

        const initiatorSelection = selectBiorhythm(initiatorBios, spirit.thoughts?.Abstraction || 0);
        const responderSelection = selectBiorhythm(responderBios, spirit.thoughts?.Abstraction || 0);

        const posterDomKey = responderSelection.primary.key;
        const posterRecKey = responderSelection.secondary.key;
        const responderDomKey = initiatorSelection.primary.key;
        const responderRecKey = initiatorSelection.secondary.key;

        const posterDomValue = responderBios[posterDomKey] || 0;
        const responderRecValue = initiatorBios[responderRecKey] || 0;
        const posterToResponderDelta = (posterDomValue - responderRecValue) + (spirit.thoughts?.State || 0);

        const responderDomValue = initiatorBios[responderDomKey] || 0;
        const posterRecValue = responderBios[posterRecKey] || 0;
        const responderToPosterDelta = (responderDomValue - posterRecValue) + (spirit.thoughts?.State || 0);

        applyLoyaltyRank(spirit, initiator.name, Math.round(posterToResponderDelta));
        applyLoyaltyRank(initiator, spirit.name, Math.round(responderToPosterDelta));

        // Update thoughts
        spirit.thoughts = spirit.thoughts || generateThoughts(responderBios);
        const thoughtKey = bioToThought?.[posterDomKey]?.key || 'State';
        const thoughtSign = bioToThought?.[posterDomKey]?.sign || 1;
        spirit.thoughts[thoughtKey] = Math.max(-100, Math.min(100, Math.round((spirit.thoughts[thoughtKey] || 0) + thoughtSign * Math.abs(posterDomValue))));
        spirit.thoughts.State = Math.round(Object.values(spirit.thoughts).slice(0, -1).reduce((sum, val) => sum + val, 0));

        initiator.thoughts = initiator.thoughts || generateThoughts(initiatorBios);
        const initThoughtKey = bioToThought?.[responderDomKey]?.key || 'State';
        const initThoughtSign = bioToThought?.[responderDomKey]?.sign || 1;
        initiator.thoughts[initThoughtKey] = Math.max(-100, Math.min(100, Math.round((initiator.thoughts[initThoughtKey] || 0) + initThoughtSign * Math.abs(responderDomValue))));
        initiator.thoughts.State = Math.round(Object.values(initiator.thoughts).slice(0, -1).reduce((sum, val) => sum + val, 0));

        // Save both
        let updatedSpirits = data.spirits.map(s => {
            if (s.name === spirit.name) return spirit;
            if (s.name === initiator.name) return initiator;
            return s;
        });
        await apiSave({ ...data, spirits: updatedSpirits });

        // Generate and save reply
        const { topic, type } = selectVerse(spirit, spirit.thoughts.State);
        const content = `${spirit.name}: "${topic}" (Dominant: ${posterDomKey}=${posterDomValue}, Recessive: ${posterRecKey}=${responderBios[posterRecKey]}, Type: ${type})`;
        await savePost(content, targetPost.id, spirit.name);

        // Silent failure instead of alert
        console.log("Silent failure: spirit could not reply — see console for details.");
    } catch (err) {
        console.error('simulateSpiritReplies failed:', err);
        console.log("Silent failure: spirit could not reply — see console for details.");
    }
}




document.addEventListener('DOMContentLoaded', async () => {
    console.log("DOMContentLoaded fired — initializing Home Hub...");

    const hub = document.getElementById('home-hub');
    if (!hub) {
        console.warn('Home hub element not found.');
        return;
    }

    // Build hub structure (if not already present)
    hub.innerHTML = `
        <div class="spirit-sidebar" id="spirit-sidebar"></div>
        <div class="post-section">
            <div style="display: flex; justify-content: center; margin-bottom: 10px;">
                <select id="spirit-select" style="padding: 5px; width: 200px;">
                    <option value="">Select Spirit</option>
                </select>
            </div>
            <div class="button-group" style="display: flex; flex-direction: row; gap: 10px; margin: 10px 0; justify-content: center;">
                <button id="post-command">Post as Spirit</button>
                <button id="refresh-timeline">Timeline</button>
                <button id="clear-timeline">Clear</button>
                <button id="load-spirit">Load Spirit</button>
            </div>
            <div id="timeline"></div>
            <div id="selected-post" style="display: none;"></div>
        </div>
    `;

    // Event delegation
    hub.addEventListener('click', async (e) => {
        const spiritName = document.getElementById('spirit-select')?.value || '';
        const target = e.target;

        if (target.id === 'post-command') {
            if (!spiritName) {
                alert('Please select a spirit.');
                return;
            }
            const content = prompt('Speak your post:');
            if (!content) return;
            await savePost(content, null, spiritName);
            await loadTimeline();
        } else if (target.id === 'refresh-timeline') {
            activeView = 'timeline';
            activeSpirit = null;
            activeSpiritView = 'posts';
            await loadTimeline();
        } else if (target.id === 'clear-timeline') {
            if (!confirm("Dissolve all posts from the timeline? This cannot be undone.")) return;
            await clearTimeline();
        } else if (target.id === 'load-spirit') {
            if (!spiritName) {
                alert('Please select a spirit.');
                return;
            }
            activeView = 'sheet';
            activeSpirit = spiritName;
            activeSpiritView = 'posts';
            await loadSpiritSheet(spiritName);
        } else if (target.classList.contains('reply-button')) {
            const postId = target.getAttribute('data-post-id');
            const responderName = document.getElementById('spirit-select')?.value || '';

            if (!responderName) {
                alert('Select a spirit to reply with.');
                return;
            }
            if (!postId) {
                console.warn('Reply button missing data-post-id attribute');
                return;
            }

            console.log('[Spirit Auto-Reply] Invoking replyToPost from:', responderName, '→ Post ID:', postId);

            // Call the full automatic reply function you already have
            await replyToPost(postId, responderName);
        } else if (target.id === 'recent-posts-btn') {
            activeSpiritView = 'posts';
            await updateSpiritPosts(activeSpirit);
        } else if (target.id === 'recent-replies-btn') {
            activeSpiritView = 'replies';
            await updateSpiritReplies(activeSpirit);
        } else if (target.closest('.post-box')) {
            const postId = target.closest('.post-box').id.replace('post-', '');
            activeView = 'post';
            activeSpiritView = 'posts';
            await showSelectedPost(postId);
        }
    });

    // Initial load
    refreshSpiritDropdown();
    activeView = 'timeline';
    await loadTimeline();

    // Auto-refresh intervals
    if (!spiritPostInterval) {
        updateSpiritPostInterval();
    }
    if (spiritReplyIntervals.length === 0) {
        updateSpiritReplyIntervals();
    }

    // Auto-refresh dropdown every 2 seconds
    setInterval(refreshSpiritDropdown, 2000);

    // Periodic cleanup
    cleanupLoyaltyData();

    console.log('Home Hub initialized: Auto-refresh enabled');
});