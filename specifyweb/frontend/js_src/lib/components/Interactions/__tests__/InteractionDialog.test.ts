/**
 * Regression test for issue #7900:
 * The MissingState block in InteractionDialog.tsx contained a duplicate
 * rendering of the "preparations not found" message. The outer conditional
 * already checked `state.type === 'MissingState'`, but an inner block
 * redundantly checked the same condition and re-rendered `state.missing`,
 * causing the "no records found" message to appear twice.
 *
 * This test reads the source file and verifies that within the MissingState
 * JSX block, `preparationsNotFoundFor` appears exactly once, and there is
 * no redundant nested MissingState check.
 */

import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const sourcePath = resolve(__dirname, '..', 'InteractionDialog.tsx');
const source = readFileSync(sourcePath, 'utf-8');

describe('InteractionDialog MissingState rendering (#7900)', () => {
  test('preparationsNotFoundFor appears exactly once in MissingState block', () => {
    /*
     * Find the MissingState rendering block. It starts with the conditional
     * `{state.type === 'MissingState' && (` and contains the JSX for
     * displaying missing/unavailable preparations.
     *
     * We extract the block following the first occurrence (the rendering
     * section, not the button area) and count how many times
     * `preparationsNotFoundFor` appears within it.
     */
    const lines = source.split('\n');

    // Find the MissingState conditional that starts the results display.
    // This is the block that contains `mt-2 space-y-2` on the next line.
    const blockStartIndex = lines.findIndex(
      (line, index) =>
        line.includes("state.type === 'MissingState'") &&
        lines[index + 1]?.includes('mt-2 space-y-2')
    );
    expect(blockStartIndex).not.toBe(-1);

    // The block ends within ~30 lines; extract it
    const blockLines = lines.slice(blockStartIndex, blockStartIndex + 30);
    const block = blockLines.join('\n');

    const occurrences = (block.match(/preparationsNotFoundFor/g) ?? []).length;
    expect(occurrences).toBe(1);
  });

  test('no redundant nested MissingState check inside the results block', () => {
    const lines = source.split('\n');

    // Find the results-display MissingState block (the one with mt-2)
    const blockStartIndex = lines.findIndex(
      (line, index) =>
        line.includes("state.type === 'MissingState'") &&
        lines[index + 1]?.includes('mt-2 space-y-2')
    );
    expect(blockStartIndex).not.toBe(-1);

    // Count MissingState checks in the 30 lines following that point
    const sectionLines = lines.slice(blockStartIndex, blockStartIndex + 30);
    const checksInSection = sectionLines.filter((line) =>
      line.includes("state.type === 'MissingState'")
    ).length;

    // Should be exactly 1 (the outer check), not 2 (which was the bug)
    expect(checksInSection).toBe(1);
  });
});
