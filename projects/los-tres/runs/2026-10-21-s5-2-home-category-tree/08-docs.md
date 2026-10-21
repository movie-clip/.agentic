REPORT 2026-10-21-s5-2-home-category-tree/08
status:      DONE
verdict:     NONE

changed:
  - C:\projects\investments\los-tres\docs\design\system.md — replaced by 01-ux § Design system, CHANGED/NEW markers removed, approval line now cites D-1
  - capabilities/ux.md § Producing the states — `home` row split into `home, populated` and `home, no category has products` (07-ux-review wording: not producible without wiping the demo DB)
  - capabilities/architecture.md § The seams the product forces — Public visibility bullet now names product-page.ts, category-page.ts, category-tree.ts, all calling visibleProductWhere()
  - capabilities/backend.md § Layout — catalogue/ list gains category-tree.ts
  - capabilities/frontend.md § Layout — listing components gain CategoryTree, SiteHeader and CategoryEmpty homeLabel note
  - capabilities/frontend.md § Layout — added the two-class override rule after the `.page p` paragraph
  - capabilities/testing.md § Shared scaffolding and gotchas — insertCategory signature now lists position
  - capabilities/testing.md § Shared scaffolding and gotchas — added the malformed-slug and parent-cycle bullet
  - capabilities/testing.md § Running tests — added the S5.2 home testids and the home count text rule

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order verification was NONE; premises spot-checked against code (category-tree.ts exists and uses visibleProductWhere; insertCategory has position)

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - The 01-ux ux.md entry (down -v recipe) was superseded by 07's and not applied, as ordered.
  - Open item for the human: the S5.2 SHOULD_FIX in 07-ux-review (site name twice above the fold at 390) is for S6.2, not a docs matter.

skill_calls:
  - none

risks:
  - testing.md and frontend.md corrections were applied as given; the insertCategory position option already exists in tests/support/catalogue.ts, consistent with the correction.
  - Other docs/ files were searched for S5.2-stale statements (home, system.md, placeholder); none found, so none edited.
  - Pack indexes unchanged: no section added, removed or renamed.
