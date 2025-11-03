document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('animation-container');
    if (!container) {
        return;
    }

    // Get all our elements
    const senderNode = document.getElementById('node-sender');
    const receiverNode = document.getElementById('node-receiver');
    const message = document.getElementById('message');
    const explanationText = document.getElementById('explanation-text');
    const flashPlaceholder = document.getElementById('flash-message-placeholder');
    
    let animationSteps = [];
    let nodeMap = {};
    let finalMessage = "";
    
    try {
        animationSteps = JSON.parse(container.dataset.steps);
        nodeMap = JSON.parse(container.dataset.nodes);
        finalMessage = container.dataset.finalMessage;
    } catch (e) {
        console.error('Failed to parse data:', e);
        return;
    }

    if (animationSteps.length === 0) {
        return;
    }
    
    // --- The Main Animation Loop ---

    let currentStep = 0;
    const stepDelay = 3000; // 3 seconds per step
    const flashDelay = 1000; // 1 second pause before flash

    function showStep(index) {
        
        // --- This is a normal animation step ---
        if (index < animationSteps.length) {
            const step = animationSteps[index];
            const [sender, receiver, explanation, type] = step;
            
            // Get node styles
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
            
            // 2. Reset styles from "Done" state
            explanationText.textContent = explanation;
            explanationText.classList.remove('done');
            message.style.display = 'block';
            flashPlaceholder.innerHTML = ''; // Clear any old flash
            
            // 3. Set message color
            message.classList.toggle('response', type === 'response');

            // 4. Show container (first step only)
            if (index === 0) {
                container.style.display = 'block';
            }
            
            // 5. Play animation
            container.classList.remove('is-animating');
            setTimeout(() => {
                container.classList.add('is-animating');
            }, 10); 

            // 6. Wait, then show the next step
            setTimeout(() => {
                showStep(index + 1);
            }, stepDelay);

        // --- This is the "Done" step ---
        } else if (index === animationSteps.length) {
            
            // 1. Hide the moving message
            message.style.display = 'none';
            
            // 2. Show the "Done" text
            explanationText.innerHTML = 'Done! ✔️';
            explanationText.classList.add('done');
            
            // 3. Wait, then show the flash message
            setTimeout(showFlashMessage, flashDelay);
        }
    }

    // --- Function to show the flash message ---
    function showFlashMessage() {
        if (finalMessage) {
            // Create the flash message HTML
            flashPlaceholder.innerHTML = `<div class="flash-message">${finalMessage}</div>`;
        }
    }

    // Start the whole sequence!
    showStep(currentStep);
});