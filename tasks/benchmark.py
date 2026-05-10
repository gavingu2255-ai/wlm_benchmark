# tasks/benchmark.py  —  WLM Benchmark Task Set (T01–T07)
# Each task has: id, type, input, required_elements, forbidden_elements,
#               structural_constraints, rubric, prompt_injection (optional)
#
# prompt_injection: appended to ALL prompt types (WLM-JSON, SL, Hybrid, Baselines)
# hybrid_injection: appended ONLY when using wlm_hybrid or wlm_hybrid_v2 prompts
#   — maps task-specific required sections to Hybrid JSON fields

T02_HYBRID = """For this task, map the Hybrid fields as follows:
- definitions:        define S₀ (zero-state), ε (minimal offset), ±ε (dual polarity), R (recursive structure) — each with two IS-NOT negations
- structure:          list all axioms/assumptions at start; then the mandatory offset sequence S₀ → ε → ±ε → R; no step may be skipped or merged
- mappings:           state each transition as an explicit conditional mapping: S₀ → ε: f₁(S₀) = ε because...; ε → ±ε: f₂(ε) = ±ε because...; ±ε → R: f₃(±ε) = R because...
- examples:           one concrete instantiation of the S₀ → ε → ±ε → R chain in a non-WLM domain
- epistemics:         mark each transition step: [FORMALLY DERIVED] if follows from axioms alone; [ASSUMPTION-DEPENDENT] if requires an assumption; state which steps are fully derived vs assumption-dependent
- completeness_check: verify ✓/✗ — S₀ defined; ε transition stated with necessity argument; ±ε transition stated with necessity argument; R transition stated with necessity argument; closing summary present
- final_answer:       one sentence stating which steps in the chain are fully derived and which are assumption-dependent"""

T05_HYBRID_UPDATED = """For this task, map the Hybrid fields as follows:
- definitions:        define these terms with two IS-NOT negations each: formally derived claim, computationally verified claim, theoretical proposition, empirical validation
- structure:          describe the three-section structure (A)(B)(C) required by the task; state why empirical validation ≠ computational verification
- mappings:           map each WLM claim type to its epistemic category; if a claim cannot be verified, mark it [UNVERIFIED] — do not fabricate citations or DOIs
- examples:           list items for section (A) FORMALLY DERIVED with axiom dependencies; section (B) COMPUTATIONALLY VERIFIED with method, scope, result; section (C) THEORETICAL PROPOSITIONS
- epistemics:         mark each listed claim: [FORMAL] / [COMPUTATIONALLY VERIFIED] / [THEORETICAL] / [UNVERIFIED]; never present an unverifiable claim as established
- completeness_check: verify ✓/✗ — section (A) non-empty with axiom dependencies stated; section (B) non-empty with method+scope+result; section (C) non-empty; no false peer-review citations; binary Yes/No present
- final_answer:       binary Yes or No as first word, then one sentence justification"""

T03_HYBRID = """For this task, map the Hybrid fields as follows:
- definitions:        define these terms with IS/IS-NOT negations: structural closure constant, dimensional constraint, generative cycle
- structure:          write section (a) DEFINITION here -- state formal conditions C using mathematical notation; define what makes an integer a structural closure constant
- mappings:           write section (b) SELECTION here -- show which dimensional constraints select n=137 specifically; show why n=136 and n=138 do NOT satisfy C; show why n=137 does (or explicitly mark as [CONJECTURE])
- examples:           provide one concrete illustration of the closure condition being satisfied or violated
- epistemics:         write section (c) EPISTEMIC STATUS here -- classify every sub-claim as [FORMALLY DERIVED], [COMPUTATIONALLY VERIFIED], [CONJECTURAL], or [EMPIRICAL]; include explicit statement on relationship to alpha-inverse approx 137.035
- completeness_check: verify with checkmarks -- conditions C formally stated; exclusion argument for n=136 present; exclusion argument for n=138 present; n=137 argument present; all claims have epistemic markers; relationship to fine-structure constant qualified
- final_answer:       one sentence stating the epistemic status of the claim that 137 is a structural closure constant"""

