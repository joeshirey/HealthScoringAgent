document.addEventListener('DOMContentLoaded', () => {
    const evaluateBtn = document.getElementById('evaluate-btn');
    const validateBtn = document.getElementById('validate-btn');
    const resultsCard = document.getElementById('results-card');
    const resultsContent = document.getElementById('results-content');
    const validationContent = document.getElementById('validation-content');

    let lastEvaluationResult = null;
    let lastCode = '';
    let lastLanguage = '';

    evaluateBtn.addEventListener('click', async () => {
        const codeInput = document.getElementById('code-input').value;
        const languageInput = document.getElementById('language-input').value;
        const githubUrlInput = document.getElementById('github-url-input').value;

        let requestBody;
        let endpoint;

        if (githubUrlInput) {
            endpoint = '/evaluate-from-url';
            requestBody = { github_url: githubUrlInput };
        } else {
            endpoint = '/evaluate';
            requestBody = { code: codeInput, language: languageInput };
            lastCode = codeInput;
            lastLanguage = languageInput;
        }

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            lastEvaluationResult = data.results;
            if (!githubUrlInput) {
                lastCode = codeInput;
            } else {
                // We don't have the code locally if it's from a URL,
                // so we can't validate it yet. A future improvement
                // would be to return the fetched code from the backend.
                validateBtn.style.display = 'none';
            }
            lastLanguage = languageInput;


            displayEvaluationResults(data.results);
            resultsCard.style.display = 'block';
            if(lastCode) {
                validateBtn.style.display = 'block';
            }

        } catch (error) {
            resultsContent.innerHTML = `<p>Error: ${error.message}</p>`;
            resultsCard.style.display = 'block';
        }
    });

    validateBtn.addEventListener('click', async () => {
        if (!lastEvaluationResult || !lastCode) {
            alert('Please run an evaluation first.');
            return;
        }

        const requestBody = {
            code: lastCode,
            language: lastLanguage,
            evaluation_results: lastEvaluationResult
        };

        try {
            const response = await fetch('/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            displayValidationResult(data.validation);

        } catch (error) {
            validationContent.innerHTML = `<p>Error: ${error.message}</p>`;
        }
    });

    function displayEvaluationResults(results) {
        let html = `<h3>Overall Score: ${results.score}</h3>`;
        html += '<ul>';
        for (const key in results) {
            if (key !== 'score' && key !== 'recommendations' && key !== 'score_breakdown') {
                html += `<li><strong>${key.replace(/_/g, ' ')}:</strong> ${results[key]}</li>`;
            }
        }
        html += '</ul>';

        if (results.recommendations && results.recommendations.length > 0) {
            html += '<h4>Recommendations:</h4>';
            html += '<ul>';
            results.recommendations.forEach(rec => {
                html += `<li>${rec}</li>`;
            });
            html += '</ul>';
        }
        resultsContent.innerHTML = html;
        validationContent.innerHTML = '';
    }

    function displayValidationResult(validation) {
        let html = `<h4>Validation Summary:</h4>`;
        html += `<p><strong>Evaluation Correct:</strong> ${validation.is_evaluation_correct}</p>`;
        html += `<p><strong>Agreement Score:</strong> ${validation.agreement_score}</p>`;
        html += `<p><strong>Summary:</strong> ${validation.summary}</p>`;

        if (validation.discrepancies && validation.discrepancies.length > 0) {
            html += '<h5>Discrepancies:</h5>';
            html += '<ul>';
            validation.discrepancies.forEach(disc => {
                html += `<li><strong>${disc.criterion_name}:</strong> ${disc.finding}</li>`;
            });
            html += '</ul>';
        }
        validationContent.innerHTML = html;
    }
});
