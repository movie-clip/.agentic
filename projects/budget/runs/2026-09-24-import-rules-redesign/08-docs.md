REPORT 2026-09-24-import-rules-redesign/08
status:      DONE
verdict:     NONE

changed:
  - docs/PROJECT_GUIDE.md — "### 2) Rule Management" rewritten: single list, per-row description edit + category dropdown + Save, Apply All (with count), Refresh Queue, paging kept, modified-row highlight, and in-list-vs-import-triggered refresh edit-preservation rule
  - docs/RELEASE_NOTES.md — appended a new 2026-09-25 entry describing the redesign (single implementation, batch use case deleted, Domain stripper/catalog extraction, edit-preservation change, cosmetic polish); no prior entry content touched
  - docs/TECHNICAL_DESIGN.md — not changed; grepped for CreateCategorizationRulesBatch/RulesQueue/PotentialRule/rules-queue wording and none exist in this file, so there was nothing to reconcile

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order verification is NONE (prose-only); I read PotentialRulesViewModel.cs, PotentialRuleRowViewModel.cs and MainWindow.axaml:421-503 directly (not only prior lane reports) to confirm the D1 refresh-preservation semantics and the D2 highlight/count before describing them in docs

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - 07-integration.md § risks flags that decisions.md records D1/D2 rulings only as literal "option 1" text with no lettered list preserved, so the mapping to 02-design.md's (a)/(b)/(c) options is inferred, not quoted. I read the shipped code directly to resolve this for the docs (see § risks below) rather than trust either report's wording.
  - docs/OPERATIONS.md was not touched — no build/test/run/publish step, pre-release checklist item, or dependency policy changed by this redesign, so it is out of the definition of done and I left it alone.

skill_calls:
  - none

risks:
  - The shipped D1/D2 behavior does not match "option 1" read literally as design's first-listed option (a) in either case: PotentialRulesViewModel.cs confirms RefreshCommand/SaveRowAsync/ApplyAllAsync all call LoadAsync(keepEdits: true) while the public RefreshAsync(content) (import/merge/apply-rules/prefix/restore/load call sites) uses keepEdits: false — i.e. shipped code matches design's recommended option (c) for D1, not (a). MainWindow.axaml:450-463 shows a modified-row border-highlight style and PotentialRulesViewModel.ApplyAllText shows an "Apply All (N)" count — i.e. shipped code matches design's option (b) for D2, not (a). I documented what the code actually does (per this lane's "document what shipped" rule), not the literal "option 1" text in decisions.md; if the human's "option 1" ruling was meant to select design's (a) options, docs.md now describes behavior that disagrees with that ruling and the human should re-check decisions.md D-1/D-2 against 07-integration.md § risks.
  - docs/TECHNICAL_DESIGN.md has no existing section describing the Potential Rules / rules-queue feature at all (grepped for Potential, "Preview...Rules", "rules queue", "potential rule" — zero matches), so there was no stale batch-use-case or old-shape reference to remove; I did not add a new architecture section for the feature since the order's definition of done only asks to check for and remove stale mentions, not to author new coverage, and adding one would exceed this order's scope.