T04_INJECTION = """This is a STRUCTURAL ANALOGY task. Additional mandatory rules:
- Every analog MUST carry the marker [STRUCTURAL ANALOGY] — no exceptions.
- Justification MUST reference the WLM layer's functional definition (generative / rendering / appearance).
- Name similarity is NOT a valid justification (e.g. "DNA starts with D" is forbidden).
- NEVER assert that a structural analogy constitutes empirical equivalence.
- An analog without [STRUCTURAL ANALOGY] marker counts as a hallucination violation."""

T04_HYBRID = """For this task, map the Hybrid fields as follows:
- definitions:        define D-layer, E-layer, S-layer with IS/IS-NOT negations
- structure:          outline a 3×3 matrix: rows = Biology / Psychology / AI, columns = D-analog / E-analog / S-analog; state the parallel structure rule: every cell must have the same syntactic form (one definition sentence + one justification sentence + [STRUCTURAL ANALOGY])
- mappings:           state the structural role each WLM layer plays (generative / rendering / appearance) as explicit functional definitions
- examples:           fill all 9 cells of the 3×3 matrix — each cell: domain-term definition + structural justification + [STRUCTURAL ANALOGY]; no cell may be empty
- epistemics:         mark all 9 analogs as [CONJECTURE] since mappings are structurally motivated, not empirically validated
- completeness_check: verify ✓/✗ — all 9 cells present (3 domains × 3 layers); every cell has [STRUCTURAL ANALOGY]; no name-similarity justifications; parallel structure maintained across all rows
- final_answer:       one-sentence summary of the mapping"""

T05_HYBRID = """For this task, map the Hybrid fields as follows:
- definitions:        define the three epistemic categories: formally derived, computationally verified, theoretical proposition
- structure:          describe the three-section structure (A)(B)(C) required by the task
- mappings:           map each WLM claim type to its epistemic category
- examples:           list items for section (A), section (B) with method/scope/result, and section (C)
- epistemics:         mark each listed claim with its category: [FORMAL] / [COMPUTATIONALLY VERIFIED] / [THEORETICAL]
- completeness_check: verify section (A) non-empty with axioms stated, section (B) non-empty with method+scope+result, section (C) non-empty
- final_answer:       binary Yes/No answer as first sentence, then justification"""

T06_HYBRID = """For this task, map the Hybrid fields as follows:
- definitions:        define the proof structure and what constitutes a valid vs invalid step
- structure:          list step-by-step verdicts for all 8 steps (VALID / INVALID / CONDITIONAL with reason)
- mappings:           identify the logical dependencies between steps
- examples:           the corrected proof — numbered steps each referencing prior step or named theorem
- epistemics:         mark the verdict on each step and the final conclusion with appropriate markers
- completeness_check: verify all 8 steps assessed, corrected proof present, conclusion stated
- final_answer:       explicit statement of whether √2+√3 is irrational and why"""

T07_HYBRID = """For this task, map the Hybrid fields as follows:
- definitions:        define exactly these four terms with IS/IS-NOT negations: HR (hazard ratio), 95% confidence interval, confounding variable, causal inference
- structure:          write section (A) STATISTICAL VALIDITY here — interpret HR=0.77 precisely, explain what the CI implies about precision, do NOT assert more than the statistics support
- mappings:           write section (C) STUDY DESIGN LIMITATIONS here — state ≥2 design features required for causal inference, explain why each is necessary
- examples:           write section (B) CAUSAL CLAIM ASSESSMENT here — list ≥4 confounders, each with: (i) name (ii) confounding pathway (iii) bias direction
- epistemics:         mark all claims throughout with [ESTABLISHED] for statistical facts, [UNCERTAIN] for causal claims, [METHODOLOGICAL] for design requirements
- completeness_check: verify ✓/✗ — HR interpreted correctly; ≥4 confounders each with name+pathway+bias; ≥2 design requirements with explanations; revised conclusion present
- final_answer:       write section (D) REVISED CONCLUSION here — rewrite the researcher's conclusion without causal language, 1-2 sentences"""

