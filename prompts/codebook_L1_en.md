# KuKi Annotation Codebook v0.3 — Layer 1: Entity Roles

## What counts as the article

- Annotate the content as provided.
- Your personal opinion about the frames or the entities is irrelevant and must not influence any label. Annotate how the text frames things, not whether you agree.

**Golden rule.** Label what is in the text, as a careful ordinary reader of that language and culture would understand it; not what you privately know to be true, and not what you suspect the author "really" means without textual support.

## Layer 1 — Entity Roles (NER)

Adapted from SemEval-2025 Task 10, Subtask 1. We keep only the three top-level roles and drop all 22 fine-grained sub-roles. This collapse is deliberate: the coarse level transfers across languages far more reliably than the fine level.

### Definition of a Named-Entity

- Named entities in a broad sense:
  - Traditional named entities: Specific persons, organisations, and locations (e.g., "Vladimir Putin," "the UN," "Moscow").
  - Toponym-derived and affiliation entities: Phrases that indicate a group or collective identity based on a place, political, military, or organizational affiliation (e.g., "Trump supporters," "residents of Ukraine," "Russian forces," "European officials," "Russian President Vladimir Putin").
- The Centrality Rule: You must only annotate named entities that are central to the article's narrative. Determining centrality requires a careful reading of the text. If an entity does not drive the story or suffer its main impacts, leave it unannotated.
- Descriptive entity expressions. When a named entity is modified by a descriptive title, function, or affiliation, annotate the entire entity expression, including the descriptor.
  - "Russian President Vladimir Putin" → annotate the whole phrase, not only "Vladimir Putin".
  - "former US President Donald Trump" → annotate the whole phrase.
  - "NATO Secretary General Mark Rutte" → annotate the whole phrase.
  The entity span should include all words that directly identify or describe the entity. Do not include surrounding words that merely describe an action or event.
- What NOT to annotate:
  - Generic / unnamed entities: Do not annotate purely nominal entity mentions such as "migrants," "the public," or "citizens."
  - Settings without roles: Do not annotate locations or organizations if they are just the backdrop of the story and do not act or suffer harm.

### Decision rules

1. Annotate the complete entity span on its first relevant occurrence.
2. If two entities are nested or overlap, prefer the most complete meaningful entity expression. For example, annotate "Russian President Vladimir Putin" rather than only "Vladimir Putin".
3. Do not annotate later pronouns referring to an already annotated entity (e.g., he, she, they, him, her, them, it).
4. A repeated explicit mention of the same entity does not need to be annotated again if its role remains unchanged.
5. If the entity is presented in a different role later in the article, annotate the first mention where that new role becomes clear.
6. If it is unclear whether two mentions refer to the same entity, prefer annotation over omission. When in doubt, annotate the more complete plausible entity span rather than risk missing a relevant entity.
7. Use the NONE label only when the text contains no central entity that drives the narrative. This applies, for example, to neutral mentions of entities that do not play a meaningful role in the text.
   Important: Do not use NONE simply because an entity has a neutral role. NONE should primarily be used when no clear narrative structure is present, such as in short news summaries, event listings, or chronological overviews that simply report a sequence of events without establishing clear protagonists, antagonists, or innocent parties.

### Examples

**Test Case 1: Location as a mere setting.** "NATO troops in Africa handing out candy to the people."
- "NATO troops" is an affiliation entity doing a virtuous act → Annotate as PROTAGONIST.
- "Africa" is a named location, but it is merely the setting here. It is not acting or suffering harm → Do not annotate.
- "the people" are the beneficiaries, but it is a generic, unnamed phrase → Do not annotate.

**Test Case 2: Location as an active entity.** "Moscow threatened to cut off the winter gas supply to Europe."
- "Moscow" is a named location, but here it acts as a political entity (a government) issuing a threat → Annotate as ANTAGONIST.
- "Europe" is a named location, but here it is the direct target of the threat and potential harm → Annotate as INNOCENT.

**Test Case 3: When to use NONE.** The text provides a neutral chronological overview of events. No entity is presented as a clear PROTAGONIST, ANTAGONIST, or INNOCENT.
- "On Monday, the government announced the new measures. On Tuesday, parliament discussed the proposal. On Wednesday, the measures were approved." → NONE
- "The government introduced the new measures to protect vulnerable citizens, while opposition leaders accused it of deliberately harming low-income families." → Do not use NONE. The text establishes a clear narrative structure: the government is presented as an actor and the low-income families as affected parties. The relevant entities should therefore receive the appropriate role labels.

If an entity is genuinely neutral, reported on factually with no positive or negative slant and no harm → do not force a role. Leave it unannotated. Only the three roles exist; neutrality is expressed by absence.

### The three roles or None

**PROTAGONIST — the hero / the good actor**
- Definition. An entity the text presents positively: protecting values or people, doing good, standing up against a stronger force, acting virtuously, seeking peace, or fighting for change. The "good guy" of the article's story.
- Look for. praise, admiration, framing as defender/guardian/victorious-underdog, moral approval, sympathy for a just cause.
- Example. An article that portrays volunteers delivering aid under shelling as selfless and brave casts those volunteers as PROTAGONIST.

**ANTAGONIST — the villain / the bad actor**
- Definition. An entity the text presents negatively as a source of harm, threat, or wrongdoing: aggressor, oppressor, deceiver, corrupt actor, conspirator, traitor, foreign adversary, incompetent, etc. The "bad guy" of the article's story.
- Look for. blame, accusation, framing as threat/aggressor/liar/corrupt, moral condemnation, attribution of bad motives.
- Example. An article describing a foreign government as orchestrating a covert plot to destabilise the country casts that government as ANTAGONIST.

**INNOCENT — the victim / the harmed party**
- Definition. An entity presented as suffering harm, being exploited, overlooked, or unjustly blamed, through no fault of their own. They are acted upon rather than acting. Distinct from PROTAGONIST: the innocent does not necessarily fight back or embody virtue; they are primarily harmed.
- Look for. suffering, harm, loss, being exploited/forgotten/scapegoated, helplessness, sympathy without heroism.
- Example. An article focusing on displaced families who lost their homes, with no agency of their own in the events, casts those families as INNOCENT.

**NONE — when no other entity could be identified**
- Definition. NONE is a document-level status used when no qualifying role-bearing entity is present.
- Example. The text provides a neutral chronological overview of events. No entity is presented as a clear PROTAGONIST, ANTAGONIST, or INNOCENT.
- In your answer, NONE means returning no entity roles.

### Annotated mini-example

Content: "While ordinary families struggle to pay their heating bills, the so-called reformers in the ministry — long known as puppets of foreign capitals — pushed through a law that experts warn will cripple the economy. Either we reverse course now, or our children inherit ruin. The people have had enough."

- "ordinary families" → INNOCENT; "the reformers / ministry" → ANTAGONIST.
- Why: Families suffer (heating bills) without agency; officials are blamed and discredited.
