# Phase 8.2-G Freeze Log: Section IV Canonical Freeze

**Project:** Paper 1 — *Turn-Aware Search and Road-Impedance Modelling for Two-Wheeler Routing in Urban Road Networks*  
**Target Venue:** CSNT 2027 (IEEE Conference Format, Standard Two-Column `IEEEtran`, 6.0 Pages Max)  
**Phase:** Phase 8.2-G — Section IV Canonical Freeze  
**Date:** 2026-11-06  
**Document:** [`phase_8_2_freeze_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_2_freeze_log.md)  
**Canonical Frozen Drafts:**
- [`paper1_section_IV_A_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_A_draft_v2.md) (Version 2.0)
- [`paper1_section_IV_B_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_B_draft_v2.md) (Version 2.0)
- [`paper1_section_IV_C_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_C_draft_v2.md) (Version 2.0)
- [`paper1_section_IV_D_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_D_draft_v2.md) (Version 2.0)
**Applied Skills:** [`blrmap-research-protocol`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/blrmap-research-protocol/SKILL.md), [`evidence-integrity-audit`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/.agents/skills/evidence-integrity-audit/SKILL.md)  
**Status:** **SECTION IV CANONICAL MANUSCRIPT FROZEN (APPROVED BY RESEARCH LEAD)**  

---

## 1. Formal Freeze Declaration

By explicit decision of the Research Lead, Section IV of Paper 1 (*Turn-Aware A\* Algorithm, Correctness and Complexity Analysis*) has successfully passed integrated technical and editorial review (Phase 8.2-F) and is hereby declared **CANONICALLY FROZEN** across all four modular subsections (IV-A through IV-D, Version 2.0).

The canonical frozen draft files are located at:
1. Subsection IV-A: [`research/paper1_manuscript/paper1_section_IV_A_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_A_draft_v2.md)
2. Subsection IV-B: [`research/paper1_manuscript/paper1_section_IV_B_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_B_draft_v2.md)
3. Subsection IV-C: [`research/paper1_manuscript/paper1_section_IV_C_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_C_draft_v2.md)
4. Subsection IV-D: [`research/paper1_manuscript/paper1_section_IV_D_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_D_draft_v2.md)

Under project research protocol and version-control governance, **no further modifications, rewrites, refactorings, or word substitutions may be made to these files without explicit written authorization from the Research Lead.**

---

## 2. Integrated Review & Quality Verification Lifecycle

The freeze of Section IV represents the rigorous execution of the Phase 8 research plan:

1. **Phase 8.1 (Structural Planning & Admissibility Evidence Mapping):**
   - Constructed [`paper1_section_IV_structural_blueprint_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_structural_blueprint_v1.md) and [`paper1_section_IV_mathematical_evidence_map_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_mathematical_evidence_map_v1.md).
   - Reconstructed two-wheeler A\* algorithm execution step by step from [`routing/algorithms.py`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/routing/algorithms.py) ([`phase_8_1_implementation_audit.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_implementation_audit.md)).
   - Executed semantic precision check Phase 8.1-U ([`phase_8_1_U_final_consistency_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_1_U_final_consistency_log.md)) establishing exact priority-queue pop terminology ($119$–$129,619$ pops) vs. theoretical cardinality ($740,823$).
2. **Phase 8.2-A through 8.2-D (Modular Prose Drafting):**
   - Authored Section IV-A v1.0 (Search Architecture, 142 words).
   - Authored Section IV-B v1.0 (Scaled Haversine Heuristic, 106 words).
   - Authored Section IV-C v1.0 (Admissibility & Consistency Proofs, 190 words).
   - Authored Section IV-D v1.0 (Computational Complexity Analysis, 141 words).
3. **Phase 8.2-E (Controlled Section IV Compression):**
   - Executed a surgical, zero-loss compression pass ([`phase_8_2_E_compression_log.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/phase_8_2_E_compression_log.md)), reducing cumulative whitespace word count from $579$ to $529$ words ($-8.6\%$).
   - Eliminated the $+19$-word overrun above the $560$-word blueprint ceiling, creating $21$ words of headroom below the $550$-word target and $31$ words below the $560$-word ceiling.
   - Preserved all v1 baselines byte-for-byte and generated corresponding v2.0 files.
   - Refined queue-extraction semantics in IV-C to accurately reflect non-decreasing key extraction without suggesting stale-entry filtering.
