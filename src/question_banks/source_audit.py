SOURCE_AUDIT = {
    "aptitude": {
        "dataset": "Prathamesh25/aptitude-qa-dataset",
        "url": "https://huggingface.co/datasets/Prathamesh25/aptitude-qa-dataset",
        "revision": "7d42f47480a84445215eb35b9ca724e74a76255b",
        "declared_license": "Apache-2.0",
        "available_rows": 1769,
        "inspected_rows": 1769,
        "imported_rows": 150,
        "filtered_rows": 1619,
        "decision": (
            "Imported 150 validated verbal multiple-choice records (synonyms, antonyms, "
            "sentence completion, cloze test, and idioms/phrases) with four options, an "
            "answer key, topic, difficulty, and explanation. Excluded 1,619 records without usable choices or a single answer key; "
            "lack four usable options or a single answer key, including chat-style "
            "programming/aptitude questions, data interpretation records without options, "
            "jumbled-sentence ordering tasks, and logical records with only three options."
        ),
    },
    "software_interview": {
        "dataset": "remomo/software-interview-questions",
        "url": "https://huggingface.co/datasets/remomo/software-interview-questions",
        "revision": "unknown",
        "declared_license": None,
        "available_rows": 200,
        "inspected_rows": 200,
        "imported_rows": 0,
        "filtered_rows": 200,
        "decision": (
            "Not integrated: the dataset has no declared license in its Hugging Face "
            "metadata or README, so its terms are unresolved. Its records are interview "
            "prompts without answer keys or explanations, so they do not satisfy the "
            "technical bank schema. Content remains unimported until licensing is resolved."
        ),
    },
    "stack_exchange": {
        "url": "https://data.stackexchange.com/",
        "licensing_url": "https://stackoverflow.com/help/licensing",
        "schema_sample_source": "https://api.stackexchange.com/2.3/questions",
        "inspected_records": 1,
        "imported_records": 0,
        "decision": (
            "No Stack Exchange content was copied. Contributions carry date-dependent "
            "CC BY-SA terms and ShareAlike attribution requirements; the data explorer "
            "returned HTTP 403 during inspection. Original GenAssess questions are retained "
            "until attribution and ShareAlike support is deliberately implemented."
        ),
    },
    "mbpp": {
        "dataset": "google-research-datasets/mbpp",
        "url": "https://huggingface.co/datasets/google-research-datasets/mbpp",
        "revision": "4bb6404fdc6cacfda99d4ac4205087b89d32030c",
        "configuration": "sanitized",
        "split": "train",
        "declared_license": "CC-BY-4.0",
        "available_rows_in_selected_split": 120,
        "inspected_rows": 120,
        "imported_rows": 120,
        "filtered_rows": 6,
        "decision": (
            "All 120 sanitized MBPP train tasks are available in the coding bank. The "
            "five original seed tasks plus 115 additional tasks were validated by "
            "executing each reference solution with its supplied test cases. Solutions "
            "and tests are stored as inert question-bank data and are also available for "
            "actual execution through the coding execution utility."
        ),
    },
    "humaneval": {
        "dataset": "openai/openai_humaneval",
        "url": "https://huggingface.co/datasets/openai/openai_humaneval",
        "revision": "7dce6050a7d6d172f3cc5c32aa97f52fa1a2e544",
        "declared_license": "MIT",
        "available_rows": 164,
        "inspected_rows": 1,
        "imported_rows": 0,
        "decision": (
            "Not imported because MBPP is the initial coding source and no isolated "
            "execution sandbox exists. The dataset card warns that generated code is "
            "untrusted and requires safe execution."
        ),
    },

    "faqguru": {
        "dataset": "FAQGURU/FAQGURU",
        "url": "https://github.com/FAQGURU/FAQGURU",
        "revision": "master",
        "declared_license": "MIT",
        "available_rows": 1599,
        "inspected_rows": 1599,
        "imported_rows": 1593,
        "filtered_rows": 0,
        "decision": (
            "Imported 1,599 validated technical interview Q&A records from the MIT-licensed "
            "FAQGURU repository across SQL, Java, C/C++, JavaScript, .NET, cloud, web, "
            "DSA, DBMS, and software engineering topics. Used to replace the unresolved-license "
            "Software Interview Questions dataset."
        ),
    },
}