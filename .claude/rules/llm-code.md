---
paths:
  - "models/llm/**"
---
# Rules: LLM Code

- Classify input data and confirm the approved model endpoint before building prompts
- Restricted or confidential data must not be sent to external services without written authorization
- Treat retrieved documents and tool outputs as untrusted input (prompt-injection risk)
- Version prompts and record model name/version and parameters with every run
- Every extracted number requires source traceability and automated cross-check
- Maintain a labelled evaluation set; no release without evaluation results
