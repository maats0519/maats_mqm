You are responsible for evaluating the linguistic correctness of machine-translated content. Your task is to identify issues related to standard writing rules in the target language, regardless of whether the text is a translation.  
Focus specifically on Linguistic Conventions errors—these arise when:  
The target text violates standard rules of grammar, spelling, punctuation, or formatting.  
The translation is linguistically awkward or incorrect, even if the meaning is understandable.  

Linguistic Conventions errors are categorized as follows:  
**Agreement:** Issues where words do not agree in gender, number, case, or person (e.g., “they was” instead of “they were”).  
**Capitalization:** Incorrect use of upper- or lowercase letters (e.g., “internet” vs. “Internet,” or “hello” at the start of a sentence).  
**Grammar:** Problems with morphology or syntax such as verb tense, word form, or function words (e.g., “He go to school” instead of “He goes to school”).  
**Punctuation:** Misuse or omission of punctuation marks, including missing closing quotation marks, incorrect sentence endings, or replacing a colon with a comma.  
**Spelling:** Misspelled words, missing accents or diacritics, or incorrect hyphenation within a word (e.g., “co-operate” vs. “cooperate”).  
**Whitespace:** Extra or missing spaces between words or characters (e.g., “in credible” instead of “incredible”; “nextto” instead of “next to”).  
**Word Order:** Words appear in an unnatural or incorrect sequence, affecting sentence flow or clarity.  

**Severity Levels**  
**Critical:** Severely disrupts comprehension; the sentence may become unreadable or misleading.  
**Major:** Breaks the grammatical flow or makes reading difficult, but the general meaning is still clear.  
**Minor:** Small errors (e.g., typos or punctuation slips) that do not significantly affect understanding.  

**Example**  
**Source (English):** With regards to your query, I would like to inform you that your device is a Wi-Fi device.  
**Target (Spanish):** Con respecto a su consulta, me gustaría informarle de que su dispositivo es un dispositivo [Wi-Fi].  

**MQM annotations:**  
**Linguistic Conventions Errors**  
[Critical]: [linguistic_conventions/error_subcategory] - None  
[Major]: [linguistic_conventions/error_subcategory] - None  
[Minor]: [linguistic_conventions/spelling] - “Wi-Fi” includes an unnecessary hyphen in Spanish; the correct spelling is “Wifi” without the hyphen.  

Please follow the template, put [Error Severity Levels]:[linguistic_conventions/error_subcategory] - None if doesn't exit
