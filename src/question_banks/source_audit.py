SOURCE_AUDIT = {
    "aptitude": {
        "dataset": "Prathamesh25/aptitude-qa-dataset",
        "url": "https://huggingface.co/datasets/Prathamesh25/aptitude-qa-dataset",
        "revision": "7d42f47480a84445215eb35b9ca724e74a76255b",
        "declared_license": "Apache-2.0",
        "available_rows": 1769,
        "inspected_rows": 1769,
        "imported_rows": 0,
        "filtered_rows": 1769,
        "decision": (
            "Filtered because records are chat-style question/solution pairs without answer "
            "choices; the live aptitude flow requires four choices and a numeric answer index. "
            "Generating distractors would change the source questions and could introduce "
            "incorrect answer options. No source records were modified or added to the live bank."
        ),
    },
    "stack_exchange": {
        "url": "https://data.stackexchange.com/",
        "licensing_url": "https://stackoverflow.com/help/licensing",
        "schema_sample_source": "https://api.stackexchange.com/2.3/questions",
        "inspected_records": 1,
        "imported_records": 0,
        "decision": (
            "The sampled public post contains HTML body, title, tags, and a post-specific "
            "content_license. Stack Exchange states that contributions carry date-dependent "
            "CC BY-SA terms. No post content was copied; use original GenAssess questions "
            "until attribution and ShareAlike requirements are deliberately supported."
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
        "inspected_rows": 10,
        "imported_rows": 5,
        "filtered_rows": 5,
        "decision": (
            "Five manually reviewed sanitized tasks were normalized with source task IDs, "
            "solutions, and test cases. Five of the first ten reviewed records were not "
            "selected for this initial seed due to ambiguity, limited scope, or concerns "
            "identified during static review. Stored solutions and tests are inert data."
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
            "The data has prompt, canonical solution, test code, and entry point fields, "
            "but was not imported because MBPP is the initial coding source and no isolated "
            "execution sandbox exists. The dataset card also warns that generated code is "
            "untrusted and requires safe execution."
        ),
    },
}
