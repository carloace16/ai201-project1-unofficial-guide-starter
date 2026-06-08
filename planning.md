# Project 1 Planning: The Unofficial Guide

## Domain

Shonen Manga and Anime Catch-Up Guides. This knowledge is valuable because official streaming sites do not tell you which episodes are non-canon filler, which chapters pick up exactly where an anime season ends, or which fan-edits improve the pacing. This is highly specific, community-driven knowledge.

## Documents

| #   | Source  | Description                      | URL or location                       |
| --- | ------- | -------------------------------- | ------------------------------------- |
| 1   | Reddit  | Skypiea arc skip advice          | `docs/reddit_onepiece_skypiea.txt`    |
| 2   | Discord | One Pace Dressrosa guide         | `docs/discord_one_pace_guide.txt`     |
| 3   | Guide   | One Punch Man manga transition   | `docs/opm_reading_guide.txt`          |
| 4   | Guide   | Boruto canon filler guide        | `docs/boruto_filler_guide.txt`        |
| 5   | Reddit  | Two Blue Vortex starting chapter | `docs/reddit_two_blue_vortex.txt`     |
| 6   | Guide   | Bleach TYBW prep and filler      | `docs/bleach_tybw_prep.txt`           |
| 7   | Guide   | Jujutsu Kaisen manga transition  | `docs/jjk_manga_transition.txt`       |
| 8   | Guide   | Demon Slayer Hashira training    | `docs/ds_hashira_training_review.txt` |
| 9   | Guide   | MHA Season 6 manga transition    | `docs/mha_season6_manga.txt`          |
| 10  | Guide   | Anime tracking and watch history | `docs/anime_tracking_advice.txt`      |

## Chunking Strategy

**Chunk size:** 250 characters
**Overlap:** 50 characters
**Reasoning:** Since these are short, highly concentrated forum posts and Discord messages rather than long-form articles, a smaller chunk size ensures the embedding model captures specific advice (like exact chapter numbers) without diluting it with unrelated shows. The 50-character overlap prevents cutting crucial chapter numbers or episode ranges in half.

## Retrieval Approach

**Embedding model:** `all-MiniLM-L6-v2` (via sentence-transformers)
**Top-k:** 3 chunks
**Production tradeoff reflection:** If deploying for real users without cost limits, I would likely upgrade to an OpenAI embedding model (`text-embedding-3-small` or `large`). While `all-MiniLM` is fast and free locally, a commercial model has better multilingual support (useful for anime titles in romaji/Japanese) and a larger context window for parsing longer, complex Reddit theories.

## Evaluation Plan

| #   | Question                                                                                  | Expected answer                                                                                                            |
| --- | ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| 1   | Should I skip the Skypiea arc in One Piece?                                               | No, do not skip it. It holds important lore drops for the endgame. You can read the manga if the anime pacing is too slow. |
| 2   | Which Boruto episodes are actually canon from the manga?                                  | Watch the Momoshiki Arc (51-66), Mujina Bandits (148-151), Vessel/Kara arcs (181-220), and Code arc (287-293).             |
| 3   | I just finished Jujutsu Kaisen Season 2. Where do I start the manga?                      | Start exactly at Chapter 137.                                                                                              |
| 4   | Do I need to watch the Bount Arc before Bleach TYBW?                                      | No, you do not need to watch the Bount Arc or other filler arcs, but you should watch a recap of the Fullbringer Arc.      |
| 5   | I finished Season 2 of One Punch Man anime. Should I read the webcomic or the manga next? | Start reading the Murata manga at Chapter 85. Ignore the webcomic unless you want major spoilers.                          |

## Anticipated Challenges

1. **Number Confusion:** The documents are packed with numbers (Chapter 85, Episode 51-66, Season 2, 102 chapters). The retrieval system might get confused and pull numbers from the wrong anime if the query isn't specific enough.
2. **Short Chunk Dilution:** Because the chunk size is small, if an anime name is mentioned at the start of a document but the chapter numbers are at the end, the chunk with the chapter numbers might not contain the anime's name, causing the system to miss it.

## Architecture

Document Ingestion (Python `os`) → Chunking (Python string slicing) → Embedding + Vector Store (ChromaDB + `all-MiniLM-L6-v2`) → Retrieval (Chroma DB `query`) → Generation (Groq API: `llama-3.3-70b-versatile`)

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:** I will use the AI to help me write the script to iterate through the `docs` folder, open the `.txt` files, and apply the 250/50 sliding window character chunking strategy.
**Milestone 4 — Embedding and retrieval:** I will use the AI to set up the ChromaDB local client, initialize the sentence-transformer model, insert the chunks with their metadata, and write the query function.
**Milestone 5 — Generation and interface:** I will use the AI to format the Gradio UI skeleton provided in the spec and write the Groq API call with a strict system prompt to enforce grounded answers.
