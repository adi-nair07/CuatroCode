document.addEventListener('DOMContentLoaded', () => {
    const predictBtn = document.getElementById('predict-btn');
    const btnText = document.getElementById('btn-text');
    const btnLoader = document.getElementById('btn-loader');
    
    // Result elements
    const resultsPanel = document.getElementById('results-panel');
    const errorPanel = document.getElementById('error-panel');
    const resCurrent = document.getElementById('res-current');
    const resPredict = document.getElementById('res-predict');
    const trendGlow = document.getElementById('trend-glow');
    
    const trendContainer = document.getElementById('trend-container');
    const trendIcon = document.getElementById('trend-icon');
    const trendText = document.getElementById('trend-text');

    predictBtn.addEventListener('click', async () => {
        // Reset panels
        resultsPanel.classList.add('hidden');
        resultsPanel.classList.remove('fade-in');
        errorPanel.classList.add('hidden');
        
        // Loader State
        btnText.classList.add('hidden');
        btnLoader.classList.remove('hidden');
        predictBtn.disabled = true;

        try {
            const response = await fetch('/predict', {
                method: 'GET'
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Server error occurred');
            }

            // Populate Results
            resCurrent.textContent = `$${result.current_price.toFixed(2)}`;
            resPredict.textContent = `$${result.predicted_tomorrow.toFixed(2)}`;
            
            // Format styling based on trend
            const trend = result.trend;

            trendContainer.className = 'rounded-xl p-4 flex items-center justify-center gap-3 border backdrop-blur-sm shadow-lg transition-all duration-300';
            
            if (trend === "UP") {
                trendGlow.className = 'absolute inset-0 opacity-20 blur-md z-0 transition-colors duration-300 bg-emerald-500';
                trendContainer.classList.add('bg-emerald-500/10', 'border-emerald-500/30', 'text-emerald-400');
                trendIcon.textContent = '📈';
                trendText.textContent = 'UPTREND ANTICIPATED';
            } else {
                trendGlow.className = 'absolute inset-0 opacity-30 blur-md z-0 transition-colors duration-300 bg-red-500';
                trendContainer.classList.add('bg-red-500/10', 'border-red-500/30', 'text-red-400');
                trendIcon.textContent = '📉';
                trendText.textContent = 'DOWNTREND ANTICIPATED';
            }

            // Show results
            resultsPanel.classList.remove('hidden');
            // Trigger reflow to restart CSS animation
            void resultsPanel.offsetWidth;
            resultsPanel.classList.add('fade-in');

        } catch (error) {
            console.error('Prediction Error:', error);
            errorPanel.textContent = `Prediction failed: ${error.message}`;
            errorPanel.classList.remove('hidden');
            errorPanel.classList.add('fade-in');
        } finally {
            // Revert Button State
            btnText.classList.remove('hidden');
            btnLoader.classList.add('hidden');
            predictBtn.disabled = false;
        }
    });

    // Add subtle interactive tilt effect to card
    const card = document.querySelector('.glass-card');
    document.addEventListener('mousemove', (e) => {
        const xAxis = (window.innerWidth / 2 - e.pageX) / 100;
        const yAxis = (window.innerHeight / 2 - e.pageY) / 100;
        
        // Limit tilt
        const xLimit = Math.max(Math.min(xAxis, 2), -2);
        const yLimit = Math.max(Math.min(yAxis, 2), -2);
        
        card.style.transform = `rotateY(${xLimit}deg) rotateX(${yLimit}deg)`;
    });
    
    // Reset tilt on mouseleave
    document.addEventListener('mouseleave', () => {
        card.style.transform = `rotateY(0deg) rotateX(0deg)`;
    });
});
