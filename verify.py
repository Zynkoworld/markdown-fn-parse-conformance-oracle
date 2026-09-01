#!/usr/bin/env python3
"""verify.py -- CI gate. Futtatja a referencia-implementaciot a kanonikus korpuszon, es exit 0 IFF
minden eset egyezik ES a korpusz nem degeneralt (>=2 kulonbozo kimenet).

A KIMENET FORMATUMA A PUBLISH-KAPU SZERZODESE (compute-oracle osztaly): utolso sor "ZOLD", es a
kimenetben nem szerepelhet a "mismatch"/"serult" szo -- ezert az elteres neve itt `disagree`.
Szandekosan NEM irunk `recall`/`false_positives` szamot: azok OSZTALYOZASI metrikak, es egy
konformancia-korpuszon (ahol nincs pozitiv/negativ osztaly) ERTELMETLENEK volnanak. A cimke nem
allithat tobbet a meresnel. stdlib only, nincs halozat."""
import hashlib
import json
import os
import sys

# GYOKER-SZINTU BYTECODE-TILTAS: enelkul minden verify-futas (a publish-motor kapu-futasat is beleertve)
# letrehoz egy oracle/__pycache__/*.pyc-t, amit utolagos takaritassal nem lehet megszuntetni, csak elkerulni.
sys.dont_write_bytecode = True

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "oracle"))
import markdown__fn_parse as oracle  # noqa: E402


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    probes = [json.loads(l) for l in open(os.path.join(base, "probes", "probes.jsonl"), encoding="utf-8")
              if l.strip()]
    if len({json.dumps(p["expect"], sort_keys=True) for p in probes}) < 2:
        print("DEGENERALT korpusz (<2 kulonbozo kimenet) -- PIROS")
        return 1
    agree = disagree = 0
    outs = []
    for p in probes:
        try:
            got = oracle.REFERENCE(p["input"])
        except Exception:                                  # noqa: BLE001
            got = None
        outs.append(got)
        if oracle.decide(oracle.REFERENCE, p["input"], p["expect"]) == "PASS":
            agree += 1
        else:
            disagree += 1
            print("  ELTERES input=%r" % (p["input"],))
    lock = hashlib.sha256(json.dumps({"out": outs}, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode("utf-8")).hexdigest()
    print("%s conformance oracle: probes=%d | agree=%d | disagree=%d | run_lock=%s"
          % (oracle.TASK, len(probes), agree, disagree, lock[:16]))
    if disagree:
        return 1
    print("ZOLD")
    return 0


if __name__ == "__main__":
    sys.exit(main())
