REPORT 2026-09-23-import-review/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order verification field was NONE (read-only recon)

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - No multi-file import path exists anywhere in the code (`AllowMultiple = false` on both file pickers) — see § Root cause — potential-rules list, Finding 1.
  - Real bug found: paging the "Potential New Rules" list discards unsaved category edits and "Apply All" only ever commits the current page, not all pages — see § Root cause — potential-rules list, Finding 2.
  - The exact UI element in question is the "Potential New Rules" panel, `ImportedRuleTransactions` ItemsControl at `src/HomeCharts.App/MainWindow.axaml:425-447` — see § Import flow map, step 6.
  - Full file:line hop list from file-select to SQLite merge is in § Import flow map, for whichever lane picks up a fix.
  - Every new import replaces the whole potential-rules queue in place rather than accumulating across files — see § Root cause — potential-rules list, Finding 1.

risks:
  - Order's "two pages/files" framing is unconfirmed as literally "2"; the two mechanisms found (queue replaced per-import vs. page-scoped edit loss) both explain the symptom class but neither is a hardcoded cap of 2 — see § Risks / open questions.
  - No `tests/HomeCharts.Presentation` project exists in this repo, so there is no automated coverage of `MainWindowViewModel` paging/queue behavior to cross-check against — see § Risks / open questions.

## Orchestrator brief
- No multi-file import exists in the code as shipped: both file pickers hard-code `AllowMultiple = false` (`src/HomeCharts.App/MainWindow.axaml.cs:87,118`), `ImportFilePath` is a single string, and every import/preview use case takes one `fileContent` string. The "multiple files in one import" premise does not match any implemented flow.
- The user-visible symptom is real but has a different, page-based root cause: the "Potential New Rules" list (`ImportedRuleTransactions`, bound in `MainWindow.axaml:447`) silently **discards unsaved category edits whenever the user pages Prev/Next**, and "Apply All" only ever commits the **currently displayed page**, not all pages — see § Root cause — potential-rules list.
- Every new import (or Refresh Queue) also **wipes the previous file's whole queue** — no accumulation across sequential single-file imports — see § Root cause — potential-rules list, Finding 1.
- Risks: order's "two pages/files" framing is unconfirmed as literally "2"; the mechanism found explains data loss at *any* page boundary or *any* subsequent import, not a hardcoded cap of 2. Flagged in `risks` above.
- Sections below, in order: § Import flow map (file:line), § Root cause — potential-rules list, § Other flow observations (incidental, not fixed), § Docs checked, § Risks / open questions.

## Import flow map (file:line)

1. **File selection (UI)** — `src/HomeCharts.App/MainWindow.axaml.cs`
   - `OnBrowseImportFileClick` (line 77-106): `StorageProvider.OpenFilePickerAsync` with `AllowMultiple = false` (line 87) → calls `_viewModel.ImportFromSelectedFileAsync(localPath)` (line 104).
   - `OnBrowseTransactionsFileClick` (line 108-134): same pattern, `AllowMultiple = false` (line 118), feeds the separate Transactions-tab preview flow.
2. **View model entry points** — `src/HomeCharts.Presentation/Mvp/MainWindowViewModel.cs`
   - `ImportFromSelectedFileAsync(filePath)` (553-557) sets `ImportFilePath` then calls `ImportAsync()`.
   - `ImportAsync()` (565-629): reads file content (578), calls `_importBankStatementUseCase.ExecuteAsync(sourceName, content)` (589 → `HomeCharts.Application/UseCases/ImportBankStatementUseCase.cs`), then `_applyCategorizationRulesUseCase.ExecuteAsync(...)` (618), then refreshes dashboard/rules-queue/category-expense previews (620-622), each re-parsing the **same single file content** already in memory (not re-reading other files).
   - Parallel Transactions-tab path: `PreviewMatchedTransactionsAsync()` (631-690) → `_previewMatchedTransactionsUseCase` → `MergeMatchedTransactionsAsync()` (692+) → `MergeMatchedTransactionsUseCase` (Application layer) merges the staged single file's matched rows into SQLite.
