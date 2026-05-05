"""Route /api/guide: PHD2."""
from __future__ import annotations

from fastapi import APIRouter, Body, Depends, HTTPException

from ..auth import require_token
from ..deps import Bridge, get_bridge
from ..phd2.client import Phd2RpcError

router = APIRouter(prefix="/api/guide", tags=["guide"], dependencies=[Depends(require_token)])


@router.get("/status")
async def status(bridge: Bridge = Depends(get_bridge)) -> dict:
    return {
        "connection": bridge.phd2.state,
        "live": dict(bridge.phd2.live),
    }


@router.post("/start")
async def start(
    payload: dict = Body(default={}),
    bridge: Bridge = Depends(get_bridge),
) -> dict:
    try:
        result = await bridge.phd2.start_guiding(
            settle_pixels=float(payload.get("settle_pixels", 1.5)),
            settle_time=float(payload.get("settle_time", 10.0)),
            settle_timeout=float(payload.get("settle_timeout", 60.0)),
        )
    except (ConnectionError, Phd2RpcError) as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {"ok": True, "result": result}


@router.post("/stop")
async def stop(bridge: Bridge = Depends(get_bridge)) -> dict:
    try:
        await bridge.phd2.stop_capture()
    except (ConnectionError, Phd2RpcError) as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {"ok": True}


@router.post("/dither")
async def dither(
    payload: dict = Body(default={}),
    bridge: Bridge = Depends(get_bridge),
) -> dict:
    try:
        result = await bridge.phd2.dither(
            amount=float(payload.get("amount", 3.0)),
            ra_only=bool(payload.get("ra_only", False)),
            settle_pixels=float(payload.get("settle_pixels", 1.5)),
            settle_time=float(payload.get("settle_time", 10.0)),
            settle_timeout=float(payload.get("settle_timeout", 60.0)),
        )
    except (ConnectionError, Phd2RpcError) as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {"ok": True, "result": result}


@router.post("/loop")
async def loop_(bridge: Bridge = Depends(get_bridge)) -> dict:
    try:
        await bridge.phd2.loop()
    except (ConnectionError, Phd2RpcError) as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {"ok": True}


@router.post("/clear_calibration")
async def clear_calibration(
    payload: dict = Body(default={}),
    bridge: Bridge = Depends(get_bridge),
) -> dict:
    which = payload.get("which", "Both")
    try:
        await bridge.phd2.clear_calibration(which)
    except (ConnectionError, Phd2RpcError) as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {"ok": True}


@router.post("/pause")
async def pause(
    payload: dict = Body(default={}),
    bridge: Bridge = Depends(get_bridge),
) -> dict:
    try:
        await bridge.phd2.set_paused(bool(payload.get("paused", True)),
                                    full=bool(payload.get("full", False)))
    except (ConnectionError, Phd2RpcError) as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {"ok": True}


@router.post("/find_star")
async def find_star(bridge: Bridge = Depends(get_bridge)) -> dict:
    try:
        r = await bridge.phd2.call("find_star")
    except (ConnectionError, Phd2RpcError) as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {"ok": True, "result": r}


@router.post("/calibrate")
async def calibrate(bridge: Bridge = Depends(get_bridge)) -> dict:
    """Avvia calibration completa: clear cal -> guide (forza recalibrate)."""
    try:
        await bridge.phd2.call("clear_calibration", "Both")
        await bridge.phd2.call("guide", {
            "settle": {"pixels": 1.5, "time": 10.0, "timeout": 60.0},
            "recalibrate": True,
        })
    except (ConnectionError, Phd2RpcError) as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {"ok": True}


@router.get("/profile")
async def profile(bridge: Bridge = Depends(get_bridge)) -> dict:
    """Restituisce info su profilo guide attivo (camera, mount, scope)."""
    try:
        eq = await bridge.phd2.call("get_current_equipment", timeout=5.0)
    except Exception:
        eq = None
    info: dict = {"equipment": eq or {}}
    try:
        info["pixel_scale"] = await bridge.phd2.call("get_pixel_scale", timeout=3.0)
    except Exception:
        pass
    try:
        info["calibrated"] = await bridge.phd2.call("get_calibrated", timeout=3.0)
    except Exception:
        pass
    try:
        info["app_state"] = await bridge.phd2.call("get_app_state", timeout=3.0)
    except Exception:
        pass
    return info
