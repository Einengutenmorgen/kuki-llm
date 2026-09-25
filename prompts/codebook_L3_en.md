# KuKi Annotation Codebook v0.3 — Layer 3: Persuasion

## What counts as the article

- Annotate the content as provided.
- Your personal opinion about the frames or the entities is irrelevant and must not influence any label. Annotate how the text frames things, not whether you agree.

**Golden rule.** Label what is in the text, as a careful ordinary reader of that language and culture would understand it; not what you privately know to be true, and not what you suspect the author "really" means without textual support.

## Layer 3 — Persuasion

Adapted from SemEval-2023 Task 3, Subtask 3. The original taxonomy has 23 fine-grained techniques grouped under six coarse categories; we annotate only the six. A span-level, multi-label judgement: which persuasion families does the article use? Many factual reports use none — that is a valid and expected outcome.

### Definition

Persuasion techniques are rhetorical and psychological devices used to influence the reader, including but not limited to logical fallacies and appeals to emotion that support flawed or one-sided argumentation. The source taxonomy contains 23 techniques grouped into six coarse categories; we annotate only the six. It is a multi-label, multi-class task; we are annotating on the span level.

### Decision rules

1. Zero is valid. A neutral factual report may use no persuasion techniques. Do not invent one.
2. Multi-label. Mark every span where a technique occurs; the same category can be marked on several spans, and several categories often co-occur.
3. Mark the span, not the document. Annotate the specific text span(s) that carry the technique; record each occurrence rather than a single document-level flag.
4. Attack on Reputation vs. Manipulative Wording. If charged language targets a specific actor's credibility, prefer Attack on Reputation; if it is general emotional colouring not aimed at discrediting an actor, prefer Manipulative Wording. Both may apply.

### The six categories

**Attack on Reputation**
- Definition. The argument does not address the topic but targets a person, group, organisation, object, or activity in order to question or undermine their credibility. Includes name-calling/labelling, guilt by association, casting doubt on character, charging hypocrisy, and questioning moral standing.
- Look for. insulting labels, smears, "who are they to talk," associating the target with something discrediting, attacking the messenger instead of the message.
- Positive example. Calling an opponent a "puppet of foreign interests" instead of addressing their argument.
- Negative example. Stating that an opponent's economic forecast is wrong and giving counter-figures is a substantive argument, NOT an Attack on Reputation — it addresses the claim, not the person.

**Justification**
- Definition. A statement paired with an appeal that is used to justify or support it: appeal to authority, to popularity ("everyone agrees"), to shared values, to national pride (flag-waving), or to fear/prejudice.
- Look for. "experts say," "everyone knows," "as patriots we must," appeals to fear to push or reject an idea, appeals to cherished values.
- Positive example. "Any true patriot supports this measure" justifies a position by appealing to group pride.
- Negative example. Citing a named study with its actual findings to support a claim is ordinary evidence, NOT appeal-to-authority, unless the authority's mere say-so stands in place of evidence.

**Simplification**
- Definition. The argument excessively simplifies the issue: assigning a single cause where many exist (causal over-simplification), presenting a false either/or with no other options (false dilemma), or claiming one action will inevitably trigger a dramatic chain of consequences (consequential over-simplification).
- Look for. "the sole reason is …," "either we do X or we are doomed," slippery-slope chains.
- Positive example. "If we allow this, the whole country will collapse within a year" is a consequential over-simplification.
- Negative example. Accurately stating that an event had several contributing causes is NOT Simplification — the fallacy requires collapsing real complexity into one cause or two choices.

**Distraction**
- Definition. The argument shifts attention away from the real subject: attacking a distorted version of the opponent's position (strawman), introducing an irrelevant topic (red herring), or deflecting criticism by pointing at the accuser's faults (whataboutism).
- Look for. "but what about …," refuting a claim the opponent never made, changing the subject to dodge the point.
- Positive example. Answering a corruption allegation with "And what about the corruption in their own party?" is whataboutism.
- Negative example. Directly rebutting the opponent's actual argument, even forcefully, is NOT Distraction — the technique requires changing or distorting the subject.

**Call**
- Definition. The text is not an argument but an encouragement to act or to think in a particular way: slogans, conversation-killers that shut down debate, and appeals that the time has come to act.
- Look for. punchy slogans, "there is no alternative," "now is the moment to …," phrases that end discussion.
- Positive example. "The time to act is now — hesitation is betrayal" combines an appeal to time with a conversation-killer.
- Negative example. A neutral sentence reporting that a politician "called for talks" is NOT a Call technique — the article must itself urge the reader to act or think a certain way.

**Manipulative Wording**
- Definition. The text is not an argument per se, but uses specific language — non-neutral, loaded, exaggerated, vague, or repeated — to impact the reader emotionally: loaded language, intentional vagueness/confusion, exaggeration or minimisation, and repetition.
- Look for. emotionally charged word choice, "huge / catastrophic / tiny," deliberately vague phrasing, the same charged phrase repeated for effect.
- Positive example. Describing a policy as a "monstrous, catastrophic betrayal" uses loaded language and exaggeration.
- Negative example. Plain descriptive wording ("the government raised the tax by two percent") is NOT Manipulative Wording, even if the reader happens to dislike the news.

### Annotated mini-example

Content: "While ordinary families struggle to pay their heating bills, the so-called reformers in the ministry — long known as puppets of foreign capitals — pushed through a law that experts warn will cripple the economy. Either we reverse course now, or our children inherit ruin. The people have had enough."

- Persuasion: Attack on Reputation; Justification; Simplification; Call; Manipulative Wording.
- Why: "puppets of foreign capitals" (Attack on Reputation); "experts warn" (Justification); "either… or ruin" (false dilemma = Simplification); "reverse course now" / "had enough" (Call); "cripple," "ruin" (Manipulative Wording).
