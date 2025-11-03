document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('animation-container');
    if (!container) {
        return;
    }

    // Get all our elements (unchanged)
    const senderNode = document.getElementById('node-sender');
    const receiverNode = document.getElementById('node-receiver');
    const message = document.getElementById('message');
    const explanationText = document.getElementById('explanation-text');
    const flashPlaceholder = document.getElementById('flash-message-placeholder');
    
    let animationSteps = [];
    let nodeMap = {};
    let finalMessage = "";
    let redirectUrl = ""; 

    try {
        animationSteps = JSON.parse(container.dataset.steps);
        nodeMap = JSON.parse(container.dataset.nodes);
        finalMessage = container.dataset.finalMessage;
        redirectUrl = container.dataset.redirectUrl;
    } catch (e) {
        console.error('Failed to parse data:', e);
        return;
    }

    if (animationSteps.length === 0) {
        return;
    }
    
    // --- The Main Animation Loop ---

    const stepDelay = 3000;
    const flashDelay = 1000;
    const redirectDelay = 2000;
    const resultsDelay = 1500; // * NEW: 1.5 sec pause after flash, before showing results

    function showStep(index) {
        
        // --- This is a normal animation step (unchanged) ---
        if (index < animationSteps.length) {
            const step = animationSteps[index];
            const [sender, receiver, explanation, type] = step;
            
            const senderData = nodeMap[sender];
            const receiverData = nodeMap[receiver];

            // 1. Update content and style
            if (senderData) {
                senderNode.innerHTML = `${senderData.emoji} ${sender}`;
                senderNode.className = `node ${senderData.class}`;
            }
            if (receiverData) {
                receiverNode.innerHTML = `${receiverData.emoji} ${receiver}`;
                receiverNode.className = `node ${receiverData.class}`;
            }
            
            // 2. Reset styles
            explanationText.textContent = explanation;
            explanationText.classList.remove('done');
            message.style.display = 'block';
            flashPlaceholder.innerHTML = '';
            
            // 3. Set message color
            message.classList.toggle('response', type === 'response');

            // 4. Show container
            if (index === 0) {
                container.style.display = 'block';
            }
            
            // 5. Play animation
            container.classList.remove('is-animating', 'request', 'response');
            setTimeout(() => {
                container.classList.add('is-animating', type);
            }, 10); 

            // 6. Wait, then show the next step
            setTimeout(() => {
                showStep(index + 1);
            }, stepDelay);

        // --- "Done" step (unchanged) ---
        } else if (index === animationSteps.length) {
            
            message.style.display = 'none';
            explanationText.innerHTML = 'Done! ✔️';
            explanationText.classList.add('done');
            setTimeout(showFlashMessage, flashDelay);
        }
    }

    // --- Function to show the flash message (UPDATED) ---
    function showFlashMessage() {
        // 1. Show the flash message
        if (finalMessage) {
            flashPlaceholder.innerHTML = `<div class="flash-message">${finalMessage}</div>`;
        }
        
        // 2. *NEW*: Find the results div
        const resultsDiv = document.getElementById('search-results-content');
        
        // 3. *NEW*: Set a timeout to hide the animation and show the results
        //    (This happens *after* the flash message appears)
        setTimeout(() => {
            // Hide the entire animation box
            container.style.display = 'none';
            
            // Show the search results content
            if (resultsDiv) {
                resultsDiv.style.display = 'block';
            }
        }, resultsDelay); // Wait 1.5 seconds

        
        // 4. (Unchanged) Redirect if a URL is provided (for data entry pages)
        //    This runs on its own timer.
        if (redirectUrl) {
            setTimeout(() => {
                window.location.href = redirectUrl;
            }, redirectDelay);
        }
    }

    // Start the whole sequence!
    showStep(0);
});