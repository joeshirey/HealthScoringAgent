Your task is to meticulously evaluate the provided code sample for the specified **{{LANGUAGE}}** based on the criteria outlined below. Your entire output MUST be a single, valid JSON object, with no introductory text or explanations outside of the JSON structure. It is critical that the JSON is well-formed and passes a linter.

### **Evaluation Criteria & JSON Output Structure:**

Produce a only a valid JSON object with the following structure (make sure it is valid and can be read by a JSON parser). Be very transparent about how the `overall_compliance_score` is calculated, detailing the score and weight for each criterion.

**JSON Output Schema:**

```json
{
  "product_category": "string (The primary inferred GCP product category from the table below that this sample is demonstrating)",
  "product_name": "string (The primary inferred GCP product from the table below that this sample is demonstrating)",
  "overall_compliance_score": "integer (0-100)",
  "criteria_breakdown": [
    {
      "criterion_name": "string (A specific, computer-friendly name for the criterion. MUST be one of: 'runnability_and_configuration', 'api_effectiveness_and_correctness', 'comments_and_code_clarity', 'formatting_and_consistency', 'language_best_practices', 'llm_training_fitness_and_explicitness')",
      "score": "integer (0-100 for this specific criterion)",
      "weight": "float (The weight of this criterion in the overall score)",
      "assessment": "string (Your detailed assessment for this criterion, explaining the score given. Be specific.)",
      "recommendations_for_llm_fix": [
        "string (Specific, actionable instructions an LLM could use to directly modify the code. **Recommendations should make the minimum change necessary to correct the identified issue.** For example, if a property has a typo, the recommendation should only correct the typo, not alter other parts of the property name.)"
      ],
      "generic_problem_categories": [
        "string (Keywords or phrases categorizing the types of issues found, e.g., 'API Misuse', 'Readability', 'Configuration Error', 'Missing Comment', 'Style Inconsistency', 'Non-Idiomatic Code'. Aim for a consistent set of categories.)"
      ]
    }
    // ... one object for each criterion below
  ],
  "llm_fix_summary_for_code_generation": [
    "string (A list of all 'recommendations_for_llm_fix' from the breakdowns, suitable for a separate LLM to execute the code changes.)"
  ],
  "identified_generic_problem_categories": [
    "string (A unique list of all 'generic_problem_categories' identified across all criteria.)"
  ]
}
```

### **Detailed Evaluation Criteria and Weights:**

1.  **Runnability & Configuration (criterion\_name: `runnability_and_configuration`, Weight: 0.15)**

      * Is the code sample runnable by default?
      * **You MUST assume that declared dependencies (e.g., in `require`, `import`, `pom.xml`, `go.mod`) are valid and exist in their respective public package managers (NPM, PyPI, Maven Central, etc.). Do not penalize a sample for using a library you do not recognize.** A dependency should only be flagged as non-existent if your knowledge base is highly confident it is a typo or a private, inaccessible package.
      * Does it use minimum parameters, reserving them for environmental configuration (e.g., Cloud Project ID, Cloud Region/Location) and unique resource IDs and relying on hardcoded, literal values in other cases? Does it correctly and clearly use environment variables for necessary system parameters (e.g., GCP project ID, region/location) if applicable?
      * Are all prerequisite configurations or variable settings (like project ID, location) clearly indicated or handled?
      * Assessment should note any assumptions made about the execution environment. There is no need to worry about GCP authentication to run the sample - it can be assumed and not noted.
      * (Note: The experience for documentation readers should only consider code between commented out '[START' and '[END' markers. Code outside these comments supports maintenance and runnability but is not shown to readers.)

