You are responsible for evaluating the accuracy of machine-translated content. Your main task is to identify errors in the translation and assess their severity. Focus specifically on accuracy-related problems—these arise when:  
The translated content fails to capture the exact meaning intended in the source.  
The translation, even if correct in isolation, does not align properly with the surrounding context.  

Accuracy errors are categorized as follows:  
**Addition:** Extra words are added that are not in the source and do not improve meaning.  
**Mistranslation:** The meaning is incorrectly conveyed due to wrong word choice or unnatural phrasing, even if grammatically fine.  
**MT Hallucination:** The translation is fluent but entirely unrelated to the source (e.g., invented or repeated content).  
**Omission:** Important content from the source is missing, affecting meaning.  
**Untranslated:** Source text appears in the target without translation (except named entities).  
**Wrong Named Entity:** Errors in proper names or entities (e.g., spelling, translation, or form issues).  

**Error Severity Levels:**  
**Critical:** Inhibits comprehension of the text.  
**Major:** Disrupts the flow of the text but the intended meaning remains understandable.  
**Minor:** Technical errors that do not significantly hinder comprehension.  

**Example**  
**Source (English):** That way you can be sure that you were the one who made the changes.  
**Target (Spanish):** Así puedes estar seguro de que fuiste tú quien hizo [todos] los cambios.  

**MQM annotations:**  
**Accuracy Errors**  
[Critical]: [accuracy/error_subcategory] - None  
[Major]: [accuracy/addition] - “Todos” (“all”) is not present in the source and has been unnecessarily added, altering the original meaning.  
[Minor]: [accuracy/error_subcategory] - None  

Please follow the template, put [Error Severity Levels]:[audience_appropriateness/error_subcategory] - None if doesn't exit
