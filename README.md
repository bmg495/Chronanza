# Chronanza

A timeline-based trivia and ordering puzzle game where players arrange historical events, pop culture milestones, inventions, and cultural moments in chronological order.

## How to Play

1. **Pick a Topic & Subcategory:** Choose from **15** broad topics—such as *World History*, *Themed History*, *Crime & Law*, *Business & Brands*, *Nature & Animals*, *Food*, *Art & Architecture*, *Technology*, *Sports*, *Music*, *Literature*, *Movies*, *Television*, *Pop Culture*, and *Toys & Videogames*—and dive into specific subcategories (e.g., *Famous battles*, *space journeys*, *court cases*, *Snacks*, *Consoles*)[cite: 3].
2. **Order the Tiles:** Each puzzle presents a set of event tiles (such as 9-tile sets in the `Puzzles` and `Database` sheets) featuring a **Tile Name** and a short **Fact** clue[cite: 1, 3, 4]. Arrange the tiles from earliest to latest by **Year** (supporting BCE/negative years like `-2560` through modern years up to `2022`)[cite: 3, 4].
3. **Lock In & Learn:** Check your chronological sequence to score and reveal the exact years and historical/cultural facts behind each tile[cite: 1, 3, 4].

## Content & Data Structure

The game content is structured across three sheets in `Chronanza.xlsx`:

* **Topics:** Maps out **15** top-level topics and **159** planned subcategories[cite: 3].
* **Puzzles:** Contains curated puzzle sets (such as a 9-tile *Video Games* puzzle from *Pong* in `1972` to *Nintendo Switch* in `2017`) with `ID Number`, `Tile Name`, `Year`, and `Fact`[cite: 1].
* **Database:** Stores **306** tile records across populated subcategories spanning years `-2560` to `2022`, each with:
  * `id` (e.g., `WH-FB-001`, `TVG-CN-001`)[cite: 1, 4]
  * `topic` and `subcategory`[cite: 4]
  * `tileName`[cite: 4]
  * `year` (integer; negative values represent BCE)[cite: 3, 4]
  * `fact`[cite: 4]
