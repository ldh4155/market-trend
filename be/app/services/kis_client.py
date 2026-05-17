from typing import Any

import httpx

from app.core.config import settings


class KisApiError(RuntimeError):
    pass


class KisClient:
    def __init__(self, timeout: float = 10.0) -> None:
        self.base_url = settings.KIS_BASE_URL.rstrip("/")
        self.app_key = settings.KIS_APP_KEY
        self.app_secret = settings.KIS_APP_SECRET
        self.timeout = timeout

        if not self.app_key or not self.app_secret:
            raise KisApiError("KIS_APP_KEY and KIS_APP_SECRET are required.")

    def issue_access_token(self) -> str:
        response = httpx.post(
            f"{self.base_url}/oauth2/tokenP",
            headers={"content-type": "application/json; charset=utf-8"},
            json={
                "grant_type": "client_credentials",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
            },
            timeout=self.timeout,
        )
        self._raise_for_error(response)
        payload = response.json()
        token = payload.get("access_token")
        if not token:
            raise KisApiError(f"KIS token response did not include access_token: {payload}")
        return token

    def fetch_near_highlow(
        self,
        *,
        access_token: str,
        price_class_code: str = "0",
        input_market_code: str = "0000",
        volume_range: str = "0",
    ) -> list[dict[str, Any]]:
        response = httpx.get(
            f"{self.base_url}/uapi/domestic-stock/v1/ranking/near-new-highlow",
            headers={
                "content-type": "application/json; charset=utf-8",
                "authorization": f"Bearer {access_token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": "FHPST01870000",
                "custtype": "P",
            },
            params={
                "fid_cond_mrkt_div_code": "J",
                "fid_cond_scr_div_code": "20187",
                "fid_div_cls_code": "0",
                "fid_input_cnt_1": "",
                "fid_input_cnt_2": "",
                "fid_prc_cls_code": price_class_code,
                "fid_input_iscd": input_market_code,
                "fid_trgt_cls_code": "0",
                "fid_trgt_exls_cls_code": "0",
                "fid_aply_rang_prc_1": "",
                "fid_aply_rang_prc_2": "",
                "fid_aply_rang_vol": volume_range,
            },
            timeout=self.timeout,
        )
        self._raise_for_error(response)
        payload = response.json()
        if payload.get("rt_cd") != "0":
            raise KisApiError(
                f"KIS near-highlow API failed: {payload.get('msg_cd')} {payload.get('msg1')}"
            )
        output = payload.get("output") or []
        if not isinstance(output, list):
            raise KisApiError(f"KIS near-highlow output was not a list: {payload}")
        return output

    @staticmethod
    def _raise_for_error(response: httpx.Response) -> None:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise KisApiError(
                f"KIS HTTP error {response.status_code}: {response.text[:500]}"
            ) from exc
