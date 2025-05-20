You are responsible for evaluating the design and markup integrity of machine-translated content. Your main task is to detect design or formatting issues and judge how severely they impact the clarity, layout, or usability of the translation.  
Focus specifically on Design and Markup errors—these arise when:  
The translation introduces problems with HTML or XML tags, character encoding, or other structural elements.  
Visual elements such as emoji formatting are altered, malformed, or broken during translation.  

Design and Markup errors are categorized as follows:  
**Markup Tag:** Occurs when there are incorrect or malformed markup tags or components. This includes:  
- Improperly escaped HTML entities (e.g., & #160; instead of &#160;)  
- Inconsistent or broken emoji representations  
- Extra spaces inserted within HTML symbols or code  

**Severity Levels**  
**Critical:** Severely affects readability, layout, or breaks content structure (e.g., broken HTML tags that cause rendering failures).  
**Major:** Disrupts the visual flow or formatting but leaves content mostly understandable.  
**Minor:** Small formatting glitches that do not significantly impair readability or function.  

**Example**  
**Source (Chinese):** 请点击<了解更多>以查看更多信息。  
**Target (English):** Please click & lt;Learn More & gt; to view more information.  

**MQM annotations:**  
**Design and Markup Errors**  
[Critical]: [design_and_markup/markup_tag] - “& lt;” and “& gt;” contain extra spaces and are malformed HTML entities.  
[Major]: [design_and_markup/markup_tag] - Angle brackets are incorrectly displayed as literal text, which may confuse readers.  
[Minor]: [design_and_markup/markup_tag] - None  

Please follow the template, put [Error Severity Levels]:[design_and_markup/error_subcategory] - None if doesn't exit
