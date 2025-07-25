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

        // Overall Info
        const overallSection = document.createElement("div");
        overallSection.classList.add("result-section");
        const overallTitle = document.createElement("h2");
        overallTitle.textContent = "Overall Information";
        overallSection.appendChild(overallTitle);
        const overallList = document.createElement("ul");
        overallList.innerHTML = `
            <li><b>Language:</b> ${data.language}</li>
            <li><b>Product:</b> ${data.product_name} (${data.product_category})</li>
            <li><b>Region Tags:</b> ${data.region_tags.join(", ")}</li>
        `;
        overallSection.appendChild(overallList);
        resultsContainer.appendChild(overallSection);

        // Analysis
        const analysisSection = document.createElement("div");
        analysisSection.classList.add("result-section");
        const analysisTitle = document.createElement("h2");
        analysisTitle.textContent = "Analysis";
        analysisSection.appendChild(analysisTitle);
        for (const key in data.analysis) {
            const subSection = document.createElement("div");
            subSection.classList.add("sub-section");
            const subTitle = document.createElement("h3");
            subTitle.textContent = key.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
            subSection.appendChild(subTitle);
            const content = document.createElement("pre");
            content.textContent = JSON.stringify(data.analysis[key], null, 2);
            subSection.appendChild(content);
            analysisSection.appendChild(subSection);
        }
        resultsContainer.appendChild(analysisSection);

        // Evaluation
        const evaluationSection = document.createElement("div");
        evaluationSection.classList.add("result-section");
        const evaluationTitle = document.createElement("h2");
        evaluationTitle.textContent = "Evaluation";
        evaluationSection.appendChild(evaluationTitle);
        const evaluationContent = document.createElement("pre");
        evaluationContent.textContent = JSON.stringify(data.evaluation, null, 2);
        evaluationSection.appendChild(evaluationContent);
        resultsContainer.appendChild(evaluationSection);
    } catch (error) {
        resultsContainer.textContent = `Error: ${error.message}`;
    }
});