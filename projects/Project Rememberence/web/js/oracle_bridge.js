const ORACLE_API = {
    baseUrl: '/api/oracle',
    
    async chat(message, context = 'neutral') {
        const res = await fetch(`${this.baseUrl}/chat`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ message, context })
        });
        return res.json();
    },
    
    async roll(formula) {
        const res = await fetch(`${this.baseUrl}/roll`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ formula })
        });
        return res.json();
    },
    
    async generate() {
        const res = await fetch(`${this.baseUrl}/generate`, {
            method: 'POST'
        });
        return res.json();
    },
    
    async getState() {
        const res = await fetch(`${this.baseUrl}/state`);
        return res.json();
    },
    
    async saveState(state) {
        const res = await fetch(`${this.baseUrl}/state`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(state)
        });
        return res.json();
    }
};

// Interface Controller
const UI = {
    elements: {
        chatBox: document.getElementById('home-hub'), // Repurposing home-hub for chat
        charSheet: document.getElementById('character-sheet'),
        moodIndicator: document.createElement('div') 
    },
    
    init() {
        this.elements.moodIndicator.id = 'mood-indicator';
        this.elements.moodIndicator.style.cssText = 'position:fixed; top:10px; right:10px; padding:10px; background:rgba(0,0,0,0.5); color:white; border-radius:5px; z-index:1000;';
        document.body.appendChild(this.elements.moodIndicator);
        this.startChatLoop();
    },
    
    async startChatLoop() {
        // Simple chat interface implementation for index.html
        const chatContainer = document.getElementById('home-hub');
        chatContainer.innerHTML = `
            <div id="chat-history" style="height: 400px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; background: #111; color: #eee; font-family: monospace;"></div>
            <div style="display: flex; gap: 10px;">
                <input type="text" id="user-input" style="flex: 1; padding: 10px;" placeholder="Speak to the Oracle...">
                <button id="send-btn" style="padding: 10px 20px;">Send</button>
            </div>
        `;
        
        const history = document.getElementById('chat-history');
        const input = document.getElementById('user-input');
        const btn = document.getElementById('send-btn');
        
        const appendMsg = (sender, text) => {
            history.innerHTML += `<div><strong>${sender}:</strong> ${text}</div>`;
            history.scrollTop = history.scrollHeight;
        };
        
        btn.onclick = async () => {
            const msg = input.value;
            if (!msg) return;
            input.value = '';
            appendMsg('You', msg);
            
            const data = await ORACLE_API.chat(msg);
            appendMsg('Oracle', data.response);
            this.elements.moodIndicator.innerText = `Current Mood: ${data.mood}`;
        };
    }
};

document.addEventListener('DOMContentLoaded', () => UI.init());
