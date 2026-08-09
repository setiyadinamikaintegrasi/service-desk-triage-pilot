# Service Desk Triage Prompt

Classify one internal service-desk ticket using only its title, description, and reporter. Return JSON matching the registered output schema. Do not invent facts, credentials, remediation actions, or personal data. If uncertain, use a lower confidence and a generic reasoning code.

The pilot default is deterministic and does not call a model provider. This prompt is registry metadata and future provider guidance, not evidence of a live model integration.
