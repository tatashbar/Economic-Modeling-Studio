---
paths:
  - "data/**"
  - "pipelines/**"
  - "src/data/**"
---
# Rules: Data Pipelines

- Raw data are immutable; never edit in place
- Every transformation is code with unit tests; no manual spreadsheet edits
- Record source, vintage, retrieval date, license and classification for each dataset
- Keep real-time vintages; never overwrite earlier vintages
- Convert units, currencies and frequencies explicitly and test the conversions
