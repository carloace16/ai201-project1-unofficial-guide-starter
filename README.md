# The Unofficial Guide — Project 1

## Domain

**Shonen Manga and Anime Catch-Up Guides.** This knowledge is highly valuable because official streaming sites do not tell you which episodes are non-canon filler, which chapters pick up exactly where an anime season ends, or which fan-edits improve the pacing. This is highly specific, community-driven knowledge that is otherwise fragmented across Reddit, Discord, and forums.

---

## Document Sources

| #   | Source                           | Type    | URL or file path                      |
| --- | -------------------------------- | ------- | ------------------------------------- |
| 1   | Skypiea arc skip advice          | Reddit  | `docs/reddit_onepiece_skypiea.txt`    |
| 2   | One Pace Dressrosa guide         | Discord | `docs/discord_one_pace_guide.txt`     |
| 3   | One Punch Man manga transition   | Guide   | `docs/opm_reading_guide.txt`          |
| 4   | Boruto canon filler guide        | Guide   | `docs/boruto_filler_guide.txt`        |
| 5   | Two Blue Vortex starting chapter | Reddit  | `docs/reddit_two_blue_vortex.txt`     |
| 6   | Bleach TYBW prep and filler      | Guide   | `docs/bleach_tybw_prep.txt`           |
| 7   | Jujutsu Kaisen manga transition  | Guide   | `docs/jjk_manga_transition.txt`       |
| 8   | Demon Slayer Hashira training    | Guide   | `docs/ds_hashira_training_review.txt` |
| 9   | MHA Season 6 manga transition    | Guide   | `docs/mha_season6_manga.txt`          |
| 10  | Anime tracking and watch history | Guide   | `docs/anime_tracking_advice.txt`      |

---

## Chunking Strategy

**Chunk size:** 250 characters
**Overlap:** 50 characters

**Why these choices fit your documents:** Since these documents are short, highly concentrated forum posts and Discord messages rather than long-form articles, a smaller chunk size ensures the embedding model captures specific advice (like exact chapter numbers) without diluting it with unrelated shows. The 50-character overlap prevents cutting crucial chapter numbers or episode ranges in half.

