"""Route /api/focuser."""
from __future__ import annotations

from fastapi import APIRouter, Body, Depends, HTTPException

from ..auth import require_token
from ..deps import Bridge, get_bridge
from ._roles import first_element, resolve_device

router = APIRouter(prefix="/api/focuser", tags=["focuser"], dependencies=[Depends(require_token)])


@router.get("/status")
async def status(device: str | None = None, bridge: Bridge = Depends(get_bridge)) -> dict:
    dev = await resolve_device(bridge.state, "focuser", device)
    pos = await bridge.state.get_property(dev, "ABS_FOCUS_POSITION") or {}
    rel = await bridge.state.get_property(dev, "REL_FOCUS_POSITION") or {}
    temp = await bridge.state.get_property(dev, "FOCUS_TEMPERATURE") or {}
    abort = await bridge.state.get_property(dev, "FOCUS_ABORT_MOTION") or {}
    backlash = await bridge.state.get_property(dev, "FOCUS_BACKLASH_STEPS") or {}
    direction = await bridge.state.get_property(dev, "FOCUS_MOTION") or {}
    return {
        "device": dev,
        "position": first_element(pos, "FOCUS_ABSOLUTE_POSITION"),
        "max_position": _max_for(pos, "FOCUS_ABSOLUTE_POSITION"),
        "rel_step": first_element(rel, "FOCUS_RELATIVE_POSITION"),
        "temperature": first_element(temp, "TEMPERATURE"),
        "backlash": first_element(backlash, "FOCUS_BACKLASH_VALUE"),
        "moving": pos.get("state") == "Busy",
        "direction": _selected_switch(direction),
    }


@router.post("/abs")
async def goto_abs(
    payload: dict = Body(..., example={"position": 24350}),
    bridge: Bridge = Depends(get_bridge),
) -> dict:
    dev = await resolve_device(bridge.state, "focuser", payload.get("device"))
    pos = int(payload["position"])
    await bridge.indi.send_number(dev, "ABS_FOCUS_POSITION", {"FOCUS_ABSOLUTE_POSITION": pos})
    return {"ok": True}


@router.post("/rel")
async def move_rel(
    payload: dict = Body(..., example={"steps": 100, "direction": "in"}),
    bridge: Bridge = Depends(get_bridge),
) -> dict:
    dev = await resolve_device(bridge.state, "focuser", payload.get("device"))
    steps = abs(int(payload["steps"]))
    direction = (payload.get("direction") or "out").lower()
    if direction not in ("in", "out"):
        raise HTTPException(status_code=400, detail="direction must be in|out")
    # FOCUS_MOTION: FOCUS_INWARD | FOCUS_OUTWARD
    await bridge.indi.send_switch(dev, "FOCUS_MOTION", {
        "FOCUS_INWARD": direction == "in",
        "FOCUS_OUTWARD": direction == "out",
    })
    await bridge.indi.send_number(dev, "REL_FOCUS_POSITION", {"FOCUS_RELATIVE_POSITION": steps})
    return {"ok": True}


@router.post("/abort")
async def abort(device: str | None = None, bridge: Bridge = Depends(get_bridge)) -> dict:
    dev = await resolve_device(bridge.state, "focuser", device)
    await bridge.indi.send_switch(dev, "FOCUS_ABORT_MOTION", {"ABORT": True})
    return {"ok": True}


# In-memory state degli autofocus run (per polling progress)
_AUTOFOCUS_RUNS: dict[str, dict] = {}


@router.post("/autofocus")
async def autofocus_start(
    payload: dict = Body(default={}),
    bridge: Bridge = Depends(get_bridge),
) -> dict:
    """Avvia autofocus iterativo lato bridge.

    Algoritmo:
    1. Prende posizione corrente
    2. Per N step (default 9), cambia posizione di step_size
    3. Per ogni posizione: scatta exposure_sec, attende fine, legge HFR dal frame
    4. Determina V-curve, trova minimo HFR, sposta focuser su quella posizione

    Body params:
      device: str (focuser device, optional if 1 only)
      camera: str (camera device, optional if 1 only)
      step_size: int (default 50)
      n_steps: int (default 9, dispari)
      exposure_sec: float (default 2.0)
    """
    foc = await resolve_device(bridge.state, "focuser", payload.get("device"))
    cam = await resolve_device(bridge.state, "camera", payload.get("camera"))
    step_size = int(payload.get("step_size", 50))
    n_steps = int(payload.get("n_steps", 9))
    if n_steps % 2 == 0:
        n_steps += 1
    exposure = float(payload.get("exposure_sec", 2.0))

    pos_prop = await bridge.state.get_property(foc, "ABS_FOCUS_POSITION")
    cur_pos = first_element(pos_prop, "FOCUS_ABSOLUTE_POSITION", 0)
    if cur_pos is None:
        raise HTTPException(status_code=503, detail="cannot read focuser position")
    cur_pos = int(cur_pos)

    run_id = f"af_{int(asyncio.get_event_loop().time() * 1000)}"
    _AUTOFOCUS_RUNS[run_id] = {
        "id": run_id,
        "focuser": foc,
        "camera": cam,
        "step_size": step_size,
        "n_steps": n_steps,
        "exposure": exposure,
        "start_pos": cur_pos,
        "samples": [],   # list of {pos, hfr, stars}
        "best_pos": None,
        "best_hfr": None,
        "status": "running",  # running | done | failed
        "step_idx": 0,
        "error": None,
    }
    asyncio.create_task(_run_autofocus(bridge, run_id))
    return {"ok": True, "run_id": run_id}


