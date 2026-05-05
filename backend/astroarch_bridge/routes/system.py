"""Route /api/system: stato globale, snapshot, info."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from .. import __version__
from ..auth import require_token
from ..deps import Bridge, get_bridge

router = APIRouter(prefix="/api/system", tags=["system"], dependencies=[Depends(require_token)])


@router.get("/info")
async def info(bridge: Bridge = Depends(get_bridge)) -> dict:
    return {
        "name": "astroarch-bridge",
        "version": __version__,
        "developer": "Zarletti-Osservatorio Jupiter",
    }


@router.get("/snapshot")
async def snapshot(bridge: Bridge = Depends(get_bridge)) -> dict:
    return await bridge.state.snapshot()


@router.get("/connections")
async def connections(bridge: Bridge = Depends(get_bridge)) -> dict:
    snap = await bridge.state.snapshot()
    return snap["connections"]


@router.get("/devices")
async def devices(bridge: Bridge = Depends(get_bridge)) -> dict:
    return {"devices": await bridge.state.list_devices()}


@router.get("/camera_roles")
async def camera_roles(bridge: Bridge = Depends(get_bridge)) -> dict:
    """Identifica la camera primaria (imaging) e quella di guida.

    Strategia:
    1. Chiede a PHD2 quale camera sta usando (= guide)
    2. Heuristic sui nomi (ASI120/290/174/Guide/Guider)
    3. Se solo una camera -> primary
    """
    cameras = await bridge.state.find_devices_by_role("CCD_EXPOSURE")
    guide: str | None = None
    method = "none"

    # Step 1: PHD2 -> camera attiva è la guida
    try:
        if bridge.phd2.state == "connected":
            eq = await bridge.phd2.call("get_current_equipment", timeout=4.0)
            if isinstance(eq, dict):
                cam_info = eq.get("camera") or {}
                cam_name = (cam_info.get("name") or "").strip()
                if cam_name:
                    cn_low = cam_name.lower()
                    for c in cameras:
                        cl = c.lower()
                        if cl in cn_low or cn_low in cl:
                            guide = c
                            method = "phd2"
                            break
    except Exception:
        pass

    # Step 2: heuristic naming
    if guide is None:
        guide_keywords = ("guide", "guider", "asi120", "asi174",
                          "asi178", "asi290", "asi585", "qhy5")
        for c in cameras:
            cl = c.lower()
            if any(k in cl for k in guide_keywords):
                guide = c
                method = "heuristic"
                break

    # Primary = primo non-guide
    primary: str | None = None
    for c in cameras:
        if c != guide:
            primary = c
            break

    if primary is None and cameras:
        primary = cameras[0]
        guide = None
        method = "single"

    return {
        "cameras": cameras,
        "primary": primary,
        "guide": guide,
        "method": method,
    }


@router.get("/simbad")
async def simbad_search(name: str) -> dict:
    """Risolve nome oggetto astronomico in RA/Dec via Sesame (CDS) usando astropy.

    Es: /api/system/simbad?name=M31
    """
    import asyncio
    from astropy.coordinates import SkyCoord
    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="empty name")

    def _resolve():
        try:
            sc = SkyCoord.from_name(name)
            return {
                "name": name,
                "ra_hours": float(sc.ra.hour),
                "dec_deg": float(sc.dec.deg),
                "ra_str": sc.ra.to_string(unit="hour", sep=":", precision=2),
                "dec_str": sc.dec.to_string(unit="deg", sep=":", precision=2,
                                            alwayssign=True),
            }
        except Exception as e:
            return {"error": str(e)}

    try:
        result = await asyncio.wait_for(asyncio.to_thread(_resolve), timeout=10.0)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="SIMBAD timeout")
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
