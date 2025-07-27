const githubLinkInput = document.getElementById("github-link");
const analyzeBtn = document.getElementById("analyze-btn");
const resultsContainer = document.getElementById("results");

analyzeBtn.addEventListener("click", async () => {
    const githubLink = githubLinkInput.value;
    if (!githubLink) {
        alert("Please enter a GitHub link.");
        return;
    }

    resultsContainer.textContent = "Analyzing...";

    try {
        const response = await fetch("/analyze_github_link", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ github_link: githubLink }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        resultsContainer.innerHTML = ""; // Clear previous results

        const analysis = data.analysis;
        const validation = data.validation;

        // Overall Info
        const overallSection = document.createElement("div");
        overallSection.classList.add("result-section");
        const overallTitle = document.createElement("h2");
        overallTitle.textContent = "Overall Information";
        overallSection.appendChild(overallTitle);
        const overallList = document.createElement("ul");
        overallList.innerHTML = `
            <li><b>Language:</b> ${analysis.language}</li>
            <li><b>Product:</b> ${analysis.product_name} (${analysis.product_category})</li>
            <li><b>Region Tags:</b> ${analysis.region_tags.join(", ")}</li>
        `;
        overallSection.appendChild(overallList);
        resultsContainer.appendChild(overallSection);

        // Validation
        const validationSection = document.createElement("div");
        validationSection.classList.add("result-section");
        const validationTitle = document.createElement("h2");
        validationTitle.textContent = "Evaluation Validation";
        validationSection.appendChild(validationTitle);
        const validationList = document.createElement("ul");
        validationList.innerHTML = `
            <li><b>Validation Score:</b> ${validation.validation_score}/10</li>
            <li><b>Reasoning:</b> ${validation.reasoning}</li>
        `;
        validationSection.appendChild(validationList);
        resultsContainer.appendChild(validationSection);

        // Detailed Evaluation
        const evaluationSection = document.createElement("div");
        evaluationSection.classList.add("result-section");
        const evaluationTitle = document.createElement("h2");
        evaluationTitle.textContent = "Detailed Evaluation";
        evaluationSection.appendChild(evaluationTitle);
        const evaluationContent = document.createElement("pre");
        evaluationContent.textContent = JSON.stringify(analysis.evaluation, null, 2);
        evaluationSection.appendChild(evaluationContent);
        resultsContainer.appendChild(evaluationSection);
    } catch (error) {
        resultsContainer.textContent = `Error: ${error.message}`;
        console.error(error);
    }
});