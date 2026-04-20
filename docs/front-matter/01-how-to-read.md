# How to Read a Module

Every module in this compendium follows the same section order. Once you know the pattern, you can find any part of any module without searching.

## Section Order

| Section | Purpose |
|---|---|
| **Learning Objectives** | What you will be able to do after finishing this module. Written as capability statements, not topic lists. |
| **Prerequisites** | What you genuinely need to know first. If a module is listed here, you should complete it before this one. |
| **The Problem** | A short framing paragraph (two to four sentences) that explains why this topic exists and what gap it fills. |
| **Core Content** | The full lesson, broken into named subsections. Each subsection covers one concept. |
| **Vendor Implementations** | How major vendors implement the concept in configuration syntax. Only present where vendor differences are meaningful. |
| **Common Pitfalls** | The mistakes that engineers most commonly make with this topic, and how to diagnose and fix them. |
| **Practice Problems** | Questions that require you to apply the material, not just recall it. Answers are provided but collapsed. |
| **Lab** | A hands-on exercise with specific steps and expected output. Uses Packet Tracer, GNS3, Containerlab, or vendor simulators. |
| **Summary and Key Takeaways** | A synthesis of the module from a different angle. This section does not repeat Core Content; it reframes it. |
| **Where to Next** | Forward pointers to the next module in sequence and to related topics. |
| **Standards and Certifications** | The formal standards that define this topic, and where it appears in major certification syllabi. |
| **References** | Authoritative sources: RFCs, IEEE standards, vendor documentation, textbooks. |
| **Attribution and Licensing** | Who wrote it, what AI assistance was used, and the licence for the content. |

## Supplementary Notes

Sections marked with a collapsed block on the web (the triangle or arrow icon) contain supplementary detail. In this PDF, these appear as indented note blocks below the relevant paragraph. They cover deeper technical background, historical context, or edge cases that are useful but not essential for a first read.

You do not need to read supplementary blocks to understand the core content of a module. Treat them as optional depth for when you want to know more.

## The `human_reviewed` Flag

Every module's frontmatter contains a `human_reviewed` field. When this is `false`, the module was drafted with AI assistance and has been checked against authoritative sources, but has not yet been reviewed by a subject-matter expert. Content may be accurate but should be verified against the cited references before use in production or formal study.

When `human_reviewed` is `true`, a named contributor has reviewed the module's technical claims against authoritative sources and approved the content.

## Reading the Practice Problems

Practice problems are written to require application, not recall. A question like "what is an MTU?" tests recall. A question like "a customer reports that SSH sessions connect fine but SCP transfers to the same host die after a few seconds - what is the most likely cause and how would you confirm it?" requires you to apply what you have learned.

Work through problems before expanding the answers. The reasoning in the answer is as important as the result.