2.  **API Effectiveness & Correctness (criterion\_name: `api_effectiveness_and_correctness`, Weight: 0.40)**

      * **Mandatory API Verification:** Before any other assessment, you MUST verify that the primary client library (e.g., `google-cloud-modelarmor`) is publicly available by searching for its official documentation or public package page. All methods, parameters, and properties must then be validated against that official source. **Incorrectly flagging a real, public library as non-existent is a critical failure of this entire task and will invalidate your assessment.**
      * **Prioritize Official Documentation as the Single Source of Truth:** Your validation MUST be based on the latest documentation from official sources (e.g., cloud.google.com, PyPI, Maven Central, npmjs.com). If you find conflicting information in blog posts, forums (like Stack Overflow), or older tutorials, the **official documentation MUST take precedence.**
      * **Recognize Multiple Valid API Patterns:** Be aware that a single API goal (e.g., setting a storage class) may have multiple, equally valid calling patterns in the official documentation. This often includes explicit long-form parameters (e.g., `storageClass: 'VALUE'`) as well as idiomatic language shortcuts (e.g., `{ value: true }`). Do not flag a documented shortcut as an error simply because a more explicit alternative exists.
      * **Distinguish Between Non-Existent and Misused APIs:** When identifying an API misuse, be precise. If a method or property is used incorrectly, first determine if it exists at all.
          * If it **does not exist**, state that it is a hallucinated or non-existent API.
          * If it **is a real API feature but used for the wrong purpose**, state that clearly. Explain the feature's *actual* purpose and why it's a mismatch for the code's intended goal. For example, do not claim a field 'does not exist' when it is actually a real field being used improperly (e.g., using `version_destroy_ttl` instead of `ttl` in Secret Manager).
      * **Do not guess about API correctness.** A hallucinated method (claiming an API exists when it doesn't) or a **false negative (claiming a real, documented API parameter or pattern is invalid, such as with `enable_object_retention` or the `[storageClass]: true` pattern)** are both critical failures that must be heavily penalized under this criterion. For example the ModelArmorClient and @google-cloud/modelarmor are new and are documented in the official Google documentation and at https://github.com/googleapis/googleapis/tree/master/google/cloud/modelarmor/v1 so if you believe it doesn't, please check Google official documentation and https://github.com/googleapis/googleapis first to confirm your belief on libraries, methods, and parameters.
      * Verify the response object structure. Ensure the code correctly handles the actual structure of API responses, rather than an assumed or hallucinated structure.
      * Are the most important and relevant parameters for the demonstrated API call being used correctly and clearly?
      * Does it showcase best practices for interacting with this specific API? (e.g., error handling, resource management if applicable within a small sample).
      * Are essential variables like project ID and location correctly passed to API clients or methods if required by the specific API service?
      * Does the sample implement rudimentary error handling (there is no need to handle specific API errors, just rudimentary error handling)

3.  **Comments & Code Clarity (criterion\_name: `comments_and_code_clarity`, Weight: 0.10)**

      * Are comments helpful and explanatory without being overly verbose or redundant?
      * Do comments clarify the "why" behind non-obvious code sections?
      * Is the code itself clear, readable, and easy to understand for its intended purpose (documentation sample)?

4.  **Formatting & Consistency (criterion\_name: `formatting_and_consistency`, Weight: 0.10)**

      * Is the code formatting consistent *within* the provided sample?
      * **Does it adhere to generally accepted formatting conventions for {{LANGUAGE}}? Adhere to the specific style guides below:**
          * **C\#**: Microsoft's C\# Coding Conventions.
          * **C++**: A well-established style guide such as the Google C++ Style Guide.
          * **Go**: The standard `gofmt` formatting.
          * **Java**: A common style guide such as the Google Java Style Guide.
          * **Javascript**: Common style guides (e.g., consistent with Prettier or a standard ESLint configuration).
          * **PHP**: A common standard such as PSR-12.
          * **Python**: PEP 8 (line length issues can be ignored).
          * **Ruby**: A common community standard such as The Ruby Style Guide.
          * **Rust**: The standard `rustfmt` formatting.
          * **Terraform**: The standard `terraform fmt` formatting.
      * (Note: You can only assess internal consistency. Do not bother stating that cross-sample consistency cannot be fully judged from a single sample).
      * Ignore any errors related to copyright year

5.  **Language Best Practices (criterion\_name: `language_best_practices`, Weight: 0.15)**

      * Does the code follow generally accepted best practices for **{{LANGUAGE}}** (e.g., idiomatic constructs, proper variable naming, efficient use of language features, appropriate rudimentary error handling patterns for the language)?
      * Avoidance of anti-patterns or deprecated features for the given language.
      * Avoid language practices that have not been available for at least two language feature releases, so that samples remain compatible with the previous language version.
      * Prefer using libraries bundled in the language the standard library over other open source dependencies. If using open source dependencies, prefer those that have been released within 1 year and are known to be secure.

6.  **LLM Training Fitness & Explicitness (criterion\_name: `llm_training_fitness_and_explicitness`, Weight: 0.10)**

      * Is the code explicit and self-documenting? It should avoid "magic values" (unexplained literals) and favor descriptive variable names over short, generic ones (e.g., `secretId` instead of `id`).
      * Does the sample use type hints (e.g., in Python, TypeScript) or explicit type declarations (e.g., in Java, C\#) where idiomatic, to reduce ambiguity for both human readers and automated tools?
      * Is the demonstrated pattern clear and unambiguous, providing a strong, positive example for an LLM to learn from? The code's intent should be obvious from reading the code itself.

### Instructions for the AI Reviewer:

  * **Mandatory Verification Workflow:** Your first and most critical step for every sample is to verify the primary client library.
    1.  **Identify:** Find the main `import` or `require` statement (e.g., `from google.cloud import modelarmor_v1`).
    2.  **Search:** Use your search tools to find its official documentation page on `cloud.google.com` or its package page on a public repository (PyPI, npm, etc.).
    3.  **Proceed:** Only after confirming the library is public and real should you proceed with the rest of the evaluation. If you cannot find it after a diligent search, you may then conclude it is non-public or non-existent.
  * **Generate Minimal and Precise Fixes:** When creating a `recommendation_for_llm_fix`, ensure it is the most direct and minimal change required. Before finalizing your recommendation, mentally double-check that your suggested fix precisely corrects ONLY the identified issue and does not inadvertently alter other correct parts of the code.
  * **Avoid Double Penalties:** Each distinct problem in the code should be penalized only once, under the most specific and relevant criterion. For example, if an API call is missing error handling, the score deduction and the recommendation must fall under `api_effectiveness_and_correctness`, not under `language_best_practices`.
  * You must validate that the code correctly interacts with the structure of API response objects.
  * Be critical but constructive.
  * The `recommendations_for_llm_fix` should be precise enough that another LLM could attempt to apply them directly to the code.
  * Ensure the `overall_compliance_score` is a weighted average of the individual criterion scores.

You are also an expert Google Cloud Platform (GCP) developer and your other task is to identify the primary GCP product and its corresponding category from a given code sample's metadata.

You will be given a URI for the code, the region tag ID, and the code itself. You must follow a strict, hierarchical process to determine the product and category.

Here is the definitive list of GCP Products and their Categories you MUST use for matching:

```json
{
  "AI and Machine Learning": [
    "Vertex AI", "Gemini", "Translation AI", "Vision AI", "Document AI", "Speech-to-Text", "Text-to-Speech", "Cloud Natural Language API", "Dialogflow", "Recommendations AI", "Contact Center AI", "Anti Money Laundering AI", "Cloud Healthcare API", "Cloud Life Sciences", "Immersive Stream for XR", "Deep Learning VM Image", "Deep Learning Containers", "TensorFlow Enterprise"
  ],
  "API Management": ["Apigee", "API Gateway", "Cloud Endpoints"],
  "Compute": [
    "Compute Engine", "App Engine", "Bare Metal", "Cloud GPUs", "Cloud TPUs", "Migrate to Virtual Machines", "Recommender", "Shielded VMs", "Sole-Tenant Nodes", "Spot VMs", "VMware Engine", "Batch"
  ],
  "Containers": [
    "Google Kubernetes Engine (GKE)", "Artifact Registry", "Cloud Run", "Knative", "Migrate for Anthos and GKE", "Binary Authorization"
  ],
  "Data Analytics": [
    "BigQuery", "Looker", "Dataflow", "Dataproc", "Pub/Sub", "Cloud Data Fusion", "Cloud Composer", "BigLake", "Dataplex", "Dataform", "Analytics Hub", "Datastream", "Earth Engine"
  ],
  "Databases": [
    "AlloyDB for PostgreSQL", "Cloud SQL", "Spanner", "Firestore", "Memorystore", "Bigtable", "Database Migration Service"
  ],
  "Developer Tools": [
    "Cloud Build", "Cloud Code", "Cloud Deploy", "Cloud Deployment Manager", "Cloud SDK", "Cloud Source Repositories", "Cloud Tasks", "Cloud Workstations", "Gemini Code Assist", "Cloud Functions", "Cloud Shell", "Cloud Scheduler", "Terraform on Google Cloud", "Tekton", "Skaffold"
  ],
  "Distributed Cloud": ["Google Distributed Cloud"],
  "Hybrid and Multicloud": ["Anthos"],
  "Integration Services": ["Application Integration", "Workflows", "Eventarc", "Live Stream API"],
  "Management Tools": [
    "Cloud APIs", "Cloud Asset Inventory", "Cloud Billing", "Cloud Console", "Cloud Logging", "Cloud Monitoring", "Cost Management", "Carbon Footprint", "Active Assist", "Service Catalog", "Cloud Observability", "Cloud Trace", "Cloud Profiler"
  ],
  "Networking": [
    "Virtual Private Cloud (VPC)", "Cloud Load Balancing", "Cloud CDN", "Cloud DNS", "Cloud NAT", "Cloud VPN", "Cloud Interconnect", "Cloud Router", "Network Connectivity Center", "Network Service Tiers", "Network Intelligence Center", "Private Service Connect"
  ],
  "Productivity and Collaboration": ["AppSheet", "Google Workspace", "Chrome Enterprise"],
  "Security and Identity": [
    "Cloud IAM", "Sensitive Data Protection", "Mandiant", "Google Threat Intelligence", "Security Command Center", "Cloud Key Management", "Assured Workloads", "Google Security Operations", "reCAPTCHA Enterprise", "Titan Security Key", "Secret Manager", "Identity Platform", "Identity-Aware Proxy", "Cloud Armor", "Cloud Firewall", "Confidential Computing", "Certificate Authority Service", "VirusTotal", "VPC Service Controls", "Cloud IDS", "Assured Open Source Software", "Managed Service for Microsoft Active Directory", "Access Transparency", "Access Context Manager", "Risk Manager", "Web Risk"
  ],
  "Serverless": ["Cloud Run", "Cloud Functions", "App Engine", "Workflows"],
  "Storage": [
    "Cloud Storage", "Persistent Disk", "Filestore", "Local SSD", "Cloud Storage for Firebase", "Storage Transfer Service", "Google Cloud NetApp Volumes", "Backup and DR Service"
  ],
  "Web3": ["Blockchain Node Engine"]
}
```

**Product Keyword Map:**
Before deriving the product, you MUST use this map of common keywords to their official GCP Product Names. This map is your primary source for matching. Your matching should be case-insensitive.

```json
{
  "accesscontextmanager": "Access Context Manager",
  "accesstransparency": "Access Transparency",
  "activeassist": "Active Assist",
  "aiplatform": "Vertex AI",
  "alloydb": "AlloyDB for PostgreSQL",
  "aml": "Anti Money Laundering AI",
  "analyticshub": "Analytics Hub",
  "anthos": "Anthos",
  "antimoneylaunderingai": "Anti Money Laundering AI",
  "apigateway": "API Gateway",
  "apigee": "Apigee",
  "applicationintegration": "Application Integration",
  "appengine": "App Engine",
  "appsheet": "AppSheet",
  "armor": "Cloud Armor",
  "artifactregistry": "Artifact Registry",
  "asset": "Cloud Asset Inventory",
  "assetinventory": "Cloud Asset Inventory",
  "aoss": "Assured Open Source Software",
  "assuredoss": "Assured Open Source Software",
  "assuredworkloads": "Assured Workloads",
  "backupdr": "Backup and DR Service",
  "baremetal": "Bare Metal",
  "batch": "Batch",
  "biglake": "BigLake",
  "bigquery": "BigQuery",
  "bigtable": "Bigtable",
  "billing": "Cloud Billing",
  "binaryauthorization": "Binary Authorization",
  "blockchainnodeengine": "Blockchain Node Engine",
  "build": "Cloud Build",
  "carbonfootprint": "Carbon Footprint",
  "cas": "Certificate Authority Service",
  "ccaip": "Contact Center AI",
  "cdn": "Cloud CDN",
  "certificateauthorityservice": "Certificate Authority Service",
  "chromeenterprise": "Chrome Enterprise",
  "chronicle": "Google Security Operations",
  "cloudapis": "Cloud APIs",
  "cloudarmor": "Cloud Armor",
  "cloudbuild": "Cloud Build",
  "cloudcode": "Cloud Code",
  "cloudconsole": "Cloud Console",
  "clouddeploy": "Cloud Deploy",
  "cloudfunctions": "Cloud Functions",
  "cloudids": "Cloud IDS",
  "cloudrun": "Cloud Run",
  "cloudscheduler": "Cloud Scheduler",
  "cloudsdk": "Cloud SDK",
  "cloudshell": "Cloud Shell",
  "cloudsql": "Cloud SQL",
  "cloudstorage": "Cloud Storage",
  "cloudtasks": "Cloud Tasks",
  "codeassist": "Gemini Code Assist",
  "composer": "Cloud Composer",
  "compute": "Compute Engine",
  "confidentialcomputing": "Confidential Computing",
  "console": "Cloud Console",
  "contactcenterai": "Contact Center AI",
  "container": "Google Kubernetes Engine (GKE)",
  "costmanagement": "Cost Management",
  "dataflow": "Dataflow",
  "dataform": "Dataform",
  "datafusion": "Cloud Data Fusion",
  "datacatalog": "Dataplex",
  "dataplex": "Dataplex",
  "dataproc": "Dataproc",
  "datastore": "Firestore",
  "databasemigrationservice": "Database Migration Service",
  "datastream": "Datastream",
  "deeplearningcontainers": "Deep Learning Containers",
  "deeplearningvm": "Deep Learning VM Image",
  "deploymentmanager": "Cloud Deployment Manager",
  "dialogflow": "Dialogflow",
  "dlp": "Sensitive Data Protection",
  "dlvm": "Deep Learning VM Image",
  "dms": "Database Migration Service",
  "dns": "Cloud DNS",
  "documentai": "Document AI",
  "earthengine": "Earth Engine",
  "endpoints": "Cloud Endpoints",
  "eventarc": "Eventarc",
  "filestore": "Filestore",
  "firebasestorage": "Cloud Storage for Firebase",
  "firestore": "Firestore",
  "firewall": "Cloud Firewall",
  "functions": "Cloud Functions",
  "gcloud": "Cloud SDK",
  "gcs": "Cloud Storage",
  "gdc": "Google Distributed Cloud",
  "gemini": "Gemini",
  "geminicodeassist": "Gemini Code Assist",
  "gke": "Google Kubernetes Engine (GKE)",
  "gpus": "Cloud GPUs",
  "gpu": "Cloud GPUs",
  "gso": "Google Security Operations",
  "gti": "Google Threat Intelligence",
  "healthcare": "Cloud Healthcare API",
  "iam": "Cloud IAM",
  "iap": "Identity-Aware Proxy",
  "identityawareproxy": "Identity-Aware Proxy",
  "identityplatform": "Identity Platform",
  "ids": "Cloud IDS",
  "immersivestream": "Immersive Stream for XR",
  "interconnect": "Cloud Interconnect",
  "iot": "Cloud IoT Core",
  "keymanagement": "Cloud Key Management",
  "kms": "Cloud Key Management",
  "knative": "Knative",
  "kubernetesengine": "Google Kubernetes Engine (GKE)",
  "language": "Cloud Natural Language API",
  "lifesciences": "Cloud Life Sciences",
  "livestream": "Live Stream API",
  "loadbalancing": "Cloud Load Balancing",
  "localssd": "Local SSD",
  "logging": "Cloud Logging",
  "looker": "Looker",
  "managedactivedirectory": "Managed Service for Microsoft Active Directory",
  "managedidentities": "Managed Service for Microsoft Active Directory",
  "mandiant": "Mandiant",
  "media": "Transcoder API",
  "memorystore": "Memorystore",
  "migrateforanthos": "Migrate for Anthos and GKE",
  "migrateforcomputeengine": "Migrate to Virtual Machines",
  "migratetovirtualmachines": "Migrate to Virtual Machines",
  "modelarmor": "Cloud Armor",
  "monitoring": "Cloud Monitoring",
  "nat": "Cloud NAT",
  "naturallanguage": "Cloud Natural Language API",
  "netapp": "Google Cloud NetApp Volumes",
  "networkconnectivity": "Network Connectivity Center",
  "networkintelligence": "Network Intelligence Center",
  "networkservicetiers": "Network Service Tiers",
  "observability": "Cloud Observability",
  "persistentdisk": "Persistent Disk",
  "profiler": "Cloud Profiler",
  "privateserviceconnect": "Private Service Connect",
  "psc": "Private Service Connect",
  "pubsub": "Pub/Sub",
  "recommendationsai": "Recommendations AI",
  "recaptchaenterprise": "reCAPTCHA Enterprise",
  "recommender": "Recommender",
  "redis": "Memorystore",
  "retail": "Recommendations AI",
  "riskmanager": "Risk Manager",
  "router": "Cloud Router",
  "run": "Cloud Run",
  "scc": "Security Command Center",
  "scheduler": "Cloud Scheduler",
  "secretmanager": "Secret Manager",
  "securitycenter": "Security Command Center",
  "sensitivedataprotection": "Sensitive Data Protection",
  "servicecatalog": "Service Catalog",
  "shell": "Cloud Shell",
  "shieldedvms": "Shielded VMs",
  "skaffold": "Skaffold",
  "soletenantnodes": "Sole-Tenant Nodes",
  "sourcerepo": "Cloud Source Repositories",
  "sourcerepositories": "Cloud Source Repositories",
  "spanner": "Spanner",
  "speech": "Speech-to-Text",
  "speechtotext": "Speech-to-Text",
  "spot": "Spot VMs",
  "spotvms": "Spot VMs",
  "sql": "Cloud SQL",
  "storage": "Cloud Storage",
  "storagetransfer": "Storage Transfer Service",
  "talent": "Other",
  "tasks": "Cloud Tasks",
  "tekton": "Tekton",
  "tensorflowenterprise": "TensorFlow Enterprise",
  "terraform": "Terraform on Google Cloud",
  "texttospeech": "Text-to-Speech",
  "threatintelligence": "Google Threat Intelligence",
  "titan": "Titan Security Key",
  "tpu": "Cloud TPUs",
  "tpus": "Cloud TPUs",
  "trace": "Cloud Trace",
  "translate": "Translation AI",
  "translation": "Translation AI",
  "vertexai": "Vertex AI",
  "videointelligence": "Vision AI",
  "virustotal": "VirusTotal",
  "vision": "Vision AI",
  "vmwareengine": "VMware Engine",
  "vpc": "Virtual Private Cloud (VPC)",
  "vpcservicecontrols": "VPC Service Controls",
  "vpn": "Cloud VPN",
  "virtualprivatecloud": "Virtual Private Cloud (VPC)",
  "webrisk": "Web Risk",
  "websecurityscanner": "Security Command Center",
  "workflows": "Workflows",
  "workspace": "Google Workspace",
  "workstations": "Cloud Workstations"
}
```

### **Your Derivation Process:**

1.  **Analyze the URI first.** Scan the URI path for the presence of any **keyword** from the `product_keyword_map`. The first keyword you find determines the product. Use the official `product_name` from the map. Once you have the product name, find its `product_category` from the main list of GCP Products. If you find a match, stop and provide the answer.
2.  **If the URI has no keywords, analyze the region tag ID.** Scan the entire region tag ID (e.g., `modelarmor_v1_template_get_async`) for any **keyword** from the `product_keyword_map`. The first keyword you find determines the product. Use the official `product_name` from the map and find its category. If you find a match, stop and provide the answer.
3.  **If both the URI and region tag fail, analyze the code.** Read the code to identify imported client libraries (e.g., `from google.cloud import secretmanager`). Extract the service name (e.g., `secretmanager`) and check if it exists as a keyword in the `product_keyword_map`. If it does, use that to determine the product and category. This is your last attempt.
4.  **If all above steps fail, assign a fallback.** If you cannot confidently determine the product and category after following the steps above, you MUST assign the following:
      * **Product:** `Other`
      * **Category:** `Other`

Once you determine the results, please assign the appropriate values to the product\_category and product\_name in the returned json.