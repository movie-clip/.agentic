## Orchestrator brief

- Potential New Rules is produced by `PreviewPotentialRulesUseCase.ExecuteAsync` (Application layer) — one `PotentialRuleRow` per *unmatched transaction*, not per unique pattern/description.
- Displayed/paged by `PotentialRulesViewModel` (Presentation) via `_allRows`/`Rows`; rows wrapped as `PotentialRuleRowViewModel`.
- No per-suggestion transaction/occurrence count exists anywhere in the pipeline today — see § Frequency data. It would need to be computed, not merely surfaced.
- No sort logic exists anywhere in the current pipeline (Application or Presentation) — see § Current order. Rows appear in raw file parse order.
- "Most repeated expenses first" requires grouping by pattern (e.g. `SuggestedPattern`/normalized description) and counting occurrences — this is a **counting concern**, which belongs in Application per guardrail 3 (no business logic in Presentation/App). Presentation could do the final list sort if given counts, but the counting itself is a decision.
- See § Layers affected and § Contracts impact for the concrete blast radius.
- Sections below: **Use case (producer)**, **View model (display)**, **Frequency data**, **Current order**, **Layers affected**, **Contracts impact**, **Docs**.

## Use case (producer)

- `PreviewPotentialRulesUseCase.ExecuteAsync` — `src/HomeCharts.Application/UseCases/PreviewPotentialRulesUseCase.cs:20-54`. For each parsed row with no rule match, appends one `PotentialRuleRow` (`:42-49`) to a flat `List<PotentialRuleRow>` in parse-row order; no grouping, counting, or ordering step anywhere in the method.
- `PotentialRuleRow` record definition — `src/HomeCharts.Application/UseCases/PreviewPotentialRulesUseCase.cs:81-88`: `RowKey, LineNumber, BookingDate, RawDescription, Amount, SuggestedPattern, SuggestedCategoryId`. No count/frequency field.
- `PreviewPotentialRulesResult` wraps `IReadOnlyList<PotentialRuleRow> PotentialRows` plus parse errors/warnings — `:90-93`.

## View model (display)

- `PotentialRulesViewModel` — `src/HomeCharts.Presentation/Mvp/PotentialRulesViewModel.cs`. `LoadAsync` (`:99-154`) calls the use case, builds `_allRows` (List<PotentialRuleRowViewModel>) by iterating `preview.PotentialRows` **in the order returned** (`:136-148`), with no `.OrderBy`/sort call anywhere in the file.
- `ShowPage()` (`:232-250`) pages `_allRows` via `Skip/Take` in that same insertion order, 120 rows per page (`PageSize` const, `:21`).
- `PotentialRuleRowViewModel` — `src/HomeCharts.Presentation/Mvp/PotentialRuleRowViewModel.cs` — per-row wrapper (description, category, save command); carries no count/frequency property.
- UI binding entry point: `MainWindow.axaml` and `MainWindowViewModel.cs` wire `PotentialRulesViewModel` into the Import screen (composition in `src/HomeCharts.App/CompositionRoot.cs`); not read line-by-line, not needed for this question.

## Frequency data

- **No per-suggestion transaction count is computed or available anywhere in the current pipeline.** Confirmed by reading `PreviewPotentialRulesUseCase` (Application) and `PotentialRulesViewModel`/`PotentialRuleRowViewModel` (Presentation) in full: each unmatched transaction becomes its own independent row keyed by `RowKey` (line number + date + amount + raw description, `PreviewPotentialRulesUseCase.cs:56-61`), so multiple transactions sharing the same `SuggestedPattern` currently appear as separate, unrelated rows rather than one grouped/counted suggestion.
- To sort "most repeated expenses first," a count of transactions per distinct `SuggestedPattern` (or normalized description) across `parse.Rows`/`potentialRows` would need to be computed — most naturally in `PreviewPotentialRulesUseCase.ExecuteAsync`, since that is where the pattern (`DescriptionPrefixStripper.Strip`, `:48`) and full row set are both already in scope.