**Final chunk count:** 21 chunks

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` (via sentence-transformers)

**Production tradeoff reflection:** If I were deploying this system for real users without cost limits, I would weigh upgrading to a commercial model like OpenAI's `text-embedding-3-small`. While `all-MiniLM` is fast and runs locally, a commercial model offers a much larger context window and better multilingual support, which is critical for parsing anime titles written in romaji or Japanese characters.

---

## Grounded Generation

**System prompt grounding instruction:**
I passed the following strict instruction to the Groq API: _"You are an expert Anime and Manga Guide. Answer the user's question using ONLY the provided text below. If the answer is not in the text, say 'I don't have enough information on that.' Do not use outside knowledge or guess."_

**How source attribution is surfaced in the response:**
I programmatically loop through the `results` returned by ChromaDB, extract the `source` metadata from each chunk, filter out duplicates using a Python `set()`, and format them into a bulleted list. The Gradio UI displays this list in a dedicated "Sources Used" textbox separate from the LLM's generated answer.

---

## Evaluation Report

| #   | Question                                                                                  | Expected answer                                                              | System response (summarized)                                                                     | Retrieval quality  | Response accuracy |
| --- | ----------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ------------------ | ----------------- |
| 1   | Should I skip the Skypiea arc in One Piece?                                               | No, do not skip it. It holds important lore drops.                           | Do not skip Skypiea; recent chapters prove it holds important lore drops for the endgame.        | Relevant           | Accurate          |
| 2   | Which Boruto episodes are actually canon from the manga?                                  | Watch the Momoshiki Arc (51-66), Mujina Bandits, Vessel/Kara, and Code arcs. | I don't have enough information on that.                                                         | Partially relevant | Inaccurate        |
| 3   | I just finished Jujutsu Kaisen Season 2. Where do I start the manga?                      | Start exactly at Chapter 137.                                                | Start reading the manga exactly at Chapter 137.                                                  | Relevant           | Accurate          |
| 4   | Do I need to watch the Bount Arc before Bleach TYBW?                                      | No, but watch a recap of the Fullbringer Arc.                                | No, you do not need to watch the Bount Arc, but you should watch a recap of the Fullbringer Arc. | Relevant           | Accurate          |
| 5   | I finished Season 2 of One Punch Man anime. Should I read the webcomic or the manga next? | Read the manga at Chapter 85. Ignore the webcomic.                           | Start reading the Murata manga at Chapter 85 and ignore the webcomic.                            | Relevant           | Accurate          |

**Retrieval quality:** (See table above)
**Response accuracy:** (See table above)

---

## Failure Case Analysis

**Question that failed:** Which Boruto episodes are actually canon from the manga?

**What the system returned:** "I don't have enough information on that. The text only mentions that the Boruto anime has 'anime canon' episodes that aren't in the manga, but it doesn't specify which episodes are actually canon."

**Root cause (tied to a specific pipeline stage):** This was a failure at the **Chunking and Retrieval** stage. Because my chunk size was strictly 250 characters, the document `boruto_filler_guide.txt` was split across a boundary. Chunk A contained the keywords "Boruto", "canon", and "manga", so the retriever pulled it. However, the actual episode numbers (e.g., Ep 51-66) were pushed into Chunk B. Because the retriever didn't pull Chunk B, the generator followed its strict grounding prompt and correctly stated that it didn't have the information in its provided context.

**What you would change to fix it:** I would increase the chunk size to roughly 400 characters so that the definition of the filler episodes and the actual list of episode numbers are kept together in a single semantic vector.

---

## Spec Reflection

**One way the spec helped you during implementation:**
Writing the spec first helped me realize that my documents were incredibly short and dense. By establishing the 250-character chunk size in the spec, I was able to write my `ingest.py` sliding window algorithm correctly the first time without having to blindly guess numbers.

**One way your implementation diverged from the spec, and why:**
My implementation diverged slightly in the retrieval stage. Because of local Windows and ChromaDB formatting quirks, the database returned distance numbers wrapped in triple-nested lists (e.g., `[[[0.22]]]`). I had to diverge from a standard query extraction and write "bulletproof" dictionary fallback checks to safely extract the text and sources without crashing the pipeline.

---

## AI Usage

**Instance 1**

- _What I gave the AI:_ I provided the chunking strategy and pipeline diagram from my `planning.md` and asked it to generate the `retriever.py` database connection.
- _What it produced:_ It produced standard ChromaDB query extraction code, but the code crashed on my Windows machine due to unexpected array nesting. It then generated complex `while` loops to try and unwrap the arrays.
- _What I changed or overrode:_ I overrode the complex `while` loop approach entirely. Instead, I stripped out the strict float formatting (`:.4f`) and implemented flat, direct list indexing (`docs`) combined with safe `.get()` dictionary fallbacks to ensure the pipeline stayed stable regardless of how ChromaDB formatted the output.

**Instance 2**

- _What I gave the AI:_ I provided the 10 text documents and asked it to help me formulate 5 evaluation test questions for my `planning.md` file.
- _What it produced:_ It generated 5 questions, but pointed out that the Boruto question would likely act as a "trap" for the retrieval system.
- _What I changed or overrode:_ I deliberately kept the Boruto question exactly as generated to force a failure case, which allowed me to properly evaluate the system's strict grounding limitations when semantic chunks get severed.# The Unofficial Guide — Project 1

## Domain

**Shonen Manga and Anime Catch-Up Guides.** This knowledge is highly valuable because official streaming sites do not tell you which episodes are non-canon filler, which chapters pick up exactly where an anime season ends, or which fan-edits improve the pacing. This is highly specific, community-driven knowledge that is otherwise fragmented across Reddit, Discord, and forums.

---

## Document Sources

| #   | Source                           | Type    | URL or file path                      |
| --- | -------------------------------- | ------- | ------------------------------------- |
| 1   | Skypiea arc skip advice          | Reddit  | `docs/reddit_onepiece_skypiea.txt`    |
| 2   | One Pace Dressrosa guide         | Discord | `docs/discord_one_pace_guide.txt`     |
| 3   | One Punch Man manga transition   | Guide   | `docs/opm_reading_guide.txt`          |
| 4   | Boruto canon filler guide        | Guide   | `docs/boruto_filler_guide.txt`        |
| 5   | Two Blue Vortex starting chapter | Reddit  | `docs/reddit_two_blue_vortex.txt`     |
| 6   | Bleach TYBW prep and filler      | Guide   | `docs/bleach_tybw_prep.txt`           |
| 7   | Jujutsu Kaisen manga transition  | Guide   | `docs/jjk_manga_transition.txt`       |
| 8   | Demon Slayer Hashira training    | Guide   | `docs/ds_hashira_training_review.txt` |
| 9   | MHA Season 6 manga transition    | Guide   | `docs/mha_season6_manga.txt`          |
| 10  | Anime tracking and watch history | Guide   | `docs/anime_tracking_advice.txt`      |

---

## Chunking Strategy

**Chunk size:** 250 characters
**Overlap:** 50 characters

**Why these choices fit your documents:** Since these documents are short, highly concentrated forum posts and Discord messages rather than long-form articles, a smaller chunk size ensures the embedding model captures specific advice (like exact chapter numbers) without diluting it with unrelated shows. The 50-character overlap prevents cutting crucial chapter numbers or episode ranges in half.

**Final chunk count:** 21 chunks

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` (via sentence-transformers)

**Production tradeoff reflection:** If I were deploying this system for real users without cost limits, I would weigh upgrading to a commercial model like OpenAI's `text-embedding-3-small`. While `all-MiniLM` is fast and runs locally, a commercial model offers a much larger context window and better multilingual support, which is critical for parsing anime titles written in romaji or Japanese characters.