3. **Parsing** — `src/HomeCharts.Application/Import/BankStatementParser.cs` — parses one `fileContent` string into `parse.Rows`/`Errors`/`Warnings`. No file-list parameter anywhere in this type's surface (confirmed via grep of Application layer).
4. **Potential-rules preview (the list in question)** — `src/HomeCharts.Application/UseCases/PreviewPotentialRulesUseCase.cs`
   - `ExecuteAsync(fileContent, ct)` (14-42): parses the given content (18), loads active rules (24), for every unmatched row (via `CategorizationEngine.Match`, Domain layer) builds a `PotentialRuleRow` (33-38). Returns `PreviewPotentialRulesResult` with **all** unmatched rows from that one file — no truncation inside the use case itself.
5. **VM consumption / paging** — `MainWindowViewModel.cs`
   - `RefreshRulesQueueAsync(fileContent)` (1274-1313): calls the use case (1295), then `_rulesQueueRows.Clear(); _rulesQueueRows.AddRange(preview.PotentialRows);` (1307-1308) — **replaces** the backing list wholesale every time it's called (called after every import, prefix-filter change, and `SaveAllPotentialRulesAsync`).
   - `RefreshRulesQueuePage()` (1337-1375): computes `totalPages` from `_rulesQueueRows.Count` and `RulesQueuePageSize = 120` (105), does `_rulesQueueRows.Skip(skip).Take(RulesQueuePageSize)` (1356-1358) into the **UI-bound** `ImportedRuleTransactions` collection — starting with `ImportedRuleTransactions.Clear()` (1339).
   - `MoveNextRulesQueuePage()` / `MovePreviousRulesQueuePage()` (1315-1335) just bump `_rulesQueueCurrentPage` and call `RefreshRulesQueuePage()` again.
6. **UI binding** — `src/HomeCharts.App/MainWindow.axaml:422-479` — "Potential New Rules" panel (line 425), `ItemsControl` bound to `ImportedRuleTransactions` (447), Prev/Next buttons (429-430) bound to `PreviousRulesQueuePageCommand`/`NextRulesQueuePageCommand`, "Apply All" (427) bound to `SaveAllPotentialRulesCommand`.
7. **Apply/save** — `MainWindowViewModel.cs:874-894` `SaveAllPotentialRulesAsync()` — reads `ImportedRuleTransactions.Where(row => row.IsModified && ...)` (878-881) and calls `_createCategorizationRulesBatchUseCase.ExecuteAsync(modifiedRows)` (889 → `HomeCharts.Application/UseCases/CreateCategorizationRulesBatchUseCase.cs`).

## Root cause — potential-rules list

**Identified UI element:** "Potential New Rules" panel, `ImportedRuleTransactions` ItemsControl, `src/HomeCharts.App/MainWindow.axaml:425-447`, backed by `MainWindowViewModel._rulesQueueRows` (line 103) and page-materialized into the bound `ImportedRuleTransactions` collection by `RefreshRulesQueuePage()` (`MainWindowViewModel.cs:1337-1375`).

**Finding 1 — no multi-file import exists to reproduce "spans more than two files."**
- `AllowMultiple = false` at `src/HomeCharts.App/MainWindow.axaml.cs:87` and `:118` — the file picker used by both the Import tab and the Transactions tab physically cannot select more than one file.
- `ImportFilePath` (`MainWindowViewModel.cs:255`) is a single `string`, not a collection, and every use case in the flow (`ImportBankStatementUseCase`, `PreviewPotentialRulesUseCase`, `PreviewMatchedTransactionsUseCase`, `PreviewParsedCategoryExpensesUseCase`) takes one `fileContent` parameter.
- `docs/PROJECT_GUIDE.md:20-23` documents the flow as "Select a bank statement `.txt` file" (singular) — matches the code.
- Consequence: each import is single-file, and `RefreshRulesQueueAsync` **replaces** `_rulesQueueRows` in full on every call (`MainWindowViewModel.cs:1307-1308`) — so importing file A, then file B, shows **only file B's** potential rules afterward. Nothing accumulates across sequential imports; there is no bug here relative to a spec, because no spec claims cross-file accumulation, but this is the closest literal match to "doesn't show all files" if the user imported file A, reviewed it, then imported file B expecting the queue to grow.

