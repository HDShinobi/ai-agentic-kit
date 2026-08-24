// plugins/aak-core/hooks/guard.test.mjs
import { test } from "node:test";
import assert from "node:assert";
import { isDestructive } from "./guard.mjs";

test("blocks destructive commands", () => {
  for (const c of ["rm -rf /","rm -fr /","rm -r -f /","rm -rf /*","sudo rm -rf /",
                    "rm -rf /;echo done","rm -rf / && true","rm -rf \"/\"",   // separators / quotes (M2 false-neg)
                    "mkfs.ext4 /dev/sda","dd if=/dev/zero of=/dev/sda bs=1M",
                    "dd if=x.img of=/dev/rdisk0","dd if=x.img of=/dev/vda", // macOS rdisk + vd (M2 false-neg)
                    "format C:"])
    assert.equal(isDestructive(c), true, `should block: ${c}`);
});
test("allows normal cleanup and mentions", () => {
  for (const c of ["rm -rf dist","rm -rf node_modules","rm -rf ./build","rm file.txt",
                    "npm test","git status","dd if=in.img of=out.img",
                    "echo rm -rf / is dangerous","git commit -m \"revert: rm -rf / guard\"", // rm not at cmd pos (M2 false-pos)
                    "mkfs.ext4 disk.img"])                                                    // loopback image, not /dev (M2 false-pos)
    assert.equal(isDestructive(c), false, `should allow: ${c}`);
});
