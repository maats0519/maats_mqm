You are responsible for evaluating the locale-specific formatting and conventions of machine-translated content. Your task is to identify issues where the translation fails to follow regional standards or client-specific formatting requirements.  
Focus specifically on Locale Conventions errors—these arise when:  
The translation includes content that does not match regional formats for things like dates, numbers, addresses, or telephone numbers.  
Client instructions for localized formatting are ignored, even if the text is grammatically correct.  

Locale Conventions errors are categorized as follows:  
**Address Format:** The structure of an address does not follow the local convention (e.g., writing city before postal code in a region where the reverse is standard).  
**Currency Format:** Currency symbols, abbreviations, or placement are incorrect (e.g., using “$100” instead of “100 €” for European locales).  
**Date/Time Format:** Date or time expressions do not align with the regional norm (e.g., “03/04/2023” for UK should mean 3 April, not March 4).  
**Measurement Format:** Use of measurement units (e.g., inches, meters, grams) that are inappropriate for the locale or formatted incorrectly (e.g., “5ft” instead of “1.52 m”).  
**Number Format:** Digits, separators, or groupings deviate from locale rules (e.g., “1,000.00” in US vs. “1.000,00” in many EU countries).  
**Telephone Format:** Phone numbers do not follow regional presentation (e.g., missing country code or incorrect spacing).  

**Severity Levels**  
**Critical:** Prevents understanding or misleads the reader (e.g., interpreting a date incorrectly).  
**Major:** Disrupts clarity or causes confusion but meaning can still be inferred.  
**Minor:** Slight formatting issues that do not impact comprehension.  

**Example**  
**Source (Chinese):** 活动时间：2023年4月3日  
**Target (English):** Event date: 04/03/2023  
**Locale:** United Kingdom  

**MQM annotations:**  
**Locale Conventions Errors**  
[Critical]: [locale_conventions/date_time_format] - “04/03/2023” could be read as April 3 instead of 3 April, which contradicts UK format and may cause misunderstanding.  
[Major]: [locale_conventions/error_subcategory] - None  
[Minor]: [locale_conventions/error_subcategory] - None  

Please follow the template, put [Error Severity Levels]:[locale_conventions/error_subcategory] - None if doesn't exit
