p='src/question_banks/source_audit.py'
s=open(p).read()
# insert faqguru entry before final closing brace
entry='''
    "faqguru": {
        "dataset": "FAQGURU/FAQGURU",
        "url": "https://github.com/FAQGURU/FAQGURU",
        "revision": "master",
        "declared_license": "MIT",
        "available_rows": 1599,
        "inspected_rows": 1599,
        "imported_rows": 1599,
        "filtered_rows": 0,
        "decision": (
            "Imported 1,599 validated technical interview Q&A records from the MIT-licensed "
            "FAQGURU repository across SQL, Java, C/C++, JavaScript, .NET, cloud, web, "
            "DSA, DBMS, and software engineering topics. Used to replace the unresolved-license "
            "Software Interview Questions dataset."
        ),
    },
'''
s=s.rstrip()
# remove last }
idx=s.rfind('}')
s=s[:idx]+entry+s[idx:]
open(p,'w').write(s)
print('done')