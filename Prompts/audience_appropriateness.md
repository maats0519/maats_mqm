You are responsible for evaluating the audience appropriateness of machine-translated content. Your main task is to detect audience appropriateness issues and judge how severely they affect the reader’s experience.  
Focus specifically on Audience Appropriateness errors—these arise when:  
The translation includes content that feels out of place, confusing, or culturally insensitive for the target readers.  
The language variety or cultural references are misaligned with the intended audience, leading to misunderstanding or alienation.  

Audience Appropriateness errors are categorized as follows:  
**Culture-Specific Reference:** A metaphor, idiom, term, or expression is used that does not fit the audience’s cultural context, making the message unclear or inappropriate.  
**Wrong Language Variety:** The translation uses a different regional dialect, spelling, or phrasing than what the audience expects (e.g., UK English instead of US English).  

**Severity Levels**  
**Critical:** Severely hinders understanding or creates major cultural offense or disconnect.  
**Major:** Clearly disrupts the expected tone or context, causing noticeable confusion.  
**Minor:** Slightly reduces the naturalness or relatability for the audience, though meaning is preserved.  

**Example**  
**Source (English):** Please contact our support team if you experience any issues.  
**Target (Japanese):** [お客様ごとに担当者が異なりますので、まずは担当者にご相談ください]  

**MQM annotations:**  
**Audience Appropriateness Errors**  
[Critical]: [audience_appropriateness/error_subcategory] - None  
[Major]: [audience_appropriateness/culture_specific_reference] - The phrase “お客様ごとに担当者が異なりますので…” (“each customer has a different representative”) assumes a Japan-specific corporate support structure that may not reflect the source content. It introduces a culturally specific reference not present in the source and could mislead or confuse international audiences.  
[Minor]: [audience_appropriateness/error_subcategory] - None  

Please follow the template, put [Error Severity Levels]:[audience_appropriateness/error_subcategory] - None if doesn't exit