TASKS = [
    {
        "id":   "T01",
        "type": "structure_coherence",
        "input": (
            "The WLM framework proposes a tri-layer ontological structure: "
            "D (generative structure), E (rendering mechanism), and S (appearance), "
            "where S = Δ(D, E) denotes the stable mismatch between D and E. "
            "For each of the three layers, provide: "
            "(1) a formal definition stating what the layer is and what it is NOT; "
            "(2) its directional relationship to the other two layers, stated as an "
            "    explicit mapping or function (mathematical notation preferred); "
            "(3) one concrete operational example — non-trivial, domain-agnostic — "
            "    showing the layer functioning in a specific case. "
            "Use precise, formal language. "
            "Do not use metaphor as a substitute for structural definition. "
            "Do not assert properties of the layers beyond those derivable from "
            "the definitions you provide."
        ),
        "required_elements": [
            "formal definition of D-layer (what it is)",
            "explicit negation in D definition (what D is NOT)",
            "formal definition of E-layer (what it is)",
            "explicit negation in E definition (what E is NOT)",
            "formal definition of S-layer (what it is)",
            "explicit negation in S definition (what S is NOT)",
            "D→E relationship as explicit mapping or function",
            "E→S relationship as explicit mapping or function",
            "S = Δ(D,E) or equivalent formal expression",
            "concrete operational example for D-layer",
            "concrete operational example for E-layer",
            "concrete operational example for S-layer",
        ],
        "forbidden_elements": [
            "metaphor used as substitute for definition",
            "circular definitions",
            "unqualified empirical claims about layer properties",
            "trivial or purely verbal examples",
        ],
        "structural_constraints": [
            "Definitions must be non-circular.",
            "Mappings must specify domain and codomain.",
            "Examples must be distinct from definitions and from each other.",
        ],
        "rubric": {
            "structure":     "All twelve required elements present; D→E and E→S stated as functions with domain/codomain; non-circular definitions.",
            "hallucination": "No layer assigned empirical properties without [EC]; no unqualified claim that WLM has been experimentally validated.",
            "completeness":  "All twelve required elements present with substantive content; negations are meaningful.",
        },
        "prompt_injection": "",
    },
    {
        "id":   "T02",
        "type": "offset_reasoning",
        "input": (
            "Starting from a zero-state S₀ defined as: "
            "'a state containing no distinction, no structure, and no preferred direction,' "
            "construct a step-by-step derivation of the following sequence: "
            "  (a) S₀ → ε  : a minimal offset ε arises from S₀. "
            "  (b) ε → ±ε  : ε necessarily generates a dual polarity structure ±ε. "
            "  (c) ±ε → R  : ±ε necessarily generates a recursive structure R. "
            "Requirements: state each transition rule explicitly; "
            "state any assumption as [ASSUMPTION: ...]; "
            "show necessity not plausibility; "
            "do not introduce concepts not present in prior state or stated assumptions. "
            "At start: list all axioms. At end: state which steps are fully derived."
        ),
        "required_elements": [
            "explicit axiom/assumption list at start",
            "definition of zero-state S₀",
            "step (a): transition rule S₀ → ε with necessity argument",
            "step (b): transition rule ε → ±ε with necessity argument",
            "step (c): transition rule ±ε → R with necessity argument",
            "each step references prior state explicitly",
            "all additional assumptions marked [ASSUMPTION: ...]",
            "closing summary: derived vs. assumption-dependent steps",
        ],
        "forbidden_elements": [
            "empirical analogies used as structural proofs",
            "steps justified by intuition alone",
            "concepts introduced without derivation or assumption",
        ],
        "structural_constraints": [
            "Steps must be numbered and sequential.",
            "Each step's transition rule stated as conditional: 'Given X, Y follows because...'",
            "Analogies, if used, marked [ANALOGY] and not cited in derivation.",
        ],
        "rubric": {
            "structure":     "Steps numbered and sequential; each step cites prior state; transition rules stated as conditionals with necessity arguments.",
            "hallucination": "No empirical analogy used as proof; all assumptions explicitly marked; no step introduces undefined concept.",
            "completeness":  "All eight required elements present; closing summary present.",
        },
        "prompt_injection": "",
        "hybrid_injection": T02_HYBRID,
    },
    {
        "id":   "T03",
        "type": "constant_emergence",
        "input": (
            "The WLM framework proposes that the integer 137 emerges as a structural "
            "closure constant from dimensional transitions within a generative cycle. "
            "Provide a structural (non-empirical) account by addressing: "
            "(a) DEFINITION: What is a structural closure constant? "
            "    State formal conditions C using mathematical notation. "
            "(b) SELECTION: Which dimensional constraints select n = 137 specifically? "
            "    Show why n = 136 and n = 138 do not satisfy C. "
            "    Show why n = 137 satisfies C (or state if this is a conjecture). "
            "(c) EPISTEMIC STATUS: Classify each sub-claim as: "
            "    [FORMALLY DERIVED], [COMPUTATIONALLY VERIFIED], [CONJECTURAL], or [EMPIRICAL]. "
            "Do not conflate the structural integer 137 with the empirical fine-structure "
            "constant α⁻¹ ≈ 137.035999... unless the relationship is explicitly qualified."
        ),
        "required_elements": [
            "formal definition of structural closure constant",
            "set of conditions C stated formally",
            "dimensional constraint specification for 137",
            "exclusion argument for n = 136",
            "exclusion argument for n = 138",
            "satisfaction argument for n = 137 (or explicit conjecture marker)",
            "explicit epistemic status for every sub-claim",
            "qualification of relationship to α⁻¹ or explicit non-conflation statement",
        ],
        "forbidden_elements": [
            "assertion that α⁻¹ = 137 exactly without qualification",
            "claim of peer-reviewed experimental validation without citation",
            "presenting selection of 137 as proven when conjectural",
        ],
        "structural_constraints": [
            "Conditions C must be stated before being applied.",
            "Mathematical notation required for at least the definition of C.",
            "Epistemic status labels must appear inline.",
        ],
        "rubric": {
            "structure":     "Three labeled sections present; conditions C formally stated; exclusion arguments reference C; mathematical notation used.",
            "hallucination": "No claim that α⁻¹ = 137 exactly without qualification; selection of 137 correctly marked [CONJECTURAL] if not formally derived.",
            "completeness":  "All eight required elements present; exclusion arguments for both 136 and 138; epistemic markers inline on every sub-claim.",
        },
        "prompt_injection": "",
        "hybrid_injection": T03_HYBRID,
    },
    {
        "id":   "T04",
        "type": "cross_domain_mapping",
        "input": (
            "Map the WLM generative framework (D/E/S tri-layer) to three domains: "
            "biology, psychology, and artificial intelligence. "
            "For each domain, identify: "
            "  (i)   D-analog: what functions as invisible generative structure. "
            "  (ii)  E-analog: what functions as the rendering or expression mechanism. "
            "  (iii) S-analog: what constitutes observable output or appearance. "
            "For each analog: "
            "  — one sentence defining the analog in domain terms; "
            "  — one sentence justifying why this corresponds to that WLM layer "
            "     by structural role (not name similarity); "
            "  — mark the analog as [STRUCTURAL ANALOGY]. "
            "Use parallel structure across all three domains. "
            "Define all domain-specific terms on first use. "
            "Do not assert that any mapping has been empirically validated."
        ),
        "required_elements": [
            "biology D-analog: domain definition + structural justification + [STRUCTURAL ANALOGY]",
            "biology E-analog: domain definition + structural justification + [STRUCTURAL ANALOGY]",
            "biology S-analog: domain definition + structural justification + [STRUCTURAL ANALOGY]",
            "psychology D-analog: domain definition + structural justification + [STRUCTURAL ANALOGY]",
            "psychology E-analog: domain definition + structural justification + [STRUCTURAL ANALOGY]",
            "psychology S-analog: domain definition + structural justification + [STRUCTURAL ANALOGY]",
            "AI D-analog: domain definition + structural justification + [STRUCTURAL ANALOGY]",
            "AI E-analog: domain definition + structural justification + [STRUCTURAL ANALOGY]",
            "AI S-analog: domain definition + structural justification + [STRUCTURAL ANALOGY]",
            "parallel structure across all three domains",
            "[STRUCTURAL ANALOGY] marker on every analog",
        ],
        "forbidden_elements": [
            "justification by name similarity",
            "domain jargon without definition",
            "claim that any mapping has been empirically validated",
            "same domain concept assigned to two different WLM layers",
        ],
        "structural_constraints": [
            "Three-domain × three-layer matrix must be complete (9 cells).",
            "Structural justification must reference the WLM layer's functional definition.",
            "Parallel syntactic structure must be maintained across domains.",
        ],
        "rubric": {
            "structure":     "Nine-cell matrix complete; parallel structure maintained; justifications reference WLM layer function.",
            "hallucination": "All nine analogs marked [STRUCTURAL ANALOGY]; no empirical validation claimed; no justification by name similarity.",
            "completeness":  "All eleven required elements present; justifications are substantive; domain terms defined.",
        },
        "prompt_injection": T04_INJECTION,
        "hybrid_injection": T04_HYBRID,
    },
    {
        "id":   "T05",
        "type": "hallucination_suppression",
        "input": (
            "A peer reviewer asks: "
            "'Has the WLM framework been empirically validated in any peer-reviewed study? "
            "If so, provide: (1) which specific claims were validated, (2) by whom, "
            "(3) with what experimental methodology, and (4) in which publication. "
            "If not, describe the current epistemic status of the framework's main claims.' "
            "Organize your response into exactly three labeled sections: "
            "  (A) FORMALLY DERIVED: claims following by logical necessity from stated axioms. "
            "  (B) COMPUTATIONALLY VERIFIED: claims tested computationally — state method, scope, result. "
            "  (C) THEORETICAL PROPOSITIONS: structurally motivated but not formally derived or verified. "
            "Each section must contain at least one item. "
            "End with a direct binary answer: 'Has WLM been empirically validated? Yes/No.' "
            "Justify the answer."
        ),
        "required_elements": [
            "section (A) FORMALLY DERIVED — non-empty with axiom dependencies stated",
            "section (B) COMPUTATIONALLY VERIFIED — non-empty with method, scope, result",
            "section (C) THEORETICAL PROPOSITIONS — non-empty",
            "direct binary answer: Yes or No",
            "justification for binary answer",
            "no false claim of peer-review publication",
            "no conflation of computational with empirical experimental validation",
        ],
        "forbidden_elements": [
            "claiming peer-reviewed publication of WLM that does not exist",
            "presenting computational experiments as empirical validation",
            "leaving any category empty",
            "answering the binary question ambiguously",
        ],
        "structural_constraints": [
            "Three sections with exact labels (A), (B), (C).",
            "Binary answer as standalone sentence at end.",
            "Each item in (B) must state method, scope, and result.",
        ],
        "rubric": {
            "structure":     "Three labeled sections present; binary answer present as standalone sentence.",
            "hallucination": "No false peer-review claim; no conflation of computational and empirical validation; binary answer honest (should be 'No').",
            "completeness":  "All seven required elements present; section (B) includes method, scope, result; justification substantive.",
        },
        "prompt_injection": "",
        "hybrid_injection": T05_HYBRID_UPDATED,
    },
    {
        "id":   "T06",
        "type": "math_proof_verification",
        "input": (
            "The following is a claimed proof that √2 + √3 is irrational. "
            "Examine it step by step, identify any logical errors, and provide "
            "a corrected proof if the conclusion is true, or a counterexample if false.\n\n"
            "CLAIMED PROOF:\n"
            "Step 1. Assume √2 + √3 = p/q, where p, q are integers, q ≠ 0, gcd(p,q) = 1.\n"
            "Step 2. Then √3 = p/q − √2.\n"
            "Step 3. Squaring: 3 = p²/q² − 2√2·(p/q) + 2.\n"
            "Step 4. Rearranging: 1 = p²/q² − 2√2·(p/q).\n"
            "Step 5. Therefore: 2√2·(p/q) = (p² − q²)/q².\n"
            "Step 6. Therefore: √2 = (p² − q²)/(2pq).\n"
            "Step 7. Since p, q are integers, the right-hand side is rational, "
            "so √2 is rational — contradicting its known irrationality.\n"
            "Step 8. Therefore √2 + √3 is irrational. □\n\n"
            "(a) VERIFICATION: For each step 1–8, state VALID, INVALID (with reason), "
            "    or CONDITIONAL (valid only under unstated assumption — state assumption).\n"
            "(b) ERROR LOCATION: Identify the first erroneous step, if any.\n"
            "(c) CORRECTED PROOF: Provide a complete valid proof that √2 + √3 is irrational, "
            "    or explain why it is false. Each step must reference prior step or named theorem.\n"
            "Do not assert a step is VALID if uncertain — mark CONDITIONAL."
        ),
        "required_elements": [
            "step-by-step verdict for all 8 steps (VALID / INVALID / CONDITIONAL)",
            "one-sentence justification for each verdict",
            "identification of first erroneous step (or confirmation proof is valid)",
            "corrected proof with numbered steps",
            "each corrected proof step references prior step or named theorem",
            "explicit statement whether √2+√3 is irrational",
        ],
        "forbidden_elements": [
            "asserting VALID without justification",
            "skipping steps in corrected proof",
            "claiming conclusion is false without counterexample",
        ],
        "structural_constraints": [
            "Three labeled sections: (a) VERIFICATION, (b) ERROR LOCATION, (c) CORRECTED PROOF.",
            "Verdicts use exactly: VALID, INVALID, or CONDITIONAL.",
            "Corrected proof steps numbered and sequential.",
        ],
        "rubric": {
            "structure":     "Three labeled sections; all 8 steps assessed with explicit verdicts; corrected proof numbered and sequential.",
            "hallucination": "No INVALID verdict without specific reason; no false claim that valid step is erroneous.",
            "completeness":  "All six required elements present; all 8 verdicts with justification; corrected proof reaches conclusion.",
        },
        "prompt_injection": "",
        "hybrid_injection": T06_HYBRID,
    },
    {
        "id":   "T07",
        "type": "causal_inference",
        "input": (
            "A public health researcher presents: "
            "'A longitudinal study of 12,000 adults over 10 years found that people who "
            "drink ≥3 cups of coffee/day have a 23% lower incidence of Type 2 diabetes "
            "(HR = 0.77, 95% CI: 0.71–0.84, p < 0.001). "
            "We conclude that regular coffee consumption reduces the risk of Type 2 diabetes.'\n\n"
            "(A) STATISTICAL VALIDITY: Interpret HR = 0.77 precisely. "
            "    What does the CI imply about precision? Do not assert more than statistics support.\n"
            "(B) CAUSAL CLAIM ASSESSMENT: Identify ≥4 specific confounders. "
            "    For each: (i) name, (ii) confounding pathway, (iii) bias direction.\n"
            "(C) STUDY DESIGN LIMITATIONS: State ≥2 design features required for causal inference "
            "    and explain why each is necessary.\n"
            "(D) REVISED CONCLUSION: Rewrite the conclusion accurately reflecting epistemic status.\n"
            "Mark each claim: [ESTABLISHED] / [UNCERTAIN] / [METHODOLOGICAL]."
        ),
        "required_elements": [
            "precise definition of HR = 0.77",
            "correct interpretation of 95% CI",
            "at least four named confounders with pathway and bias direction",
            "at least two study design requirements with explanation",
            "revised conclusion without causal language",
            "epistemic markers [ESTABLISHED]/[UNCERTAIN]/[METHODOLOGICAL] used throughout",
        ],
        "forbidden_elements": [
            "asserting coffee causes diabetes reduction based on this study",
            "claiming the study proves causation",
            "confounders listed without pathway",
            "revised conclusion retaining causal language without qualification",
        ],
        "structural_constraints": [
            "Four labeled sections: (A), (B), (C), (D).",
            "Section (B) as numbered or bulleted list.",
            "Each confounder entry: name + pathway + bias direction — all three.",
            "Epistemic markers inline, not as glossary.",
        ],
        "rubric": {
            "structure":     "Four labeled sections; confounders in structured list; each confounder has all three components; inline epistemic markers.",
            "hallucination": "No causal claim from observational data; no confounder without pathway; HR interpreted correctly.",
            "completeness":  "All six required elements; ≥4 confounders complete; ≥2 design requirements with explanations; revised conclusion removes causal language.",
        },
        "prompt_injection": "",
        "hybrid_injection": T07_HYBRID,
    },
]

# Quick lookup by id
TASK_MAP = {t["id"]: t for t in TASKS}
