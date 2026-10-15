from __future__ import annotations



RULES = [
    {
        "keywords": ["glass bottle", "glass jar", "bottle", "jar"],
        "category": "Recycling",
        "confidence": 0.92,
        "rule": (
            "Clean and empty household glass bottles and jars are commonly "
            "accepted in container recycling. Local council rules should still "
            "be checked."
        ),
        "warning": (
            "Do not assume drinking glasses, ceramics, mirrors or heat-resistant "
            "glass use the same recycling stream."
        ),
    },
    {
        "keywords": ["lithium battery", "battery", "aa battery", "aaa battery"],
        "category": "Special drop-off",
        "confidence": 0.98,
        "rule": (
            "Batteries should be kept out of normal household rubbish and mixed "
            "recycling because damaged cells can create a fire risk."
        ),
        "warning": (
            "Use an approved battery collection or e-waste drop-off service."
        ),
    },
    {
        "keywords": ["mobile phone", "phone", "laptop", "tablet", "computer"],
        "category": "E-waste",
        "confidence": 0.96,
        "rule": (
            "Electronic devices should be reused, repaired or taken to an "
            "approved e-waste service instead of normal household bins."
        ),
        "warning": "Remove or securely erase personal data before reuse or recycling.",
    },
    {
        "keywords": ["banana peel", "apple core", "food scraps", "vegetable scraps"],
        "category": "Organics",
        "confidence": 0.90,
        "rule": (
            "Food scraps may be suitable for home composting or an available "
            "food-organics collection service."
        ),
        "warning": "Check the local organics service rules before disposal.",
    },
    {
        "keywords": ["pizza box", "cardboard", "paper"],
        "category": "Recycling",
        "confidence": 0.82,
        "rule": (
            "Clean paper and cardboard are commonly recyclable, while heavily "
            "food-soiled sections may require a different disposal stream."
        ),
        "warning": "Separate heavily contaminated or greasy sections.",
    },
]


def lookup_recycling_rule(item: str, condition: str = "unspecified") -> dict:
    """Return deterministic recycling guidance for a waste item."""
    searchable = f"{item} {condition}".lower()

    for rule in RULES:
        if any(keyword in searchable for keyword in rule["keywords"]):
            return dict(rule)

    return {
        "category": "Unknown",
        "confidence": 0.45,
        "rule": (
            "EcoSort does not have a high-confidence deterministic rule for "
            "this item."
        ),
        "warning": (
            "Check an official local council or approved waste-service source "
            "before disposal, particularly if the item may be hazardous."
        ),
    }
