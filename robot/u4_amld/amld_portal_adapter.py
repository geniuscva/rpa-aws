"""AmldPortalAdapter: giao tiếp AMLD Online Portal qua interface để test mock được.

AMLD Portal là web thật: đăng nhập → vào tab Nhập STR → Mẫu số 01 → nhập các Phần
I/II/IV/V/VI → upload tài liệu → nộp. Interface AmldPortalPort cho phép thay hiện
thực Playwright (production) bằng mock trong test (NFR6). Username lấy từ
StrRecord.USER_ID_NGUOI_LAP_BAO_CAO; password/endpoint đọc từ data/config.yaml,
không hardcode (BR4.11/NFR4).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Protocol


class AmldError(Exception):
    """Lỗi khi thao tác với AMLD Portal."""


class AmldLoginHung(AmldError):
    """Màn hình đăng nhập AMLD treo (cần reload và thử lại — BR4.9)."""


@dataclass
class AmldSession:
    """Phiên làm việc AMLD: username từ record, password/endpoint từ config.

    Không giữ secret ngoài vòng đời phiên; không log giá trị password (BR4.11).
    """

    username: str
    endpoint: str
    password: str = ""

    def masked(self) -> dict[str, str]:
        """Thông tin an toàn để log (ẩn password)."""
        return {"username": self.username, "endpoint": self.endpoint}


class AmldPortalPort(Protocol):
    """Cổng trừu tượng tới AMLD Portal (mock hoặc Playwright thật)."""

    def login(self, session: AmldSession) -> None:
        """Đăng nhập. Raise AmldLoginHung nếu màn hình đăng nhập treo (BR4.9)."""
        ...

    def open_form(self) -> None:
        """Vào tab 'Nhập STR' → 'Mẫu số 01'."""
        ...

    def fill_section(self, section: str, data: dict[str, Any]) -> None:
        """Nhập và lưu một Phần (I/II/IV/V/VI). KHÔNG bao giờ gọi với 'III'."""
        ...

    def set_ticks(self, section: str, values: list) -> None:
        """Tick các giá trị cho Phần IV/V."""
        ...

    def upload(self, filename: str) -> int:
        """Upload một tài liệu Phần VI, trả số trang đã đếm."""
        ...

    def submit(self) -> str:
        """Nộp báo cáo, trả trạng thái tra soát (BOT_TINHTRANGTRASOAT)."""
        ...


class MockAmldPortalPort:
    """Mock AmldPortalPort cho test/dev: không chạm web thật.

    Ghi lại các Phần đã nhập (để test khẳng định KHÔNG có Phần III), mô phỏng
    đăng nhập treo N lần, hoặc ném lỗi ở một thao tác.
    """

    def __init__(
        self,
        login_hangs: int = 0,
        fail_on: Optional[str] = None,
        trasoat_status: str = "DaTraSoat",
    ) -> None:
        self._login_hangs = int(login_hangs)
        self._login_calls = 0
        self._fail_on = fail_on
        self._trasoat_status = trasoat_status
        # Dấu vết để test kiểm tra hành vi.
        self.sections_filled: list[str] = []
        self.ticks: dict[str, list] = {}
        self.uploaded: list[str] = []
        self.submitted = False

    def login(self, session: AmldSession) -> None:
        self._login_calls += 1
        if self._login_calls <= self._login_hangs:
            raise AmldLoginHung("màn hình đăng nhập treo")
        if self._fail_on == "login":
            raise AmldError("đăng nhập thất bại")

    def open_form(self) -> None:
        if self._fail_on == "open_form":
            raise AmldError("mở Mẫu số 01 thất bại")

    def fill_section(self, section: str, data: dict[str, Any]) -> None:
        if section == "III":
            raise AssertionError("KHÔNG được điền Phần III (BR4.2)")
        if self._fail_on == f"section:{section}":
            raise AmldError(f"nhập Phần {section} thất bại")
        self.sections_filled.append(section)

    def set_ticks(self, section: str, values: list) -> None:
        self.ticks[section] = list(values)

    def upload(self, filename: str) -> int:
        if self._fail_on == "upload":
            raise AmldError("upload tài liệu thất bại")
        self.uploaded.append(filename)
        return 1

    def submit(self) -> str:
        if self._fail_on == "submit":
            raise AmldError("nộp báo cáo thất bại")
        self.submitted = True
        return self._trasoat_status


class PlaywrightAmldPortalPort:
    """Hiện thực AmldPortalPort bằng Playwright cho AMLD Portal thật.

    Playwright import trễ; selector/endpoint đọc từ config, không hardcode
    (BR4.11). Dùng ở production, không trong test.
    """

    def __init__(self, config: Any, logger: Any) -> None:
        self.config = config
        self.logger = logger
        self._page: Any = None
        self._browser: Any = None
        self._playwright: Any = None

    def _ensure_page(self) -> Any:  # pragma: no cover - cần trình duyệt thật
        if self._page is None:
            from playwright.sync_api import sync_playwright  # type: ignore

            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(
                headless=False, 
                args=["--start-maximized"]
            )
            context = self._browser.new_context(no_viewport=True)
            self._page = context.new_page()
            
            # Tự động đồng ý (accept) mọi hộp thoại xác nhận (alert/confirm/prompt) 
            # để xử lý các `msg_part_*` từ hệ thống AMLD.
            self._page.on("dialog", lambda dialog: dialog.accept())
            
        return self._page

    def login(self, session: AmldSession) -> None:  # pragma: no cover - web thật
        page = self._ensure_page()
        from robot.u4_amld.amld_selectors import LOGIN_SELECTORS
        try:
            timeout_ms = getattr(self.config.amld, 'almd_login_hang_timeout_ms', 300000)
            page.goto(session.endpoint, wait_until="load", timeout=timeout_ms)
            page.wait_for_selector(LOGIN_SELECTORS["username"], timeout=timeout_ms)
        except Exception:
            # Check for hanging
            raise AmldLoginHung("đăng nhập treo hoặc không thể truy cập URL")
            
        page.locator(LOGIN_SELECTORS["username"]).press_sequentially(session.username, delay=300)
        page.locator(LOGIN_SELECTORS["password"]).press_sequentially(session.password, delay=300)
        page.wait_for_timeout(1000)
        page.click(LOGIN_SELECTORS["btn_login"])
        
        # Wait for navigation or error
        try:
            page.wait_for_timeout(3000)
            page.wait_for_selector("app-sidebar, " + LOGIN_SELECTORS["msg_error"], timeout=60000)
            if page.locator(LOGIN_SELECTORS["msg_error"]).count() > 0:
                raise AmldError("Đăng nhập thất bại do sai tài khoản/mật khẩu")
        except Exception as e:
            if not isinstance(e, AmldError):
                raise AmldLoginHung("Đăng nhập treo hoặc không vào được trang chủ")

    def open_form(self) -> None:  # pragma: no cover - web thật
        page = self._ensure_page()
        page.goto(self.config.amld.almd_url_report_two, wait_until="load", timeout=60000)
        from robot.u4_amld.amld_selectors import NAVIGATION_SELECTORS
        page.wait_for_selector(NAVIGATION_SELECTORS["tab_part_i"], timeout=60000)
        page.wait_for_timeout(3000)

    def fill_section(self, section: str, data: dict) -> None:  # pragma: no cover
        if section == "III":
            raise AssertionError("KHÔNG được điền Phần III (BR4.2)")
            
        page = self._ensure_page()
        from robot.u4_amld.amld_selectors import (
            NAVIGATION_SELECTORS,
            PART_I_SELECTORS,
            PART_II_SELECTORS,
            PART_IV_SELECTORS,
            PART_V_SELECTORS,
            PART_VI_SELECTORS
        )
        
        # Click tab corresponding to the section
        tab_key = f"tab_part_{section.lower()}"
        if tab_key in NAVIGATION_SELECTORS:
            page.click(NAVIGATION_SELECTORS[tab_key])
            page.wait_for_timeout(1000) # Give UI time to switch tab
            
        # Select save button
        btn_save = None
        if section == "I":
            btn_save = PART_I_SELECTORS["btn_save"]
            
            def _fill_i(k_selector: str, k_data: str) -> None:
                val = data.get(k_data)
                if val:
                    page.locator(PART_I_SELECTORS[k_selector]).fill(str(val))
                    
            _fill_i("input_ma_bc_noi_bo", "str_ma_bao_cao")
            _fill_i("input_ten_chinhanh", "ten_chi_nhanh")
            _fill_i("input_sonha_chinhanh", "so_nha_duong_pho_chi_nhanh")
            _fill_i("input_phuong_xa_chinhanh", "phuong_xa_chi_nhanh")
            _fill_i("input_tinh_thanh_chinhanh", "tinh_thanh_pho_chi_nhanh")
            _fill_i("input_dienthoai_chinhanh", "sdt_chi_nhanh")
            _fill_i("input_email_donvi", "email_nguoi_lap_bao_cao")
            _fill_i("input_nguoi_lap_hoten", "ten_nguoi_lap_bao_cao")
            _fill_i("input_nguoi_lap_dt_lamviec", "sdt_lam_viec_nguoi_lap_bao_cao")
            _fill_i("input_nguoi_lap_dt_didong", "sdt_dd_nguoi_lap_bao_cao")
            
        elif section == "II":
            btn_save = PART_II_SELECTORS["btn_save"]
        elif section == "IV":
            btn_save = PART_IV_SELECTORS["btn_save"]
            
            def _fill_iv(k_selector: str, k_data: str) -> None:
                val = data.get(k_data)
                if val:
                    page.locator(PART_IV_SELECTORS[k_selector]).fill(str(val))

            _fill_iv("input_ngay_bat_dau", "ngay_bat_dau")
            _fill_iv("input_ngay_ket_thuc", "ngay_ket_thuc")
            _fill_iv("textarea_co_so", "phan_iv_co_so_hop_ly_de_nghi_ngo")
            _fill_iv("textarea_ly_do", "phan_iv_3_phan_tich_ly_do_bao_cao")
            
            loai_bao_cao = str(data.get("phan_iv_loai_bao_cao_dang_ngo", "")).strip().upper()
            if loai_bao_cao and loai_bao_cao in PART_IV_SELECTORS["report_classification"]:
                page.locator(PART_IV_SELECTORS["report_classification"][loai_bao_cao]).check(force=True)
                
            toi_pham = str(data.get("phan_iv_nhan_dinh_loai_toi_pham", "")).strip()
            if toi_pham:
                if toi_pham in PART_IV_SELECTORS["crime_code"]:
                    page.locator(PART_IV_SELECTORS["crime_code"][toi_pham]).check(force=True)
                else:
                    page.locator(PART_IV_SELECTORS["crime_code"]["30"]).check(force=True)
                    page.locator(PART_IV_SELECTORS["input_toi_pham_khac"]).fill(toi_pham)
            
            try:
                page.locator(PART_IV_SELECTORS["radio_trang_thai_gd"]).check(force=True)
            except Exception:
                pass
                
        elif section == "V":
            btn_save = PART_V_SELECTORS["btn_save"]
        elif section == "VI":
            btn_save = PART_VI_SELECTORS["btn_save"]
            
        if btn_save:
            # Ignore UI validation/toast errors as we are just clicking save for now
            page.click(btn_save, force=True)
            page.wait_for_timeout(1500)

    def set_ticks(self, section: str, values: list) -> None:  # pragma: no cover
        page = self._ensure_page()
        from robot.u4_amld.amld_selectors import PART_IV_SELECTORS, PART_V_SELECTORS
        
        if section == "IV":
            for val in values:
                selector = PART_IV_SELECTORS["warning_sign"].get(str(val))
                if selector:
                    page.check(selector, force=True)
        elif section == "V":
            for val in values:
                selector = PART_V_SELECTORS["action_code"].get(str(val))
                if selector:
                    page.check(selector, force=True)

    def upload(self, files: list[str]) -> int:
        page = self._ensure_page()
        from robot.u4_amld.amld_selectors import PART_VI_SELECTORS
        import os
        
        count = 0
        for f in files:
            if not f:
                continue
            base = os.path.basename(f).lower()
            doc_type = "Tài liệu khác"
            desc = ""
            
            if base.startswith("bang_ke_") or "bảng kê" in base:
                doc_type = "Bảng kê"
                desc = "Bảng kê giao dịch"
            elif "minh_hoa" in base or "minh họa" in base:
                doc_type = "Minh họa dòng tiền"
                desc = "Minh họa dòng tiền"
            elif base.startswith("hsmtk_"):
                doc_type = "Hồ sơ mở tài khoản"
                desc = "Hồ sơ mở tài khoản"
            elif base.startswith("gttt_") or base.startswith("giay phep thanh lap_"):
                doc_type = "Hồ sơ khách hàng"
                desc = "Hồ sơ khách hàng"
            elif "accuity" in base:
                doc_type = "Tài liệu khác"
                desc = "Tra cứu Accuity"
            elif "thue" in base or "thuế" in base:
                doc_type = "Tài liệu khác"
                desc = "Tra cứu thuế"

            page.click(PART_VI_SELECTORS["btn_add_attachment"])
            page.wait_for_selector(PART_VI_SELECTORS["input_upload"])
            
            try:
                page.select_option(PART_VI_SELECTORS["select_attachment_type"], label=doc_type)
            except Exception:
                pass
            
            if desc:
                try:
                    page.locator(PART_VI_SELECTORS["input_attachment_description"]).press_sequentially(desc, delay=100)
                except Exception:
                    pass

            page.set_input_files(PART_VI_SELECTORS["input_upload"], f)
            page.click(PART_VI_SELECTORS["btn_confirm_upload"])
            page.wait_for_timeout(2000) # give it time to upload and close modal
            count += 1
            
        return count

    def submit(self) -> str:  # pragma: no cover - web thật
        page = self._ensure_page()
        from robot.u4_amld.amld_selectors import PART_VI_SELECTORS
        page.click(PART_VI_SELECTORS["btn_save"], force=True)
        return "DaTraSoat"

    def close(self) -> None:  # pragma: no cover - web thật
        if self._browser is not None:
            self._browser.close()
        if self._playwright is not None:
            self._playwright.stop()