---

## Grounded Generation

**System prompt grounding instruction:**
I passed the following strict instruction to the Groq API: _"You are an expert Anime and Manga Guide. Answer the user's question using ONLY the provided text below. If the answer is not in the text, say 'I don't have enough information on that.' Do not use outside knowledge or guess."_

**How source attribution is surfaced in the response:**
I programmatically loop through the `results` returned by ChromaDB, extract the `source` metadata from each chunk, filter out duplicates using a Python `set()`, and format them into a bulleted list. The Gradio UI displays this list in a dedicated "Sources Used" textbox separate from the LLM's generated answer.

---

## Evaluation Report

| #   | Question                                                                                  | Expected answer                                                              | System response (summarized)                                                                     | Retrieval quality  | Response accuracy |
| --- | ----------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ------------------ | ----------------- |
| 1   | Should I skip the Skypiea arc in One Piece?                                               | No, do not skip it. It holds important lore drops.                           | Do not skip Skypiea; recent chapters prove it holds important lore drops for the endgame.        | Relevant           | Accurate          |
| 2   | Which Boruto episodes are actually canon from the manga?                                  | Watch the Momoshiki Arc (51-66), Mujina Bandits, Vessel/Kara, and Code arcs. | I don't have enough information on that.                                                         | Partially relevant | Inaccurate        |
| 3   | I just finished Jujutsu Kaisen Season 2. Where do I start the manga?                      | Start exactly at Chapter 137.                                                | Start reading the manga exactly at Chapter 137.                                                  | Relevant           | Accurate          |
| 4   | Do I need to watch the Bount Arc before Bleach TYBW?                                      | No, but watch a recap of the Fullbringer Arc.                                | No, you do not need to watch the Bount Arc, but you should watch a recap of the Fullbringer Arc. | Relevant           | Accurate          |
| 5   | I finished Season 2 of One Punch Man anime. Should I read the webcomic or the manga next? | Read the manga at Chapter 85. Ignore the webcomic.                           | Start reading the Murata manga at Chapter 85 and ignore the webcomic.                            | Relevant           | Accurate          |

**Retrieval quality:** (See table above)
**Response accuracy:** (See table above)

---

## Failure Case Analysis

**Question that failed:** Which Boruto episodes are actually canon from the manga?

**What the system returned:** "I don't have enough information on that. The text only mentions that the Boruto anime has 'anime canon' episodes that aren't in the manga, but it doesn't specify which episodes are actually canon."

**Root cause (tied to a specific pipeline stage):** This was a failure at the **Chunking and Retrieval** stage. Because my chunk size was strictly 250 characters, the document `boruto_filler_guide.txt` was split across a boundary. Chunk A contained the keywords "Boruto", "canon", and "manga", so the retriever pulled it. However, the actual episode numbers (e.g., Ep 51-66) were pushed into Chunk B. Because the retriever didn't pull Chunk B, the generator followed its strict grounding prompt and correctly stated that it didn't have the information in its provided context.

**What you would change to fix it:** I would increase the chunk size to roughly 400 characters so that the definition of the filler episodes and the actual list of episode numbers are kept together in a single semantic vector.

---

## Spec Reflection

**One way the spec helped you during implementation:**
Writing the spec first helped me realize that my documents were incredibly short and dense. By establishing the 250-character chunk size in the spec, I was able to write my `ingest.py` sliding window algorithm correctly the first time without having to blindly guess numbers.

**One way your implementation diverged from the spec, and why:**
My implementation diverged slightly in the retrieval stage. Because of local Windows and ChromaDB formatting quirks, the database returned distance numbers wrapped in triple-nested lists (e.g., `[[[0.22]]]`). I had to diverge from a standard query extraction and write "bulletproof" dictionary fallback checks to safely extract the text and sources without crashing the pipeline.

---

## AI Usage

**Instance 1**

- _What I gave the AI:_ I provided the chunking strategy and pipeline diagram from my `planning.md` and asked it to generate the `retriever.py` database connection.
- _What it produced:_ It produced standard ChromaDB query extraction code, but the code crashed on my Windows machine due to unexpected array nesting. It then generated complex `while` loops to try and unwrap the arrays.
- _What I changed or overrode:_ I overrode the complex `while` loop approach entirely. Instead, I stripped out the strict float formatting (`:.4f`) and implemented flat, direct list indexing (`docs`) combined with safe `.get()` dictionary fallbacks to ensure the pipeline stayed stable regardless of how ChromaDB formatted the output.

**Instance 2**

- _What I gave the AI:_ I provided the 10 text documents and asked it to help me formulate 5 evaluation test questions for my `planning.md` file.
- _What it produced:_ It generated 5 questions, but pointed out that the Boruto question would likely act as a "trap" for the retrieval system.
- _What I changed or overrode:_ I deliberately kept the Boruto question exactly as generated to force a failure case, which allowed me to properly evaluate the system's strict grounding limitations when semantic chunks get severed.
