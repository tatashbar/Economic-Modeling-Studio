# Results: <project>

<!-- Source of the Word report and the presentation:
       python tools/report.py docx <this file> --out <project>-results.docx
       python tools/report.py pptx <this file> --out <project>-results.pptx
     Each question becomes a slide with the answer next to its first chart, so keep each answer to a few sentences.
     Everything in one folder and zip: python tools/report.py bundle <this file> --out <project>-all-results
     Name code and run folders in backticks (as in the annex) so they are collected.
     One section per question or objective in the note, in the note's order. Charts are embedded with
     ![caption](models/<family>/<name>/output/<run-id>/chart.png); a bold line right above a table becomes its caption. -->

Prepared for: <audience>. Inputs: <note, version or date>; <data files and vintages>. Classification: <level>.

## Summary
1. **<Question 1, in a few words>.** <The answer in one or two sentences, with the key number.>
2. **<Question 2>.** <Answer.>

## 1. <Question or objective 1, as the note states it>

**Answer.** <The answer, the key numbers and how confident we are.>

![<What the chart shows, units and sample>](<path/to/chart.png>)

**<Table title, units>**

| Group | n | Indicator | Value |
|---|---|---|---|

**Method and data.** <Model or method, sample, data sources and vintages; how it differs from the note's method, if the note states one.>

**Caveats.** <What the result depends on; robustness; what was not assessed and why.>

## 2. <Question or objective 2>

## Not assessed
| Question | Reason | What would allow it |
|---|---|---|

## Annex: reproducibility
| Result | Code | Run folder |
|---|---|---|