## Current order

- No sort order exists today. Order is implicitly "file/parse order" — the sequence `BankStatementParser.Parse` returns (`parse.Rows`, consumed in a plain `foreach` at `PreviewPotentialRulesUseCase.cs:36`), preserved unchanged through `List<PotentialRuleRow>`, through `PotentialRulesViewModel._allRows` construction, through paging.

## Layers affected

- **Application**: counting must originate here (or in a new/extended use case) since it requires aggregating across all parsed rows sharing a pattern, and per guardrail 3 in `budget/CLAUDE.md`/project.md, decisions do not belong in Presentation/App. A per-row count is not currently produced by any layer, so Presentation cannot do a pure view-model sort on existing data.
- **Presentation**: would consume whatever count/order field Application adds (either sort itself once given counts, or simply preserve an order Application already established) and would need a UI affordance if the desired behavior is user-toggleable sort rather than a fixed default order.
- **Contracts**: `PotentialRuleRow` is an Application-layer record, not a `Contracts` interface — no `HomeCharts.Contracts` type currently carries this data, so whether "Contracts" needs a change depends only on whether the count must be sourced from a repository (e.g., historical transaction counts beyond the current import file) versus purely from the current file's parsed rows, which is already fully available to `PreviewPotentialRulesUseCase` without any new repository call.

## Contracts impact

- `PreviewPotentialRulesUseCase` depends on `IRuleRepository`, `ICategoryRepository`, `IPrefixFilterRepository` (all `HomeCharts.Contracts.Persistence`) — none currently expose a count/frequency method, and none appear necessary for an in-file-scope count (the current import file's own `parse.Rows` already contains every occurrence needed to count matches per pattern within that file).
- If "most repeated" is meant to include historical occurrences beyond the currently loaded file (i.e., how often this pattern appeared in past imports), that would require a new repository query and a new `Contracts` method — this recon found no existing interface for that, and whether the intended scope is "within this file" or "across history" is not decidable from the code and is called out below as a risk.

## Docs

- `docs/PROJECT_GUIDE.md:25-39` § "Rule Management" is the canonical description of "Potential New Rules" behavior (single list, per-row Save, Apply All, Refresh Queue, paging) — it documents no sort order today, consistent with the code. This doc would need updating if a sort behavior is added.
- `docs/TECHNICAL_DESIGN.md` was in scope but not found to contain material beyond what's captured above on this specific flow; not separately cited.

REPORT 2026-09-27-sort-potential-rules-by-frequency/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only recon order, verification: NONE

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Counting/grouping logic, if built, most naturally belongs in `PreviewPotentialRulesUseCase.ExecuteAsync` (src/HomeCharts.Application/UseCases/PreviewPotentialRulesUseCase.cs) since it already has the full parsed row set and the `SuggestedPattern` value in scope.
  - `PotentialRuleRow` (src/HomeCharts.Application/UseCases/PreviewPotentialRulesUseCase.cs:81-88) is the record that would carry a new count field if Application computes one.
  - `PotentialRulesViewModel.LoadAsync`/`ShowPage` (src/HomeCharts.Presentation/Mvp/PotentialRulesViewModel.cs:99-154, 232-250) is where any resulting order would need to be preserved through paging rather than re-sorted per page.

skill_calls:
  - none — no skills registered for scout lane in this project's capability pack

risks:
  - Whether "most repeated" should count occurrences only within the currently loaded import file (data already in scope, no Contracts change needed) or across historical imports/transactions (would need a new Contracts repository method) is not decidable from the code alone — this changes the blast radius materially and should be confirmed before design work starts.
  - `docs/TECHNICAL_DESIGN.md` was checked but yielded no additional specifics on this flow beyond `PROJECT_GUIDE.md`; if it has been updated with detail this recon missed, that was not found via targeted search.
