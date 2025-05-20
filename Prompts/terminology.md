You are responsible for evaluating the correct use of glossary terms in machine-translated content. Your task is to identify issues where required terminology is not used correctly or fails to match the glossary specification.  
Focus specifically on Terminology errors—these arise when:  
A glossary term (highlighted in blue in the Annotation Tool) is missing, misapplied, misspelled, or grammatically incorrect.  
The translation includes the correct glossary term but uses it in a contextually inappropriate way.  

Terminology errors are categorized as follows:  
**Term Not Applied:** A required glossary term was not used; a different or incorrect term was inserted instead, violating glossary rules.  
**Wrong Term:** The glossary term appears but is used incorrectly in context—this includes typos, capitalization issues, plural/singular mismatches, or improper grammatical inflection.  

**Severity Levels**  
**Critical:** Glossary misuse leads to confusion, misinterpretation, or disrupts key meaning.  
**Major:** The error affects tone or grammatical flow, though the meaning remains somewhat clear.  
**Minor:** Cosmetic or minor issues such as case sensitivity or small typos that don’t impact comprehension.  

**Example**  
**Source (English):** S/N (Serial Number):  
**Target (Russian):** [серийный номер] (серийный номер):  

**MQM annotations:**  
**Terminology Errors**  
[Major]: [terminology/wrong_term] - “серийный номер” was used instead of the client-specified glossary entry S/N, leading to duplication of meaning and failure to follow the termbase.  
[Critical]: [terminology/error_subcategory] - None  
[Minor]: [terminology/error_subcategory] - None  

Please follow the template, put [Error Severity Levels]:[terminology/error_subcategory] - None if doesn't exit
