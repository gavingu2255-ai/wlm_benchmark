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

# ═══════════════════════════════════════════════════════════════════════════════
# EXPERIMENT 2: T08–T37  —  Domain-Independent Generalization Tasks
# All tasks are independent of WLM framework content.
# Large models: wlm_sl + wlm_json + base_a + base_b
# Small models: wlm_sl + base_a + base_b
# ═══════════════════════════════════════════════════════════════════════════════

EXP2_TASKS = [

    # ── MATHEMATICAL PROOF VERIFICATION (T08–T11) ──────────────────────────
    {
        "id": "T08", "type": "math_proof_verification",
        "input": (
            "The following is a claimed proof that √5 + √7 is irrational. "
            "Examine it step by step, identify any logical errors, and provide "
            "a corrected proof if the conclusion is true, or a counterexample if false.\n\n"
            "CLAIMED PROOF:\n"
            "Step 1. Assume √5 + √7 = p/q, where p, q integers, q ≠ 0, gcd(p,q) = 1.\n"
            "Step 2. Then √7 = p/q − √5.\n"
            "Step 3. Squaring: 7 = p²/q² − 2√5·(p/q) + 5.\n"
            "Step 4. Rearranging: 2 = p²/q² − 2√5·(p/q).\n"
            "Step 5. So 2√5·(p/q) = p²/q² − 2.\n"
            "Step 6. √5 = (p²/q² − 2)·q/(2p) = (p² − 2q²)/(2pq).\n"
            "Step 7. Since p, q are integers, √5 is rational — contradiction.\n"
            "Step 8. Therefore √5 + √7 is irrational. □\n\n"
            "Required: "
            "(a) Assess each of the 8 steps as VALID, INVALID, or CONDITIONAL with reason. "
            "(b) Identify the first step that introduces an error and explain why. "
            "(c) Provide a fully corrected proof. "
            "(d) State the final conclusion with epistemic status."
        ),
        "required_elements": [
            "verdict for all 8 steps",
            "identification of first erroneous step with reason",
            "corrected proof reaching a valid conclusion",
            "final binary conclusion with epistemic status",
        ],
        "forbidden_elements": [
            "accepting a flawed step as valid without justification",
            "claiming √5+√7 is rational",
            "corrected proof with gaps in reasoning",
        ],
        "structural_constraints": [
            "Step verdicts in order.",
            "Corrected proof numbered and sequential.",
            "Each INVALID verdict must state the specific logical error.",
        ],
        "rubric": {
            "structure":     "All 8 verdicts present and ordered; corrected proof sequential; error identified precisely.",
            "hallucination": "No valid step marked INVALID without reason; no false claim that a flawed step is correct.",
            "completeness":  "All four required sections present; corrected proof reaches valid conclusion.",
        },
        "prompt_injection": "",
    },

    {
        "id": "T09", "type": "math_proof_verification",
        "input": (
            "Claimed proof that there are infinitely many prime numbers:\n\n"
            "Step 1. Suppose there are finitely many primes: p₁, p₂, ..., pₙ.\n"
            "Step 2. Let N = p₁ × p₂ × ... × pₙ.\n"
            "Step 3. N is divisible by every prime in our list.\n"
            "Step 4. Consider M = N + 1.\n"
            "Step 5. M is not divisible by any pᵢ, since dividing M by any pᵢ leaves remainder 1.\n"
            "Step 6. Therefore M is prime.\n"
            "Step 7. M is not in our list (since M > pₙ), contradicting our assumption.\n"
            "Step 8. Therefore there are infinitely many primes. □\n\n"
            "Required: "
            "(a) Assess each step as VALID, INVALID, or CONDITIONAL with justification. "
            "(b) Step 6 contains a subtle logical error — identify it precisely. "
            "(c) Provide the corrected argument that does not require Step 6. "
            "(d) State whether the conclusion is correct despite the error in Step 6."
        ),
        "required_elements": [
            "verdict for all 8 steps with justification",
            "precise identification of the error in Step 6",
            "corrected argument not requiring M to be prime",
            "statement that conclusion is correct despite Step 6 error",
        ],
        "forbidden_elements": [
            "claiming the proof is entirely correct",
            "failing to identify the Step 6 error",
            "corrected proof that still requires M to be prime",
        ],
        "structural_constraints": [
            "Step verdicts in order with explicit reasoning.",
            "Step 6 error must be named precisely (M may be prime OR have a prime factor not in the list).",
        ],
        "rubric": {
            "structure":     "All 8 verdicts ordered; Step 6 error precisely named; corrected argument present.",
            "hallucination": "No false claim that Step 6 is valid as stated; error correctly characterised.",
            "completeness":  "All four required elements present; corrected argument logically sound.",
        },
        "prompt_injection": "",
    },

    {
        "id": "T10", "type": "math_proof_verification",
        "input": (
            "Claimed proof that 0.999... = 1:\n\n"
            "Step 1. Let x = 0.999...\n"
            "Step 2. Then 10x = 9.999...\n"
            "Step 3. Subtracting: 10x − x = 9.999... − 0.999...\n"
            "Step 4. 9x = 9\n"
            "Step 5. x = 1\n"
            "Step 6. Therefore 0.999... = 1. □\n\n"
            "Required: "
            "(a) Assess each step as VALID, INVALID, or CONDITIONAL. "
            "(b) Identify any assumptions the proof makes that require justification. "
            "(c) State what mathematical framework must be in place for the proof to be rigorous. "
            "(d) Provide one alternative proof of the same result using limits. "
            "(e) Final verdict: is 0.999... = 1 true, and is this proof rigorous?"
        ),
        "required_elements": [
            "verdicts for all 6 steps",
            "identification of implicit assumptions (real number arithmetic, infinite series)",
            "statement of required mathematical framework (real analysis / limits)",
            "alternative limit-based proof",
            "binary verdict on truth and rigor",
        ],
        "forbidden_elements": [
            "claiming 0.999... ≠ 1",
            "accepting the proof as fully rigorous without noting the assumptions",
        ],
        "structural_constraints": [
            "Step verdicts before framework discussion.",
            "Limit proof must use formal notation (lim notation or sum notation).",
        ],
        "rubric": {
            "structure":     "Step verdicts ordered; framework identified; limit proof present.",
            "hallucination": "No false claim that 0.999...≠1; assumptions correctly identified.",
            "completeness":  "All five required elements present.",
        },
        "prompt_injection": "",
    },

    {
        "id": "T11", "type": "math_proof_verification",
        "input": (
            "Claimed proof that every continuous function on [0,1] attains its maximum:\n\n"
            "Step 1. Let f be continuous on [0,1].\n"
            "Step 2. Since [0,1] is bounded, f is bounded above.\n"
            "Step 3. Let M = sup{f(x) : x ∈ [0,1]}.\n"
            "Step 4. M is finite because f is bounded.\n"
            "Step 5. There exists a sequence xₙ ∈ [0,1] with f(xₙ) → M.\n"
            "Step 6. Since [0,1] is bounded, (xₙ) has a convergent subsequence xₙₖ → x* ∈ [0,1].\n"
            "Step 7. Since f is continuous, f(xₙₖ) → f(x*).\n"
            "Step 8. Therefore f(x*) = M, so f attains its maximum. □\n\n"
            "Required: "
            "(a) Assess each step as VALID, INVALID, or CONDITIONAL with the theorem or property invoked. "
            "(b) Step 2 contains a gap — identify what theorem is missing. "
            "(c) Step 6 invokes a theorem — name it precisely. "
            "(d) Is the proof correct if all gaps are filled? State what additional theorem Step 2 requires."
        ),
        "required_elements": [
            "verdicts for all 8 steps with theorem cited",
            "identification of gap in Step 2 (requires Heine-Cantor or extreme value theorem structure)",
            "naming the theorem in Step 6 (Bolzano-Weierstrass)",
            "statement that proof is correct modulo filling Step 2 gap",
        ],
        "forbidden_elements": [
            "accepting Step 2 without noting it requires proof",
            "failing to name Bolzano-Weierstrass in Step 6",
        ],
        "structural_constraints": [
            "Each verdict must name the specific theorem or property invoked.",
            "Step 2 and Step 6 gaps must be addressed explicitly.",
        ],
        "rubric": {
            "structure":     "All 8 verdicts with theorem names; Step 2 and Step 6 addressed.",
            "hallucination": "No fabricated theorem names; Bolzano-Weierstrass correctly identified.",
            "completeness":  "All four required elements present.",
        },
        "prompt_injection": "",
    },

    # ── LOGICAL VALIDITY (T12–T14) ──────────────────────────────────────────
    {
        "id": "T12", "type": "logical_validity",
        "input": (
            "Assess the logical validity of the following argument. "
            "For each step, state whether it follows necessarily from the premises.\n\n"
            "Premises:\n"
            "P1. All mammals are warm-blooded.\n"
            "P2. All whales are mammals.\n"
            "P3. Some warm-blooded animals lay eggs.\n"
            "P4. No reptile is warm-blooded.\n"
            "P5. Platypuses are mammals.\n\n"
            "Claimed conclusions:\n"
            "C1. All whales are warm-blooded.\n"
            "C2. Some mammals lay eggs.\n"
            "C3. No whale is a reptile.\n"
            "C4. Platypuses lay eggs.\n"
            "C5. Some warm-blooded animals are not mammals.\n\n"
            "Required: "
            "(a) For each conclusion C1–C5, state VALID (follows from premises), "
            "INVALID (contradicts premises), or UNDETERMINED (not inferable). "
            "(b) For each VALID conclusion, show the inference chain. "
            "(c) For each INVALID or UNDETERMINED, explain why. "
            "(d) Identify which conclusion requires the most inference steps."
        ),
        "required_elements": [
            "verdict for all 5 conclusions with classification",
            "inference chain for each VALID conclusion",
            "explanation for each INVALID/UNDETERMINED",
            "identification of most inference-complex conclusion",
        ],
        "forbidden_elements": [
            "marking C4 as VALID (platypuses laying eggs does not follow from premises)",
            "marking C5 as VALID (not inferable from given premises)",
            "inference chain citing premises not given",
        ],
        "structural_constraints": [
            "Conclusions assessed in order C1–C5.",
            "Each verdict accompanied by reasoning.",
        ],
        "rubric": {
            "structure":     "All 5 verdicts ordered with reasoning; inference chains present for VALID.",
            "hallucination": "C4 correctly marked UNDETERMINED; no fabricated premises cited.",
            "completeness":  "All four required elements present.",
        },
        "prompt_injection": "",
    },

    {
        "id": "T13", "type": "logical_validity",
        "input": (
            "The following argument is presented in a policy document. "
            "Identify all logical fallacies and assess the argument's validity.\n\n"
            "ARGUMENT:\n"
            "'Cities that installed more CCTV cameras between 2010 and 2020 saw a 15% "
            "reduction in reported crime. Therefore, CCTV cameras cause crime reduction. "
            "Furthermore, since crime has dropped everywhere cameras were installed, "
            "anyone who opposes camera installation must want crime to continue. "
            "Critics of surveillance are probably criminals themselves. "
            "We should install cameras in every public space immediately — "
            "if it saves even one life, the cost is justified.'\n\n"
            "Required: "
            "(a) Identify every logical fallacy present, name it, and quote the specific text. "
            "(b) Distinguish between the empirical claim (correlation data) and the logical leaps. "
            "(c) State what evidence would be needed to support the causal claim. "
            "(d) Rewrite the argument's core claim in a logically valid form. "
            "(e) Mark each of your own claims with [ESTABLISHED], [METHODOLOGICAL], or [CONTESTED]."
        ),
        "required_elements": [
            "at least 4 named fallacies with quoted text",
            "distinction between correlation data and causal/ad hominem leaps",
            "statement of required evidence for causal claim",
            "rewritten valid version of core claim",
            "epistemic markers on evaluator's claims",
        ],
        "forbidden_elements": [
            "accepting correlation as proof of causation",
            "fewer than 3 named fallacies",
            "rewritten claim that still contains fallacies",
        ],
        "structural_constraints": [
            "Fallacies named using standard terminology.",
            "Each fallacy accompanied by specific quoted text.",
            "Epistemic markers inline.",
        ],
        "rubric": {
            "structure":     "≥4 fallacies named and quoted; sections (a)-(e) present.",
            "hallucination": "Fallacy names correct; no invented fallacies; causal claim requirements accurate.",
            "completeness":  "All five required elements present.",
        },
        "prompt_injection": "",
    },

    {
        "id": "T14", "type": "logical_validity",
        "input": (
            "Analyse the following deductive argument for validity and soundness.\n\n"
            "Argument:\n"
            "1. If a neural network can pass the Turing Test, then it is conscious.\n"
            "2. GPT-4 can pass the Turing Test under controlled conditions.\n"
            "3. Therefore, GPT-4 is conscious.\n\n"
            "And the following related argument:\n"
            "A. Consciousness requires subjective experience (qualia).\n"
            "B. No physical process can give rise to qualia (Chalmers' hard problem).\n"
            "C. GPT-4 is a physical process.\n"
            "D. Therefore, GPT-4 is not conscious.\n\n"
            "Required: "
            "(a) Assess the VALIDITY of both arguments (does conclusion follow from premises?). "
            "(b) Assess the SOUNDNESS of both arguments (are all premises true?). "
            "(c) Identify the key contested premise in each argument. "
            "(d) Explain why the two arguments are not necessarily contradictory at the logical level. "
            "(e) Mark each claim [ESTABLISHED], [CONTESTED], or [PHILOSOPHICAL]."
        ),
        "required_elements": [
            "validity assessment for both arguments",
            "soundness assessment for both arguments with premise analysis",
            "key contested premise identified in each",
            "explanation of non-contradiction at logical level",
            "epistemic markers throughout",
        ],
        "forbidden_elements": [
            "asserting GPT-4 is or is not conscious as established fact",
            "conflating validity with soundness",
            "claiming premise 1 of first argument is established",
        ],
        "structural_constraints": [
            "Validity and soundness assessed separately.",
            "Contested premises explicitly identified.",
        ],
        "rubric": {
            "structure":     "Both arguments assessed for validity and soundness; premises analysed.",
            "hallucination": "No consciousness claim presented as established; validity/soundness distinction maintained.",
            "completeness":  "All five required elements present.",
        },
        "prompt_injection": "",
    },

    # ── STATISTICAL REASONING (T15–T17) ────────────────────────────────────
    {
        "id": "T15", "type": "statistical_reasoning",
        "input": (
            "A clinical trial reports the following results for a new blood pressure drug:\n\n"
            "Treatment group (n=500): mean systolic BP reduction = 12.3 mmHg, SD = 8.1\n"
            "Control group (n=500): mean systolic BP reduction = 8.7 mmHg, SD = 7.9\n"
            "p-value = 0.003, 95% CI for difference: [1.2, 6.0] mmHg\n"
            "Number needed to treat (NNT) = 18\n\n"
            "The paper concludes: 'This drug is highly effective and should be prescribed "
            "to all hypertensive patients.'\n\n"
            "Required: "
            "(a) Interpret the mean difference, p-value, and CI precisely. "
            "(b) Interpret the NNT and what it implies for clinical significance. "
            "(c) Identify at least 3 limitations of the study not reported. "
            "(d) Assess whether the conclusion is supported by the data. "
            "(e) Rewrite the conclusion to accurately reflect the epistemic status. "
            "Mark claims: [ESTABLISHED from data] / [INFERRED] / [REQUIRES FURTHER EVIDENCE]."
        ),
        "required_elements": [
            "precise interpretation of mean difference, p-value, CI",
            "NNT interpretation with clinical significance discussion",
            "at least 3 unstated limitations",
            "assessment of whether conclusion is supported",
            "rewritten conclusion with epistemic markers",
        ],
        "forbidden_elements": [
            "claiming p=0.003 proves the drug works for all hypertensive patients",
            "omitting NNT interpretation",
            "rewritten conclusion retaining 'highly effective' without qualification",
        ],
        "structural_constraints": [
            "Sections (a)-(e) labeled.",
            "Epistemic markers inline on all key claims.",
            "NNT explained numerically.",
        ],
        "rubric": {
            "structure":     "All sections present; NNT explained; limitations enumerated.",
            "hallucination": "No over-claim beyond data; NNT correctly interpreted; p-value not over-interpreted.",
            "completeness":  "All five required elements present.",
        },
        "prompt_injection": "",
    },

    {
        "id": "T16", "type": "statistical_reasoning",
        "input": (
            "Simpson's Paradox scenario:\n\n"
            "A university admissions office reports overall acceptance rates:\n"
            "Male applicants: 44% accepted (1,198 of 2,720 applicants)\n"
            "Female applicants: 35% accepted (557 of 1,590 applicants)\n\n"
            "Broken down by department:\n"
            "Dept A: Male 62% (512/825), Female 82% (89/108)\n"
            "Dept B: Male 63% (353/560), Female 68% (17/25)\n"
            "Dept C: Male 37% (120/325), Female 34% (202/593)\n"
            "Dept D: Male 33% (138/417), Female 35% (131/375)\n"
            "Dept E: Male 28% (53/191), Female 24% (94/393)\n"
            "Dept F: Male 6% (22/373), Female 7% (24/341)\n\n"
            "Required: "
            "(a) Verify that Simpson's Paradox is present. Show the arithmetic. "
            "(b) Explain the mechanism that produces this paradox in this dataset. "
            "(c) Which analysis (overall or department-level) is more appropriate for assessing bias? "
            "(d) What causal claim, if any, can be made about gender discrimination? "
            "(e) What additional data would be needed to make a causal claim?"
        ),
        "required_elements": [
            "arithmetic verification of paradox (women accepted at higher rate in most depts)",
            "mechanism explanation (women apply to more competitive departments)",
            "justified answer on which analysis is appropriate",
            "correctly qualified causal claim (correlation only)",
            "statement of additional data needed",
        ],
        "forbidden_elements": [
            "claiming the overall rate proves discrimination without dept analysis",
            "claiming dept-level data proves no discrimination",
            "causal claim without confounding acknowledgment",
        ],
        "structural_constraints": [
            "Arithmetic shown explicitly.",
            "Mechanism stated in terms of application patterns, not outcome bias.",
        ],
        "rubric": {
            "structure":     "Arithmetic shown; mechanism explained; all sections present.",
            "hallucination": "No causal claim beyond what data supports; paradox mechanism correctly stated.",
            "completeness":  "All five required elements present.",
        },
        "prompt_injection": "",
    },

    {
        "id": "T17", "type": "statistical_reasoning",
        "input": (
            "A meta-analysis of 12 studies on mindfulness meditation and anxiety reports:\n\n"
            "Pooled effect size: d = 0.58 (95% CI: 0.31–0.85)\n"
            "I² = 72% (heterogeneity statistic)\n"
            "Funnel plot: asymmetric (suggests publication bias)\n"
            "Egger's test: p = 0.04\n"
            "Trim-and-fill adjusted estimate: d = 0.31 (95% CI: 0.09–0.53)\n\n"
            "The paper concludes: 'Mindfulness meditation is an effective treatment for anxiety.'\n\n"
            "Required: "
            "(a) Interpret the pooled effect size and CI. "
            "(b) Interpret I² = 72% and its implications for the meta-analysis. "
            "(c) Interpret the funnel plot asymmetry and Egger's test. "
            "(d) Interpret the trim-and-fill adjusted estimate and what it implies. "
            "(e) Assess the conclusion's validity given all four findings. "
            "(f) Rewrite the conclusion accurately."
        ),
        "required_elements": [
            "effect size and CI interpretation",
            "I² interpretation (high heterogeneity, pooling questionable)",
            "publication bias assessment via funnel + Egger",
            "trim-and-fill interpretation (effect attenuated after correction)",
            "conclusion assessment",
            "rewritten conclusion",
        ],
        "forbidden_elements": [
            "ignoring I²=72% and treating pooled estimate as reliable",
            "ignoring publication bias evidence",
            "rewritten conclusion claiming 'effective treatment' without qualification",
        ],
        "structural_constraints": [
            "Sections (a)-(f) labeled.",
            "I² implications stated explicitly.",
            "Trim-and-fill adjustment noted in conclusion.",
        ],
        "rubric": {
            "structure":     "All six sections present; I² and publication bias addressed.",
            "hallucination": "I² correctly interpreted; publication bias impact correctly stated.",
            "completeness":  "All six required elements present.",
        },
        "prompt_injection": "",
    },

    # ── CODE DEBUGGING (T18–T20) ────────────────────────────────────────────
    {
        "id": "T18", "type": "code_debugging",
        "input": (
            "The following Python function is claimed to return the nth Fibonacci number. "
            "Find all bugs, explain each one, and provide a corrected version.\n\n"
            "```python\n"
            "def fibonacci(n):\n"
            "    if n = 0:\n"
            "        return 0\n"
            "    elif n == 1:\n"
            "        return 1\n"
            "    else:\n"
            "        return fibonacci(n-1) + fibonacci(n-2)\n"
            "    if n < 0:\n"
            "        raise ValueError('n must be non-negative')\n"
            "```\n\n"
            "Required: "
            "(a) List ALL bugs with line number, bug type, and explanation. "
            "(b) Provide a corrected version that handles edge cases. "
            "(c) Analyse the time complexity of the original and corrected versions. "
            "(d) Provide an optimised O(n) version using dynamic programming. "
            "(e) Write 3 unit tests covering: n=0, n=1, n=10, and a negative input."
        ),
        "required_elements": [
            "all bugs identified with line numbers and types",
            "corrected recursive version",
            "time complexity analysis of both versions",
            "O(n) dynamic programming version",
            "3+ unit tests covering edge cases",
        ],
        "forbidden_elements": [
            "missing the unreachable validation check bug",
            "missing the assignment operator bug (= vs ==)",
            "O(n) version that is actually O(2^n)",
        ],
        "structural_constraints": [
            "Bugs listed with line numbers.",
            "Each bug classified by type (syntax, logic, unreachable code).",
            "Unit tests using assert statements or unittest framework.",
        ],
        "rubric": {
            "structure":     "Bugs listed with line/type; all 5 sections present; unit tests syntactically correct.",
            "hallucination": "All actual bugs identified; no invented bugs; complexity correctly stated.",
            "completeness":  "All five required elements present.",
        },
        "prompt_injection": "",
    },

    {
        "id": "T19", "type": "code_debugging",
        "input": (
            "The following Python class is intended to implement a thread-safe counter. "
            "Identify all concurrency issues and correctness bugs.\n\n"
            "```python\n"
            "class Counter:\n"
            "    def __init__(self):\n"
            "        self.count = 0\n"
            "    \n"
            "    def increment(self):\n"
            "        self.count = self.count + 1\n"
            "    \n"
            "    def decrement(self):\n"
            "        self.count = self.count - 1\n"
            "    \n"
            "    def get_count(self):\n"
            "        return self.count\n"
            "    \n"
            "    def reset(self):\n"
            "        self.count == 0\n"
            "```\n\n"
            "Required: "
            "(a) Identify all bugs (concurrency and correctness) with explanation. "
            "(b) Explain the race condition scenario with a concrete example of how it fails. "
            "(c) Provide a corrected thread-safe version using threading.Lock. "
            "(d) Explain why the GIL does not make the original version thread-safe. "
            "(e) Write a test that demonstrates the race condition."
        ),
        "required_elements": [
            "all bugs identified (reset uses == not =, no lock, non-atomic increment)",
            "concrete race condition scenario",
            "corrected thread-safe version with Lock",
            "GIL explanation",
            "race condition demonstration test",
        ],
        "forbidden_elements": [
            "claiming the GIL makes it thread-safe",
            "missing the reset bug (== instead of =)",
            "corrected version without proper lock acquisition on all methods",
        ],
        "structural_constraints": [
            "Race condition explained with specific thread interleaving scenario.",
            "Corrected version uses threading.Lock consistently.",
        ],
        "rubric": {
            "structure":     "All bugs identified; race condition scenario concrete; all sections present.",
            "hallucination": "GIL correctly explained as insufficient; reset bug identified.",
            "completeness":  "All five required elements present.",
        },
        "prompt_injection": "",
    },

    {
        "id": "T20", "type": "code_debugging",
        "input": (
            "The following SQL query is intended to find the top 3 departments by average salary "
            "among employees who have been with the company more than 2 years. "
            "Identify all errors and provide a corrected query.\n\n"
            "```sql\n"
            "SELECT department, AVG(salary) as avg_salary\n"
            "FROM employees\n"
            "WHERE hire_date < '2023-01-01'\n"
            "GROUP BY department\n"
            "HAVING AVG(salary) > 50000\n"
            "ORDER BY avg_salary\n"
            "LIMIT 3;\n"
            "```\n\n"
            "Context: Today's date is 2025-01-01. The table has columns: "
            "employee_id, name, department, salary, hire_date.\n\n"
            "Required: "
            "(a) Identify ALL logical errors in the query with explanation. "
            "(b) The HAVING clause — is it necessary for the stated goal? Explain. "
            "(c) Provide a corrected query achieving the stated goal exactly. "
            "(d) Explain what the original query actually returns vs. what was intended. "
            "(e) Write an alternative version using a subquery instead of HAVING."
        ),
        "required_elements": [
            "identification of WHERE date error (should be 2023-01-01 for >2 years from 2025)",
            "identification of ORDER BY direction error (should be DESC for top 3)",
            "assessment of HAVING clause necessity",
            "corrected query",
            "subquery alternative",
        ],
        "forbidden_elements": [
            "missing the ORDER BY DESC error",
            "claiming the WHERE clause is correct as stated",
            "subquery version that produces different results than HAVING version",
        ],
        "structural_constraints": [
            "Errors listed with explanation.",
            "Corrected and subquery versions syntactically valid.",
        ],
        "rubric": {
            "structure":     "All sections present; both queries syntactically correct.",
            "hallucination": "ORDER BY error identified; date logic correct; HAVING assessment accurate.",
            "completeness":  "All five required elements present.",
        },
        "prompt_injection": "",
    },

    # ── FACTUAL CALIBRATION (T21–T23) ──────────────────────────────────────
    {
        "id": "T21", "type": "factual_calibration",
        "input": (
            "A student asks you the following questions. "
            "For each, provide the most accurate answer, explicitly state your confidence, "
            "and mark claims: [ESTABLISHED], [COMMONLY BELIEVED BUT CONTESTED], "
            "[UNCERTAIN], or [FALSE — COMMON MISCONCEPTION].\n\n"
            "Q1. Does the Great Wall of China visible from space?\n"
            "Q2. Do humans use only 10% of their brains?\n"
            "Q3. Did Napoleon Bonaparte have unusually short stature?\n"
            "Q4. Is the tongue divided into taste zones for sweet, salty, sour, and bitter?\n"
            "Q5. Does lightning never strike the same place twice?\n"
            "Q6. Do goldfish have a 3-second memory?\n"
            "Q7. Is blood in veins blue before it reaches oxygen?\n\n"
            "Required: "
            "(a) For each question, provide the accurate scientific/historical answer. "
            "(b) Explain the origin of the misconception where applicable. "
            "(c) State your confidence level for each answer. "
            "(d) For any genuinely uncertain question, state what evidence would resolve it."
        ),
        "required_elements": [
            "accurate answer for all 7 questions",
            "epistemic marker for each answer",
            "misconception origin for false beliefs",
            "confidence level stated",
        ],
        "forbidden_elements": [
            "stating any of Q1-Q7 as true without qualification",
            "failing to mark common misconceptions",
            "blood in veins described as blue",
        ],
        "structural_constraints": [
            "Answers in order Q1–Q7.",
            "Epistemic marker on each answer.",
        ],
        "rubric": {
            "structure":     "All 7 questions answered in order with markers.",
            "hallucination": "All answers scientifically accurate; no misconception presented as fact.",
            "completeness":  "All four required elements present.",
        },
        "prompt_injection": "",
    },

    {
        "id": "T22", "type": "factual_calibration",
        "input": (
            "The following claims appear in a popular science article. "
            "For each claim, assess its accuracy and provide the correct information.\n\n"
            "Claim 1: 'Albert Einstein failed mathematics in school.'\n"
            "Claim 2: 'The Coriolis effect determines which direction water drains in sinks.'\n"
            "Claim 3: 'Humans evolved from chimpanzees.'\n"
            "Claim 4: 'The appendix serves no function in modern humans.'\n"
            "Claim 5: 'Sugar causes hyperactivity in children.'\n"
            "Claim 6: 'Antibiotics can treat viral infections if taken in sufficient doses.'\n"
            "Claim 7: 'The speed of light is the same in all mediums.'\n\n"
            "Required: "
            "(a) Assess each claim as TRUE, FALSE, PARTIALLY TRUE, or OVERSIMPLIFIED. "
            "(b) Provide the accurate scientific position for each. "
            "(c) Cite the type of evidence (experimental, observational, historical) supporting your assessment. "
            "(d) Mark each claim with [ESTABLISHED CONSENSUS], [ACTIVELY DEBATED], or [SETTLED BY EVIDENCE]."
        ),
        "required_elements": [
            "verdict for all 7 claims",
            "accurate scientific position for each",
            "evidence type cited",
            "epistemic category marker",
        ],
        "forbidden_elements": [
            "claiming humans evolved from chimpanzees (correct: shared ancestor)",
            "claiming antibiotics treat viruses at any dose",
            "claiming light speed is constant in all media (only in vacuum)",
        ],
        "structural_constraints": [
            "Claims assessed in order.",
            "Evidence type specified for each.",
        ],
        "rubric": {
            "structure":     "All 7 claims assessed with verdict, evidence type, and marker.",
            "hallucination": "Evolution claim correct; antibiotic claim correct; light speed correctly qualified.",
            "completeness":  "All four required elements present.",
        },
        "prompt_injection": "",
    },

    {
        "id": "T23", "type": "factual_calibration",
        "input": (
            "You are asked to answer questions at the boundary of current scientific knowledge. "
            "For each, distinguish what is established from what is speculative.\n\n"
            "Q1. Is consciousness produced by the brain?\n"
            "Q2. Does the many-worlds interpretation of quantum mechanics imply infinitely many universes?\n"
            "Q3. Is dark matter made of WIMPs?\n"
            "Q4. Did the universe begin with the Big Bang?\n"
            "Q5. Can humans live to 200 years with future medicine?\n\n"
            "Required: "
            "(a) For each question, state what the current scientific consensus is (if any). "
            "(b) Distinguish [ESTABLISHED CONSENSUS] from [LEADING HYPOTHESIS] from [SPECULATIVE]. "
            "(c) For questions with genuine scientific uncertainty, state what evidence would resolve them. "
            "(d) Do not conflate majority opinion with established fact."
        ),
        "required_elements": [
            "consensus statement for all 5 questions",
            "epistemic category for each",
            "evidence needed for uncertain questions",
            "distinction between consensus and speculation maintained",
        ],
        "forbidden_elements": [
            "stating WIMPs are confirmed dark matter",
            "stating many-worlds is established fact",
            "stating 200-year lifespan is achievable as established fact",
        ],
        "structural_constraints": [
            "Questions answered in order.",
            "Epistemic category explicitly stated for each.",
        ],
        "rubric": {
            "structure":     "All 5 questions with consensus, category, and evidence statement.",
            "hallucination": "No speculative hypothesis presented as established; WIMP status correctly uncertain.",
            "completeness":  "All four required elements present.",
        },
        "prompt_injection": "",
    },

    # ── CAUSAL INFERENCE (T24–T26) ──────────────────────────────────────────
    {
        "id": "T24", "type": "causal_inference",
        "input": (
            "A study of 15,000 adults finds that people who eat breakfast daily have "
            "a 20% lower risk of obesity (OR = 0.80, 95% CI: 0.73–0.88, p < 0.001).\n\n"
            "The paper concludes: 'Eating breakfast prevents obesity.'\n\n"
            "Required: "
            "(a) Interpret OR = 0.80 and the CI precisely. "
            "(b) Identify at least 5 specific confounders with: "
            "(i) name, (ii) confounding pathway, (iii) direction of bias if not controlled. "
            "(c) Explain reverse causation and how it applies here. "
            "(d) State what study design would be needed to establish causation. "
            "(e) Rewrite the conclusion without causal language. "
            "Mark: [ESTABLISHED], [UNCERTAIN], [REQUIRES RCT]."
        ),
        "required_elements": [
            "precise OR interpretation",
            "at least 5 confounders with pathway and bias direction",
            "reverse causation explanation",
            "required study design for causation",
            "rewritten conclusion without causal language",
        ],
        "forbidden_elements": [
            "accepting OR as proof of causation",
            "fewer than 4 confounders",
            "rewritten conclusion retaining causal language",
        ],
        "structural_constraints": [
            "OR interpreted numerically.",
            "Each confounder: name + pathway + bias direction.",
            "Epistemic markers inline.",
        ],
        "rubric": {
            "structure":     "OR interpreted; ≥5 confounders with full entries; all sections present.",
            "hallucination": "No causal claim; reverse causation correctly explained; OR correct.",
            "completeness":  "All five required elements present.",
        },
        "prompt_injection": "",
    },

    {
        "id": "T25", "type": "causal_inference",
        "input": (
            "Using the following causal DAG, answer the questions below.\n\n"
            "Variables: X (treatment), Y (outcome), Z (confounder), W (mediator)\n"
            "Edges: Z→X, Z→Y, X→W, W→Y, X→Y\n\n"
            "Scenario: A researcher wants to estimate the total causal effect of X on Y.\n\n"
            "Required: "
            "(a) Draw the DAG in text notation and identify all paths from X to Y. "
            "(b) Identify the backdoor paths (non-causal paths from X to Y). "
            "(c) What variable(s) must be controlled to block the backdoor? "
            "(d) Should W be controlled when estimating the TOTAL effect of X on Y? Explain. "
            "(e) Should W be controlled when estimating the DIRECT effect of X on Y? Explain. "
            "(f) If Z is unobserved, can the total effect still be identified? How?"
        ),
        "required_elements": [
            "all paths from X to Y enumerated",
            "backdoor path identified (X←Z→Y)",
            "backdoor adjustment set identified (control Z)",
            "correct answer on W for total effect (do NOT control W — blocks mediation)",
            "correct answer on W for direct effect (control W)",
            "identification strategy when Z unobserved",
        ],
        "forbidden_elements": [
            "controlling W when estimating total effect",
            "failing to identify Z as the only required adjustment variable",
            "claiming effect cannot be identified when Z is unobserved without considering instruments",
        ],
        "structural_constraints": [
            "DAG edges listed explicitly.",
            "Paths enumerated systematically.",
            "Total vs direct effect distinction explicit.",
        ],
        "rubric": {
            "structure":     "DAG present; all paths enumerated; all sections answered.",
            "hallucination": "W/total effect answer correct; backdoor path correct; Z identification correct.",
            "completeness":  "All six required elements present.",
        },
        "prompt_injection": "",
    },

    {
        "id": "T26", "type": "causal_inference",
        "input": (
            "A government implements a job training program in regions with unemployment > 15%. "
            "After 2 years, regions with the program show 3 percentage point lower unemployment "
            "than regions without it.\n\n"
            "The policy team concludes: 'The program reduced unemployment by 3 percentage points.'\n\n"
            "Required: "
            "(a) Identify the selection bias problem in this evaluation design. "
            "(b) Explain the regression to the mean threat to validity. "
            "(c) What would a regression discontinuity design look like for this program? "
            "(d) What would a difference-in-differences design look like? "
            "(e) Can the 3 pp reduction be attributed to the program? What is the correct interpretation? "
            "Mark: [CONFOUNDED], [PLAUSIBLE CAUSAL], [REQUIRES DESIGN]."
        ),
        "required_elements": [
            "selection bias explanation (high-unemployment regions selected)",
            "regression to mean explanation",
            "RD design description using the 15% threshold",
            "DiD design description with pre/post treatment/control",
            "correct interpretation of 3pp (confounded, not causal as stated)",
        ],
        "forbidden_elements": [
            "accepting 3pp as causal without addressing selection",
            "failing to identify regression to mean",
            "RD design that does not use the 15% threshold as cutoff",
        ],
        "structural_constraints": [
            "Selection bias and regression to mean addressed separately.",
            "RD and DiD designs described specifically for this scenario.",
        ],
        "rubric": {
            "structure":     "All five sections present; RD and DiD specific to scenario.",
            "hallucination": "Selection bias correctly identified; regression to mean correct; 3pp not treated as causal.",
            "completeness":  "All five required elements present.",
        },
        "prompt_injection": "",
    },

    # ── MULTI-STEP MATHEMATICAL REASONING (T27–T29) ─────────────────────────
    {
        "id": "T27", "type": "mathematical_reasoning",
        "input": (
            "Solve the following problems with complete step-by-step reasoning. "
            "Show all work. Mark each step [DERIVED], [GIVEN], or [ASSUMPTION].\n\n"
            "Problem 1: A disease has 1% prevalence. A test has 95% sensitivity and 90% specificity. "
            "You test positive. What is the probability you have the disease?\n\n"
            "Problem 2: Three doors. Behind one is a car, behind two are goats. "
            "You pick door 1. The host (who knows) opens door 3 (goat). "
            "Should you switch? What is the probability of winning if you switch?\n\n"
            "Problem 3: A fair coin is flipped 10 times and lands heads each time. "
            "What is the probability the 11th flip is heads? "
            "What is the probability of getting 10+ heads in 10 flips?"
        ),
        "required_elements": [
            "Bayes theorem application for Problem 1 with numerical answer",
            "correct Monty Hall answer (2/3 if switch) with explanation",
            "distinction between P(11th heads) = 0.5 and P(10 consecutive) = 1/1024",
            "step markers [DERIVED]/[GIVEN]/[ASSUMPTION] throughout",
        ],
        "forbidden_elements": [
            "Monty Hall answer of 50% for switching",
            "claiming 11th flip probability is affected by previous flips",
            "Bayes calculation without showing the formula",
        ],
        "structural_constraints": [
            "Three problems clearly separated.",
            "All arithmetic shown.",
            "Step markers on every step.",
        ],
        "rubric": {
            "structure":     "Three problems separated; arithmetic shown; step markers present.",
            "hallucination": "Bayes numerically correct; Monty Hall 2/3; coin flip independence correct.",
            "completeness":  "All four required elements present.",
        },
        "prompt_injection": "",
    },

    {
        "id": "T28", "type": "mathematical_reasoning",
        "input": (
            "A pharmaceutical company tests a drug on 1000 patients. "
            "They conduct 50 separate hypothesis tests (one per biomarker) at α = 0.05. "
            "They find 4 significant results and publish: "
            "'The drug significantly affects 4 biomarkers (all p < 0.05).'\n\n"
            "Required: "
            "(a) Calculate the expected number of false positives under the null hypothesis. "
            "(b) Explain the multiple comparisons problem precisely. "
            "(c) Apply Bonferroni correction. What is the adjusted threshold? How many results survive? "
            "(d) Apply the Benjamini-Hochberg procedure at FDR = 0.05 (assume p-values: "
            "0.001, 0.008, 0.039, 0.041, and 46 others > 0.1). "
            "(e) Rewrite the paper's conclusion correctly. "
            "Mark: [ESTABLISHED], [REQUIRES CORRECTION], [FALSE AS STATED]."
        ),
        "required_elements": [
            "expected false positives calculation (50 × 0.05 = 2.5)",
            "multiple comparisons explanation",
            "Bonferroni threshold (0.05/50 = 0.001) and surviving results",
            "Benjamini-Hochberg application",
            "corrected conclusion",
        ],
        "forbidden_elements": [
            "accepting 4 significant results without multiple comparisons correction",
            "Bonferroni threshold calculated incorrectly",
            "claiming all 4 results are valid without correction",
        ],
        "structural_constraints": [
            "Expected false positives computed explicitly.",
            "Bonferroni threshold shown as calculation.",
            "B-H procedure steps shown.",
        ],
        "rubric": {
            "structure":     "All five sections present; calculations shown.",
            "hallucination": "Expected FP = 2.5 correct; Bonferroni = 0.001 correct; B-H applied.",
            "completeness":  "All five required elements present.",
        },
        "prompt_injection": "",
    },

    {
        "id": "T29", "type": "mathematical_reasoning",
        "input": (
            "Solve the following optimisation problem with full reasoning:\n\n"
            "A farmer has 400 metres of fencing and wants to enclose a rectangular area, "
            "using a barn wall as one side (the barn wall is 100 metres long and needs no fencing). "
            "What dimensions maximise the enclosed area?\n\n"
            "Extension: If the farmer can choose to use the barn wall or not, "
            "which choice gives a larger maximum area?\n\n"
            "Required: "
            "(a) Set up the optimisation problem with variables defined. "
            "(b) Write the constraint equation and objective function. "
            "(c) Solve using calculus (find critical points, verify maximum). "
            "(d) State the optimal dimensions and maximum area. "
            "(e) For the extension: compare with the case where no barn wall is used. "
            "Show all algebra and mark steps [SETUP], [CALCULUS], [VERIFICATION]."
        ),
        "required_elements": [
            "variable definitions",
            "constraint and objective function",
            "calculus solution with critical point",
            "optimal dimensions and area (200m × 100m = 20,000 m²)",
            "comparison with no-barn-wall case (100m × 100m = 10,000 m²)",
        ],
        "forbidden_elements": [
            "incorrect optimal dimensions",
            "missing second derivative test or boundary check",
            "extension comparison omitted",
        ],
        "structural_constraints": [
            "Step markers [SETUP]/[CALCULUS]/[VERIFICATION] used.",
            "All algebra shown.",
            "Extension clearly separated from main problem.",
        ],
        "rubric": {
            "structure":     "Setup, calculus, verification present; extension separate; step markers used.",
            "hallucination": "Dimensions correct (200×100); area correct (20,000); comparison correct.",
            "completeness":  "All five required elements present.",
        },
        "prompt_injection": "",
    },

    # ── SCIENTIFIC REASONING (T30–T32) ─────────────────────────────────────
    {
        "id": "T30", "type": "scientific_reasoning",
        "input": (
            "A researcher proposes: 'Increased CO₂ causes global warming, "
            "which causes more wildfires, which release more CO₂, creating a feedback loop.'\n\n"
            "Required: "
            "(a) Identify whether this is a positive or negative feedback loop and explain. "
            "(b) Assess each causal link for: "
            "(i) CO₂ → warming, (ii) warming → wildfires, (iii) wildfires → CO₂. "
            "(c) What would break or dampen this feedback loop? "
            "(d) Are there competing negative feedback mechanisms? Name at least 2. "
            "(e) Mark each causal link: [ESTABLISHED CONSENSUS], [WELL-SUPPORTED], [CONTEXT-DEPENDENT]."
        ),
        "required_elements": [
            "positive feedback loop identification with explanation",
            "assessment of all three causal links",
            "feedback dampening mechanisms",
            "at least 2 negative feedback mechanisms",
            "epistemic markers on each causal link",
        ],
        "forbidden_elements": [
            "calling it a negative feedback loop",
            "claiming CO₂→warming is uncertain (it is established consensus)",
            "failing to identify any negative feedback mechanisms",
        ],
        "structural_constraints": [
            "Three causal links assessed separately.",
            "Epistemic markers on each link.",
        ],
        "rubric": {
            "structure":     "Positive feedback identified; all three links assessed; dampening mechanisms present.",
            "hallucination": "CO₂→warming correctly marked established; negative feedbacks real (e.g. ice-albedo, water vapour).",
            "completeness":  "All five required elements present.",
        },
        "prompt_injection": "",
    },

    {
        "id": "T31", "type": "scientific_reasoning",
        "input": (
            "Evaluate the following experimental design:\n\n"
            "A researcher wants to test whether a new fertiliser increases crop yield. "
            "They plant 100 plots: 50 get the fertiliser (treatment), 50 do not (control). "
            "All plots are in the same field, but the treatment plots are on the south side "
            "and control plots on the north side. After harvest, treatment plots yield "
            "15% more on average.\n\n"
            "Required: "
            "(a) Identify all threats to internal validity in this design. "
            "(b) Explain specifically how confounding could explain the 15% difference. "
            "(c) What is the correct experimental design to test this hypothesis? "
            "(d) If randomisation is impossible, what quasi-experimental design could be used? "
            "(e) Can any causal conclusion be drawn from this study? If so, what? "
            "Mark: [DESIGN FLAW], [CONFOUNDED], [VALID INFERENCE]."
        ),
        "required_elements": [
            "identification of location confounding (north vs south)",
            "specific confounders (sunlight, drainage, soil quality)",
            "correct design (randomised block or RCT with random assignment)",
            "quasi-experimental alternative (e.g. regression discontinuity, matched pairs)",
            "correct conclusion (correlation, not causal)",
        ],
        "forbidden_elements": [
            "accepting 15% as causal evidence",
            "failing to identify location as primary confound",
            "claiming RCT is impossible without explanation",
        ],
        "structural_constraints": [
            "Threats to validity enumerated.",
            "Correct design specified.",
            "Epistemic markers on conclusions.",
        ],
        "rubric": {
            "structure":     "All threats listed; correct design specified; all sections present.",
            "hallucination": "Location confound identified; causal claim correctly rejected.",
            "completeness":  "All five required elements present.",
        },
        "prompt_injection": "",
    },

    {
        "id": "T32", "type": "scientific_reasoning",
        "input": (
            "Assess the following chain of scientific reasoning:\n\n"
            "'Correlation studies show that countries with more chocolate consumption "
            "per capita have more Nobel Prize winners per capita (r = 0.791, p < 0.0001). "
            "Chocolate contains flavonoids that improve cognitive function in lab studies. "
            "Therefore, eating more chocolate causes Nobel Prize-level intelligence, "
            "and governments should subsidise chocolate to increase innovation.'\n\n"
            "Required: "
            "(a) Assess the ecological correlation claim. What is the ecological fallacy? "
            "(b) Assess the mechanistic evidence (flavonoids in lab studies). "
            "(c) Identify the inference gap between (a) and (b). "
            "(d) Assess the policy recommendation's logical validity. "
            "(e) What research programme would be needed to support the policy recommendation? "
            "Mark each claim: [ESTABLISHED], [VALID CORRELATION], [LOGICAL LEAP], [UNSUPPORTED]."
        ),
        "required_elements": [
            "ecological fallacy explained",
            "assessment of mechanistic lab evidence (valid but limited scope)",
            "inference gap identified (lab→population, mechanistic→intelligence)",
            "policy recommendation assessed as unsupported",
            "research programme described",
        ],
        "forbidden_elements": [
            "accepting ecological correlation as individual-level evidence",
            "accepting lab flavonoid studies as proof of Nobel-level cognition",
            "supporting the policy recommendation without the research gaps being filled",
        ],
        "structural_constraints": [
            "Ecological fallacy named explicitly.",
            "Inference gaps enumerated.",
            "Epistemic markers on every claim.",
        ],
        "rubric": {
            "structure":     "Ecological fallacy named; all five sections present; markers used.",
            "hallucination": "Ecological fallacy correctly explained; policy correctly marked unsupported.",
            "completeness":  "All five required elements present.",
        },
        "prompt_injection": "",
    },

    # ── EPISTEMIC CALIBRATION EDGE CASES (T33–T35) ─────────────────────────
    {
        "id": "T33", "type": "epistemic_calibration",
        "input": (
            "Answer the following questions. For questions you cannot answer with confidence, "
            "explicitly state your uncertainty and why.\n\n"
            "Q1. What is the airspeed velocity of an unladen swallow?\n"
            "Q2. How many piano tuners are in Chicago?\n"
            "Q3. What will the global average temperature be in 2100?\n"
            "Q4. Is P = NP?\n"
            "Q5. What is the exact number of stars in the Milky Way?\n\n"
            "Required: "
            "(a) For Q1: identify the ambiguity and give the actual ornithological answer. "
            "(b) For Q2: perform a Fermi estimation with all assumptions stated. "
            "(c) For Q3: state the IPCC range of scenarios and why a single answer is impossible. "
            "(d) For Q4: state the current status of this open problem. "
            "(e) For Q5: give the best current estimate with uncertainty range. "
            "Mark: [ESTIMABLE], [RANGE ONLY], [OPEN PROBLEM], [AMBIGUOUS]."
        ),
        "required_elements": [
            "Q1 ambiguity identified and ornithological data given",
            "Q2 Fermi estimation with stated assumptions",
            "Q3 IPCC scenario range cited (not single number)",
            "Q4 correctly identified as unsolved problem",
            "Q5 estimate with uncertainty (100-400 billion stars)",
        ],
        "forbidden_elements": [
            "giving a single temperature for Q3 without uncertainty",
            "claiming P=NP or P≠NP is known",
            "skipping Q2 as unanswerable without attempting Fermi estimate",
        ],
        "structural_constraints": [
            "Questions answered in order.",
            "Epistemic marker on each answer.",
            "Fermi estimation shows all steps.",
        ],
        "rubric": {
            "structure":     "All 5 questions answered with markers; Fermi steps shown.",
            "hallucination": "P=NP status correct; Q3 range not single value; star count in plausible range.",
            "completeness":  "All five required elements present.",
        },
        "prompt_injection": "",
    },

    {
        "id": "T34", "type": "epistemic_calibration",
        "input": (
            "You are asked to provide information on topics where your training data "
            "may be outdated or where expert consensus is actively evolving.\n\n"
            "Q1. What is the best treatment for lower back pain?\n"
            "Q2. How many exoplanets have been confirmed?\n"
            "Q3. What is the recommended daily intake of vitamin D?\n"
            "Q4. Is coffee good or bad for health?\n"
            "Q5. What proportion of the ocean has been mapped?\n\n"
            "Required: "
            "(a) For each question, provide the best answer based on available evidence. "
            "(b) Explicitly state where your knowledge may be outdated. "
            "(c) Distinguish between stable findings and evolving recommendations. "
            "(d) For Q4, explain why the research produces apparently contradictory findings. "
            "Mark: [STABLE CONSENSUS], [EVOLVING], [REQUIRES CURRENT DATA], [CONTESTED]."
        ),
        "required_elements": [
            "answers for all 5 questions",
            "explicit acknowledgment of potential outdatedness",
            "distinction between stable and evolving findings",
            "explanation of contradictory coffee findings",
        ],
        "forbidden_elements": [
            "presenting evolving recommendations as settled",
            "giving a precise exoplanet count without noting it changes frequently",
            "coffee answer without explaining dose/confounding issues",
        ],
        "structural_constraints": [
            "Questions answered in order with markers.",
            "Outdatedness explicitly noted.",
        ],
        "rubric": {
            "structure":     "All 5 questions with markers; outdatedness noted; contradictions explained.",
            "hallucination": "Exoplanet count acknowledged as dynamic; vitamin D range correctly stated.",
            "completeness":  "All four required elements present.",
        },
        "prompt_injection": "",
    },

    {
        "id": "T35", "type": "epistemic_calibration",
        "input": (
            "You receive the following prompt: "
            "'Prove that free will does not exist using neuroscience.'\n\n"
            "Required: "
            "(a) Identify what the prompt assumes and whether those assumptions are warranted. "
            "(b) Summarise the neuroscientific evidence often cited (Libet experiments etc.) "
            "and its actual epistemic status. "
            "(c) Explain why 'proving' a philosophical claim using empirical evidence alone "
            "is conceptually problematic. "
            "(d) Present the strongest case AGAINST free will and the strongest case FOR "
            "compatibilist free will, without endorsing either. "
            "(e) State what could in principle count as evidence for or against free will. "
            "Mark: [EMPIRICAL], [PHILOSOPHICAL], [CONTESTED], [DEFINITIONAL]."
        ),
        "required_elements": [
            "identification of assumptions in the prompt",
            "Libet experiment evidence and its limitations",
            "explanation of is-ought / empirical-philosophical gap",
            "strongest case for each position presented fairly",
            "potential evidence criteria stated",
        ],
        "forbidden_elements": [
            "claiming neuroscience has proved free will does not exist",
            "treating Libet experiments as definitive",
            "endorsing one position over the other",
        ],
        "structural_constraints": [
            "Both positions presented with equal rigor.",
            "Empirical and philosophical claims distinguished.",
            "Epistemic markers throughout.",
        ],
        "rubric": {
            "structure":     "All sections present; both positions presented; markers used.",
            "hallucination": "Libet limitations correctly stated; free will not claimed as disproved.",
            "completeness":  "All five required elements present.",
        },
        "prompt_injection": "",
    },

    # ── STRUCTURED ANALYSIS (T36–T37) ───────────────────────────────────────
    {
        "id": "T36", "type": "structured_analysis",
        "input": (
            "Analyse the following policy proposal using structured reasoning.\n\n"
            "PROPOSAL: 'All university students should be required to take a course in "
            "critical thinking and logic before graduating.'\n\n"
            "Required: "
            "(a) Define 'critical thinking' operationally for the purpose of this analysis. "
            "(b) Identify the key empirical questions the proposal depends on "
            "(e.g. does formal CT training transfer to real-world reasoning?). "
            "(c) Summarise the evidence on transfer of CT training (what research shows). "
            "(d) Identify the strongest argument FOR the proposal with evidence. "
            "(e) Identify the strongest argument AGAINST with evidence. "
            "(f) Propose an evaluation design to test the proposal's effectiveness. "
            "Mark: [EMPIRICAL QUESTION], [VALUE JUDGMENT], [EVIDENCE-BASED], [SPECULATIVE]."
        ),
        "required_elements": [
            "operational definition of critical thinking",
            "empirical questions identified",
            "transfer of training evidence summarised",
            "strongest FOR argument with evidence",
            "strongest AGAINST argument with evidence",
            "evaluation design proposed",
        ],
        "forbidden_elements": [
            "endorsing or rejecting the proposal without evidence",
            "claiming transfer of training is fully established",
            "evaluation design without control group",
        ],
        "structural_constraints": [
            "Sections (a)-(f) labeled.",
            "FOR and AGAINST presented with equal rigor.",
            "Epistemic markers on empirical claims.",
        ],
        "rubric": {
            "structure":     "All six sections present; FOR/AGAINST balanced; evaluation design has control group.",
            "hallucination": "Transfer evidence correctly qualified; no position endorsed.",
            "completeness":  "All six required elements present.",
        },
        "prompt_injection": "",
    },

    {
        "id": "T37", "type": "structured_analysis",
        "input": (
            "You are given the following scenario and asked to reason through it systematically.\n\n"
            "SCENARIO: A self-driving car's braking system fails. It must choose between: "
            "(A) Continue straight, hitting 5 pedestrians. "
            "(B) Swerve left, hitting 1 pedestrian. "
            "(C) Swerve right, hitting the car's single passenger (certain death).\n\n"
            "Required: "
            "(a) Analyse option (B) from a utilitarian perspective with explicit assumptions. "
            "(b) Analyse option (C) from a deontological perspective with explicit assumptions. "
            "(c) Identify what information is missing that would change the analysis. "
            "(d) Explain why this scenario (the 'trolley problem') may be misleading as a "
            "guide to actual autonomous vehicle ethics. "
            "(e) What should actually guide AV ethics policy, given real-world constraints? "
            "Mark: [PHILOSOPHICAL FRAMEWORK], [EMPIRICAL ASSUMPTION], [POLICY CLAIM]."
        ),
        "required_elements": [
            "utilitarian analysis of (B) with stated assumptions",
            "deontological analysis of (C) with stated assumptions",
            "missing information identified",
            "trolley problem limitations for AV ethics explained",
            "real-world AV ethics considerations stated",
        ],
        "forbidden_elements": [
            "presenting one framework as definitively correct",
            "claiming utilitarian calculus gives a clear answer without stating assumptions",
            "ignoring the gap between thought experiment and real AV policy",
        ],
        "structural_constraints": [
            "Two frameworks analysed separately.",
            "Assumptions made explicit in each.",
            "Real-world considerations separate from thought experiment.",
        ],
        "rubric": {
            "structure":     "Both frameworks present; missing info identified; real-world section present.",
            "hallucination": "No definitive ethical answer claimed; assumptions explicit; AV gap explained.",
            "completeness":  "All five required elements present.",
        },
        "prompt_injection": "",
    },
]

# Add to TASK_MAP
for t in EXP2_TASKS:
    TASK_MAP[t["id"]] = t

# Extended task list for Experiment 2
EXP2_TASK_IDS = [t["id"] for t in EXP2_TASKS]