**Finding 2 — real, concrete bug: unsaved edits and "Apply All" are scoped to the currently displayed page only, not all pages.**
- `RefreshRulesQueuePage()` starts with `ImportedRuleTransactions.Clear()` (`MainWindowViewModel.cs:1339`) every time the page changes (Prev/Next, `MainWindowViewModel.cs:1315-1335`) or the queue refreshes.
- The per-row edit state (`SelectedCategory`, `IsModified`) lives only on `EditableRulesImportedTransactionViewModel` instances (`src/HomeCharts.Presentation/Mvp/TransactionsModels.cs:52-96`), freshly constructed each time `RefreshRulesQueuePage` runs (`MainWindowViewModel.cs:1362-1370`) from the raw `PotentialRuleRow` data in `_rulesQueueRows` — which itself carries **no** edit state.
- Result: if a user sets categories on page 1 of a >120-row potential-rules queue (`RulesQueuePageSize = 120`, `MainWindowViewModel.cs:105`) and pages to page 2 before clicking "Apply All", page 1's selections are silently lost — the objects holding them were discarded at line 1339 and are not reconstructed from any persisted source.
- `SaveAllPotentialRulesAsync()` (`MainWindowViewModel.cs:874-894`) only enumerates the live `ImportedRuleTransactions` collection (878) — i.e. whatever page is on screen at the moment "Apply All" is clicked — never `_rulesQueueRows` in full. So even without navigating away, "Apply All" cannot ever cover more than one page's worth of rows in a single click.
- This matches the reported symptom ("list only shows/processes results from [a limited subset] instead of all available") more precisely than a file-count cap: the ceiling is **per page**, not per file, and it manifests as soon as the potential-rules count exceeds `RulesQueuePageSize` (120) for a single large file — no multi-file import is even required to trigger it.

**What was ruled out:** the paging arithmetic itself is correct — `totalPages = Math.Ceiling(_rulesQueueTotalMatchedCount / (double)RulesQueuePageSize)` (`MainWindowViewModel.cs:1349`) and `CanMoveNextRulesQueuePage()` (`1611-1618`) both scale with the true row count; there is no hardcoded `2` anywhere in the paging path. Grepped for `Take(2)`/`Skip(2)`/literal index bounds in `MainWindowViewModel.cs` — none found relevant to this list.

## Other flow observations (incidental, not fixed)

- `ImportAsync()` (`MainWindowViewModel.cs:565-629`) calls `RefreshRulesQueueAsync(content)` and `RefreshParsedCategoryExpensesAsync(content)` even on the **duplicate-import** path (lines 599-600) — reasonable (keeps preview in sync), noted only because it means a duplicate re-import of the same file also wipes any queue built from a *different* file that was open before it, reinforcing Finding 1's "single active file" scoping.
- `SaveAllPotentialRulesAsync()` calls `RefreshRulesQueueAsync()` with no `fileContent` argument (890) — this falls back to re-reading `ImportFilePath` from disk (`RefreshRulesQueueAsync`, lines 1278-1286), which is correct only as long as `ImportFilePath` still points at the file whose rules were just being reviewed; there is no guard against the user having changed `ImportFilePath` in the interim (e.g., via the Transactions tab's separate browse button), though no evidence was found that this cross-contaminates in the current UI wiring — flagged as a risk, not a confirmed bug.
- Override-preservation and rule-precedence logic (guardrails 1-2) were not implicated by anything found in this trace — `CategorizationEngine.Match` (Domain layer) is invoked once per row via `PreviewPotentialRulesUseCase.cs:30` and its result is not cached or reused in a way that looked nondeterministic.

## Docs checked

- `docs/PROJECT_GUIDE.md:16-40` — "Primary User Flows" § Import and Categorize, § Rule Management: describes single-file selection and a pageable potential-rules list; does not describe multi-file import or cross-page persistence of edits. Looks current relative to the code traced.
- `docs/TECHNICAL_DESIGN.md` — not read in this pass (not needed to answer the specific question; the use-case and view-model code was authoritative and matched `PROJECT_GUIDE.md`).

## Risks / open questions

- Could not confirm the user's exact repro steps ("multiple files involved in an import") against any code path, because no such path exists. If the user is in fact dragging/selecting one file, reviewing partial results, then re-selecting another file, Finding 1 (queue replacement) is the exact mechanism; if the user is working a single large file with a queue that pages, Finding 2 (page-scoped edit loss / Apply-All-per-page) is the exact mechanism. Recommend confirming which with the user before scoping a fix — this recon cannot distinguish them further from code alone.
- Did not check `tests/HomeCharts.Presentation` — there is no such test project in `CLAUDE.md`'s listed layout (only Domain/Application/Infrastructure test projects exist), so there is no existing automated coverage of `MainWindowViewModel` paging/queue behavior to cross-check against.
