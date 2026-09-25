# KuKi Annotation Codebook v0.3 — Layer 2: Frames

## What counts as the article

- Annotate the content as provided.
- Your personal opinion about the frames or the entities is irrelevant and must not influence any label. Annotate how the text frames things, not whether you agree.

**Golden rule.** Label what is in the text, as a careful ordinary reader of that language and culture would understand it; not what you privately know to be true, and not what you suspect the author "really" means without textual support.

## Layer 2 — Frames

Adapted from SemEval-2023 Task 3, Subtask 2, which uses the 14 generic frames of the Media Frames Corpus (Card et al., 2015). A frame is the angle or aspect the article foregrounds — the perspective from which the topic is presented. This is a document-level, multi-label task: most articles use more than one frame.

### Definition

A frame is a strategic device for representing the different salient aspects and perspectives of an issue, in order to convey a particular latent meaning about it (Entman, 1993). The same topic can be discussed from different perspectives; the frame is the perspective — which aspects of the issue the article selects and makes salient.

Frame is not topic. The topic is what the article is about ("the war," "a new pension law"). The frame is the angle through which that topic is presented (its costs, its legality, the threat it poses, its morality). One topic can be framed many ways; the same frame can appear across many topics.

What is NOT a frame. A passing mention is not a frame — the angle must be actually developed. The article's subject matter, its named entities, and its stance (for/against) are not frames. "An article about NATO" names a topic; whether it foregrounds NATO's military threat (Security & defense) or its budget (Economic) is the frame.

### Decision rules

- Multi-label. Assign every frame the article genuinely foregrounds. Multiple frames per text are possible.
- Foregrounded, not merely mentioned. A frame counts only if the article actually develops that angle and not because a single word brushes past it.
- Frame ≠ topic. "The war" is a topic; whether the article discusses it through casualties and threat (Security & defense), sanctions and prices (Economic), or international standing (External regulation & reputation) is the frame.
- Two of the most common frames in political news are Political and Security & defense. Do not over-apply them — assign only when that angle is actually developed.

### The 14 frames — overview

| Frame | The article foregrounds… |
|---|---|
| Economic | costs, benefits, financial/market implications, economic consequences. |
| Capacity & resources | availability or lack of physical, human, or institutional resources. |
| Morality | right vs. wrong, religious or ethical duties, moral judgement. |
| Fairness & equality | (in)equality, balance of rights/treatment between groups. |
| Legality, constitutionality, jurisprudence | laws, courts, constitutional questions, legal rights/processes. |
| Policy prescription & evaluation | proposed solutions, whether a policy will / does work. |
| Crime & punishment | crimes, offenders, sanctions, enforcement, punishment. |
| Security & defense | threats, safety, military/defence, protection from danger. |
| Health & safety | health, disease, sanitation, public-health safety. |
| Quality of life | wellbeing, daily life, happiness, standard of living. |
| Cultural identity | traditions, customs, social norms, group identity. |
| Public opinion | what the public thinks; polls, attitudes, social-media mood. |
| Political | politics, parties, elections, lobbying, political manoeuvring. |
| External regulation & reputation | a country's/actor's standing abroad; foreign relations, treaties, image. |

### The 14 frames — details

**Economic**
- Definition. The costs, benefits, or other financial/monetary implications of the issue — for individuals, groups, institutions, regions, or the economy as a whole.
- Look for. prices, costs, budgets, taxes, sanctions, trade, jobs, GDP, financial gain or loss.
- Positive example. An article on a pension reform that centres on its cost to the state budget and its effect on inflation.
- Negative example. An article that mentions a single budget figure in passing while focusing on whether the reform is constitutional is Legality, not Economic.

**Capacity & resources**
- Definition. The availability of, or lack of, physical, human, financial, or institutional resources — the capacity to carry something out.
- Look for. shortages, supply, manpower, infrastructure, "not enough …," logistical capacity.
- Positive example. An article arguing that hospitals lack the staff and beds to handle a crisis foregrounds Capacity & resources.
- Negative example. An article about hospital funding cuts framed around their cost is Economic; the resource-availability angle must be the focus here.

**Morality**
- Definition. The issue seen in terms of right and wrong, religious or ethical duties, conscience, or moral judgement.
- Look for. moral duty, sin, ethics, "it is wrong/right to …," religious or value-based judgement.
- Positive example. An article condemning a policy as a moral betrayal of the country's duty to the vulnerable foregrounds Morality.
- Negative example. An article calling a policy "unfair to one region" is Fairness & equality (group balance), not Morality, unless framed as an ethical or religious wrong.

**Fairness & equality**
- Definition. The (in)equality or balance with which laws, treatment, resources, or rights are distributed across people or groups.
- Look for. discrimination, equal/unequal treatment, balance of rights, "one group vs another," justice as fairness.
- Positive example. An article arguing that a tax change benefits the rich at the expense of the poor foregrounds Fairness & equality.
- Negative example. An article about whether a tax change is legal is Legality; the unequal-distribution angle must be present here.

