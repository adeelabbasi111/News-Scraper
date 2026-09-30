document.addEventListener('DOMContentLoaded', () => {
    const radioButtons = document.querySelectorAll('input[name="contentType"]');
    const estimateBox = document.getElementById('creditEstimate');
    const form = document.getElementById('researchForm');
    const progressArea = document.getElementById('progressArea');
    const progressLog = document.getElementById('progressLog');
    
    async function updateEstimate() {
        const selected = document.querySelector('input[name="contentType"]:checked').value;
        const res = await fetch(`/api/credits/estimate?content_type=${selected}`);
        const data = await res.json();
        estimateBox.textContent = `Estimated Usage: ${data.estimated_credits} credits`;
    }

    radioButtons.forEach(radio => radio.addEventListener('change', updateEstimate));

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const payload = {
            topic: document.getElementById('topic').value,
            category: document.getElementById('category').value,
            content_type: document.querySelector('input[name="contentType"]:checked').value,
            time_range: document.getElementById('timeRange').value
        };
        
        try {
            const res = await fetch('/api/research/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            
            if (res.ok) {
                progressArea.classList.remove('hidden');
                progressLog.innerHTML = `<p>Job ${data.id} Started. Status: ${data.status}...</p>`;
                pollStatus(data.id);
            } else {
                alert(`Error: ${data.detail}`);
            }
        } catch(e) {
            console.error(e);
            alert("Failed to start research");
        }
    });

    async function pollStatus(jobId) {
        const interval = setInterval(async () => {
            const res = await fetch(`/api/research/${jobId}/status`);
            const data = await res.json();
            
            progressLog.innerHTML = `<p>Current Status: <strong>${data.status}</strong></p>`;
            
            if (data.status === 'completed' || data.status === 'failed') {
                clearInterval(interval);
                if (data.status === 'completed') {
                    let pdfHtml = data.pdf_url ? `<a href="${data.pdf_url}" target="_blank" download style="display:inline-block; margin-top:10px; background-color:#28a745; color:white; padding:8px 15px; text-decoration:none; border-radius:4px; font-weight:bold;">📄 Download PDF Script</a>` : '';
                    
                    progressLog.innerHTML += `
                        <h4 style="color: green;">Research Completed Successfully!</h4>
                        <h4>Final Script:</h4>
                        <textarea style="width: 100%; height: 200px;" readonly>${data.final_script}</textarea>
                        ${pdfHtml}
                    `;
                } else if (data.status === 'failed') {
                    progressLog.innerHTML += `
                        <div style="background: #fee; padding: 10px; border: 1px solid red; border-radius: 4px; margin-top: 10px;">
                            <h4 style="color: red; margin-top: 0;">Job Failed</h4>
                            <p style="color: darkred; font-family: monospace;"><strong>Error:</strong> ${data.error_message || 'Unknown error'}</p>
                            <p style="font-size: 0.9em; color: #666;">Your credits have been refunded.</p>
                        </div>
                    `;
                }
            }
        }, 2000);
    }
});