@router.get("/autofocus/{run_id}")
async def autofocus_status(run_id: str) -> dict:
    run = _AUTOFOCUS_RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run not found")
    return run


@router.post("/autofocus/{run_id}/abort")
async def autofocus_abort(run_id: str) -> dict:
    run = _AUTOFOCUS_RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run not found")
    run["status"] = "aborting"
    return {"ok": True}


async def _run_autofocus(bridge: Bridge, run_id: str) -> None:
    import asyncio as _asyncio
    run = _AUTOFOCUS_RUNS[run_id]
    foc = run["focuser"]
    cam = run["camera"]
    step = run["step_size"]
    n = run["n_steps"]
    exp = run["exposure"]
    start = run["start_pos"]

    half = n // 2
    positions = [start + (i - half) * step for i in range(n)]

    try:
        for idx, pos in enumerate(positions):
            if run["status"] == "aborting":
                run["status"] = "aborted"
                return
            run["step_idx"] = idx + 1
            # Move focuser
            await bridge.indi.send_number(foc, "ABS_FOCUS_POSITION",
                                          {"FOCUS_ABSOLUTE_POSITION": pos})
            # Wait until move done (state Ok)
            ok = await _wait_prop_state(bridge, foc, "ABS_FOCUS_POSITION", "Ok", 15)
            if not ok:
                run["error"] = f"focuser move timeout at {pos}"
                run["status"] = "failed"
                return
            # Set short exposure
            await bridge.indi.send_number(cam, "CCD_EXPOSURE", {"CCD_EXPOSURE_VALUE": exp})
            # Wait expose done
            ok = await _wait_prop_state(bridge, cam, "CCD_EXPOSURE", "Ok", int(exp) + 30)
            if not ok:
                run["error"] = f"expose timeout at {pos}"
                run["status"] = "failed"
                return
            # Read last frame HFR via state.last_frame_meta (image processor)
            await _asyncio.sleep(1.0)  # let processor finish
            # leggi snapshot per ottenere ultimo frame
            snap = await bridge.state.snapshot()
            lf = snap.get("last_frame", {}) or {}
            hfr = lf.get("hfr")
            stars = lf.get("stars")
            run["samples"].append({"pos": pos, "hfr": hfr, "stars": stars})

        # Find min HFR
        valid = [s for s in run["samples"] if s["hfr"] and s["hfr"] > 0]
        if not valid:
            run["error"] = "no valid HFR samples"
            run["status"] = "failed"
            return
        best = min(valid, key=lambda s: s["hfr"])
        run["best_pos"] = best["pos"]
        run["best_hfr"] = best["hfr"]
        # Move to best
        await bridge.indi.send_number(foc, "ABS_FOCUS_POSITION",
                                      {"FOCUS_ABSOLUTE_POSITION": int(best["pos"])})
        await _wait_prop_state(bridge, foc, "ABS_FOCUS_POSITION", "Ok", 20)
        run["status"] = "done"
    except Exception as e:
        run["error"] = str(e)
        run["status"] = "failed"


async def _wait_prop_state(bridge: Bridge, dev: str, name: str, target_state: str,
                            timeout_sec: int) -> bool:
    import asyncio
    deadline = asyncio.get_event_loop().time() + timeout_sec
    while asyncio.get_event_loop().time() < deadline:
        p = await bridge.state.get_property(dev, name)
        if p and p.get("state") == target_state:
            return True
        await asyncio.sleep(0.4)
    return False


# import asyncio here to avoid circular at import time
import asyncio  # noqa: E402


def _selected_switch(prop: dict) -> str | None:
    for e in prop.get("elements", []):
        if e.get("value") is True:
            return e["name"]
    return None


def _max_for(prop: dict, name: str):
    for e in prop.get("elements", []):
        if e["name"] == name:
            return e.get("max")
    return None