**Legality, constitutionality, jurisprudence**
- Definition. The issue seen through laws, courts, constitutional questions, legal rights, or judicial processes.
- Look for. courts, laws, the constitution, rulings, legal rights, jurisdiction, "unconstitutional," "illegal."
- Positive example. An article on whether a decree violates the constitution and may be struck down by the court foregrounds Legality.
- Negative example. An article that a court "will discuss" a case but that focuses on the political fallout is Political, not Legality.

**Policy prescription & evaluation**
- Definition. Discussion of specific policies or solutions proposed to address the issue, and assessment of whether they will or do work.
- Look for. proposed measures, "the solution is …," evaluating whether a policy succeeds or fails, recommendations.
- Positive example. An article weighing whether a new subsidy scheme will actually reduce unemployment foregrounds Policy prescription & evaluation.
- Negative example. An article that merely reports a policy exists, without proposing or evaluating it, does not use this frame.

**Crime & punishment**
- Definition. The issue seen in terms of crimes committed, offenders, law-breaking, enforcement, sanctions, or punishment.
- Look for. crime, arrests, offenders, sentences, prosecution, punishment, law enforcement.
- Positive example. An article centred on the arrest and prosecution of officials for fraud foregrounds Crime & punishment.
- Negative example. An article about whether an action is technically legal, with no offender or punishment, is Legality, not Crime & punishment.

**Security & defense**
- Definition. Threats to the security of individuals, communities, or the nation, and measures of protection or defence against them.
- Look for. threat, danger, attack, military, defence, safety from harm, protection, war.
- Positive example. An article on the threat posed by an enemy advance and the army's defence of a city foregrounds Security & defense.
- Negative example. An article on the army's procurement budget, framed around its cost, is Economic; the threat/protection angle must be present here.

**Health & safety**
- Definition. Health care, disease, sanitation, well-being of the body, and (non-military) public safety.
- Look for. illness, epidemics, hospitals, public health, accidents, safety standards.
- Positive example. An article on the spread of an epidemic and measures to protect public health foregrounds Health & safety.
- Negative example. An article on a military threat is Security & defense, not Health & safety, even though both concern "safety."

**Quality of life**
- Definition. The effect of the issue on people's everyday lives, well-being, happiness, or standard of living.
- Look for. daily life, well-being, living standards, comfort, happiness, ordinary people's experience.
- Positive example. An article describing how rising heating costs make ordinary families' daily lives harder foregrounds Quality of life.
- Negative example. An article giving the macro inflation rate without reference to lived experience is Economic, not Quality of life.

**Cultural identity**
- Definition. Traditions, customs, language, social norms, heritage, or the identity of a group or nation.
- Look for. tradition, heritage, national/ethnic/religious identity, customs, "our culture / values / way of life."
- Positive example. An article defending a tradition as essential to national identity against outside influence foregrounds Cultural identity.
- Negative example. An article about a religious moral duty is Morality; Cultural identity is about belonging and heritage, not right/wrong.

**Public opinion**
- Definition. What the public thinks or feels about the issue: attitudes, polls, social-media mood, demonstrations of opinion.
- Look for. polls, surveys, "the public believes," approval ratings, social-media reaction, popular mood.
- Positive example. An article reporting that polls show most citizens oppose a reform foregrounds Public opinion.
- Negative example. An article in which the author merely asserts a position is not Public opinion unless it reports what the public thinks.

**Political**
- Definition. The issue seen through internal politics: parties, elections, factions, lobbying, political manoeuvring, and the distribution of political power.
- Look for. parties, elections, coalitions, ministers, lobbying, political rivalry, power struggles.
- Positive example. An article on how rival parties manoeuvre over a bill ahead of an election foregrounds Political.
- Negative example. An article on how a vote damages the country's standing with the EU is External regulation & reputation, not Political — though both may apply (see edge cases below).

**External regulation & reputation**
- Definition. A country's or actor's external relations, standing, image, or reputation abroad — including treaties, foreign relations, and international regulation.
- Look for. foreign relations, diplomacy, treaties, sanctions from abroad, international image, reputation, "how the world sees us."
- Positive example. An article on how a decision harms the country's reputation with international partners foregrounds External regulation & reputation.
- Negative example. An article on internal coalition politics with no foreign dimension is Political, not External regulation & reputation.

### Edge cases and close frames

- **Political vs. External regulation & reputation.** Political is an internal political process (parties, elections, manoeuvring). External regulation & reputation is the actor's standing and relations abroad. A parliamentary vote is Political; how that vote damages the country's image with the EU is External regulation & reputation. Both can apply to one article.
- **Economic vs. Quality of life.** Macro figures (inflation, GDP, budgets) are Economic; the same issue told through ordinary people's lived daily experience is Quality of life.
- **Security & defense vs. Health & safety.** Both involve "safety," but Security & defense concerns threat / military / protection from an adversary, while Health & safety concerns disease, accidents, and public health.

### Annotated mini-example

Content: "While ordinary families struggle to pay their heating bills, the so-called reformers in the ministry — long known as puppets of foreign capitals — pushed through a law that experts warn will cripple the economy. Either we reverse course now, or our children inherit ruin. The people have had enough."

- Frames: Economic; Political; Policy prescription & evaluation.
- Why: Heating costs & "cripple the economy" (Economic); ministry/law (Political); a law evaluated as harmful (Policy).