4. **Phase 8.2-F (Integrated Section IV Review):**
   - Evaluated the four compressed subsections continuously as one unified narrative.
   - Verified 100% mathematical consistency with frozen [Section III](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md) ($E_s, S, s, s', s_0, t, c_{\min}, P_{\text{turn}}, \mu, \ell, D_{\text{haversine}}$).
   - Verified monotonic equation sequence continuing from Section III Eqs. (1)–(3) to Section IV Eqs. (4)–(6).
   - Verified exact representation of all 4 heuristic conditions, multigraph parallel link minimization, heap duplicate semantics, and empirical vs. theoretical bounds.
   - Rendered overall verdict: **APPROVE (Zero Defect)**.

---

## 3. Canonical Frozen Artifacts & Cryptographic Fingerprints

The four canonical Section IV v2 draft files are cryptographically locked with the following SHA-256 digests:

| Subsection | Title | Canonical File Path | Word Count (Whitespace) | Word Count (Math-as-Token) | Display Equations | SHA-256 Digest |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **IV-A** | Search Architecture | [`paper1_section_IV_A_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_A_draft_v2.md) | **129 words** | 109 words | 0 | `8B86B3722895AA85E564A101538C38065F8650443B4A08C0C708CC386C3D7CEE` |
| **IV-B** | Heuristic Formulation | [`paper1_section_IV_B_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_B_draft_v2.md) | **90 words** | 83 words | 1 (Eq. 4) | `CB88AC8A92633F59F3CD322D1E6966B4426A1DE5295058BE6ED0A39A7EDEFEB6` |
| **IV-C** | Correctness Proofs | [`paper1_section_IV_C_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_C_draft_v2.md) | **185 words** | 146 words | 1 (Eq. 5) | `08262BE23D7423B7721FDF13FEED893F37C39168B67F416D45F0B06628FCC4C1` |
| **IV-D** | Complexity Analysis | [`paper1_section_IV_D_draft_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_D_draft_v2.md) | **125 words** | 114 words | 1 (Eq. 6) | `B1A07D5CD0958EED1394211BAEAF27766779DC69A6B4B3283B397B29E83EC772` |
| **TOTAL** | **Section IV Complete** | — | **529 words** | **452 words** | **3 (Eqs. 4–6)** | **FROZEN CANONICAL SUITE** |

### Page Budget Compliance Summary:
- **Cumulative Whitespace Word Count:** **529 words** ($\le 550$ words ceiling compliant; $-21\text{ words}$ headroom).
- **Cumulative Math-Token Word Count:** **452 words** (Fits comfortably in 450–500 word structural allocation).
- **Display Equation Budget:** Exactly **3 display equations** (Equations 4, 5, 6), matching page layout quotas.
- **Float Assets:** Exactly **0 algorithms/figures**, leaving column space for mathematics and body prose.

---

## 4. Preserved Mathematical Formulations and Equations

The canonical frozen text establishes the following explicit mathematical relationships:

1. **Equation (4) (Subsection IV-B):** Scaled Haversine Heuristic:
   $$h(s) = \mu_{\min} \cdot D_{\text{haversine}}(v, t) = 0.80 \cdot D_{\text{haversine}}(v, t) \tag{4}$$
   *Properties:* Evaluates at arrival vertex $v$ for $s=(u,v)$; evaluates at origin vertex $s_0$ for synthetic root $(\text{None}, s_0)$; $\mu_{\min}=0.80$ is the Table I grade-separated flyover override verified as the empirical minimum on the Bengaluru graph; vanishes at destination ($h(s)=0.0$).

2. **Equation (5) (Subsection IV-C):** Monotonic Consistency Condition:
   $$h(s) \le c(s,s') + h(s') \tag{5}$$
   *Properties:* Proved from (i) $\mu(e) \ge 0.80$, (ii) $P_{\text{turn}} \ge 0.0$, (iii) $\ell(v,w) \ge D_{\text{haversine}}(v,w)$, and (iv) spherical triangle inequality; parallel-edge minimum selection preserves the lower bound: $c_{\min}(v,w) = \min_k [\mu(v,w,k)\ell(v,w,k)] \ge 0.80 D_{\text{haversine}}(v,w)$; synthetic root base case holds ($P_{\text{turn}}(\text{None}, s_0, w) = 0.0$); path induction establishes admissibility $h(s) \le C^*(s)$; guarantees optimality when a state's current-best queue entry is first extracted without state reopening.

3. **Equation (6) (Subsection IV-D):** Asymptotic Complexity Bounds:
   $$\begin{aligned}
   \mathcal{T}_{\text{general}} &= \mathcal{O}\left( |E_s| d_{\max}^{\text{out}} \log(|E_s| d_{\max}^{\text{out}}) + q_{\max} |E_s| d_{\max}^{\text{in}} d_{\max}^{\text{out}} \right) \\
   \mathcal{M}_{\text{general}} &= \mathcal{O}(|E_s| d_{\max}^{\text{out}} + |V|)
   \end{aligned} \tag{6}$$
   *Properties:* Accounts for $|E_s|+1$ edge states, binary min-heap without `decrease-key`, duplicate pushes on strict relaxation, stale-entry pop processing, and parallel candidate scanning up to $q_{\max}$; simplifies conditionally to $\mathcal{T}_{\text{urban}} = \mathcal{O}(|E_s| \log |E_s|)$ and $\mathcal{M}_{\text{urban}} = \mathcal{O}(|E_s|)$ under bounded valence ($d_{\max}^{\text{in}}, d_{\max}^{\text{out}}, q_{\max} = \mathcal{O}(1)$); rigorously demarcates theoretical saturation limits ($5,886,792$ iterations and $3,877,450$ logical entries) from empirical query-level performance ($119$–$129,619$ queue pops across 25 corridors; $174.93\text{ ms}$ median latency).

---

## 5. Frozen Asset Invariance Audit

The cryptographic integrity of all previously frozen project artifacts was verified prior to and immediately following this freeze operation:

| File Name | Governing Phase | Status | Expected SHA-256 Fingerprint | Verified SHA-256 Fingerprint | Match Status |
| :--- | :---: | :---: | :--- | :--- | :---: |
| [`paper1_abstract_v2.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_abstract_v2.md) | Phase 5.5 | FROZEN | `67272764F7DA31239CE7E41FAE77C4C122991F52B0AE47E064F6B946334DB142` | `67272764F7DA31239CE7E41FAE77C4C122991F52B0AE47E064F6B946334DB142` | **VERIFIED** |
| [`paper1_introduction_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_introduction_v1.md) | Phase 5.5 | FROZEN | `3271BE72BA4A3D850A3DE44AA3EE03E2A01ADD66FEB6326FD73EE99AE1B64141` | `3271BE72BA4A3D850A3DE44AA3EE03E2A01ADD66FEB6326FD73EE99AE1B64141` | **VERIFIED** |
| [`paper1_related_work_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_related_work_v1.md) | Phase 6.3 | FROZEN | `839C1D5936F764C268F3245A8EE7289E8CEFC542A3858BF32D29A38DB2CA21BA` | `839C1D5936F764C268F3245A8EE7289E8CEFC542A3858BF32D29A38DB2CA21BA` | **VERIFIED** |
| [`paper1_section_III_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_III_v1.md) | Phase 7.2-W | FROZEN | `CEE2B6A495D0498862A3A395DCFC424661666ADB27D8DE0CEF23CB33692C9061` | `CEE2B6A495D0498862A3A395DCFC424661666ADB27D8DE0CEF23CB33692C9061` | **VERIFIED** |
| [`paper1_verified_references.bib`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_literature/paper1_verified_references.bib) | Phase 5.5 | FROZEN | `7F05C88479225D4AB84B3529EBB22528420A1D40CD182B26698A9370416BA028` | `7F05C88479225D4AB84B3529EBB22528420A1D40CD182B26698A9370416BA028` | **VERIFIED** |
| [`paper1_section_IV_A_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_A_draft_v1.md) | Phase 8.2-A | PRESERVED BASELINE | `3D9F80D39EB74A1BC2AF2A478FBF7BFA5B6FEFCEBC53B55FE66CE40B9CF46F54` | `3D9F80D39EB74A1BC2AF2A478FBF7BFA5B6FEFCEBC53B55FE66CE40B9CF46F54` | **VERIFIED** |
| [`paper1_section_IV_B_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_B_draft_v1.md) | Phase 8.2-B | PRESERVED BASELINE | `090C5C4212D5EB943BFD0ED4087BA48CD48705F049BF9BE307C0AEF9D284EF06` | `090C5C4212D5EB943BFD0ED4087BA48CD48705F049BF9BE307C0AEF9D284EF06` | **VERIFIED** |
| [`paper1_section_IV_C_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_C_draft_v1.md) | Phase 8.2-C | PRESERVED BASELINE | `678D4D6B5EE1C898319F4F648D6CFF05284B91230B4800249D42D4AFDF024C4E` | `678D4D6B5EE1C898319F4F648D6CFF05284B91230B4800249D42D4AFDF024C4E` | **VERIFIED** |
| [`paper1_section_IV_D_draft_v1.md`](file:///C:/Users/comps/Desktop/Final Year Project/BLRMap_Prototype/research/paper1_manuscript/paper1_section_IV_D_draft_v1.md) | Phase 8.2-D | PRESERVED BASELINE | `9B5E94CE336EF196230C863B2CE293582BF5C431FAEB55767F33EE2A05B37466` | `9B5E94CE336EF196230C863B2CE293582BF5C431FAEB55767F33EE2A05B37466` | **VERIFIED** |

---

## 6. Research Governance Directives & Stop Protocol

1. **Section IV Status:** Officially **CANONICALLY FROZEN** as of Phase 8.2-G (2026-11-06).
2. **Subsections IV-A through IV-D v2.0:** Locked against further modification.
3. **Assembly Scope:** Full-manuscript assembly (`paper1_manuscript_v1.md` or `paper1_section_IV_v1.md`) has **NOT** been executed, in strict compliance with the Phase 8.2-G mandate.
4. **Subsequent Drafting:** Drafting of subsequent manuscript sections (e.g. Section V) has **NOT** been initiated.
5. **Next Authorized Phase:** Stand by for Research Lead instructions regarding Section IV unified assembly or transition to Phase 9.0 planning.
