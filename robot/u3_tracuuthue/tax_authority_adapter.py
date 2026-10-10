"""TaxAuthorityAdapter: giao tiếp web Cục Thuế qua interface để test mock được.

Web Cục Thuế là web thật: mở trang → nhập mã số thuế → lấy ảnh captcha → nhập
chuỗi captcha đã giải → submit → đọc kết quả → export PDF. Interface
TaxAuthorityPort cho phép thay hiện thực Playwright (production) bằng mock trong
test (NFR6). URL/cấu hình đọc từ data/config.yaml, không hardcode (BR3.7).
"""
from __future__ import annotations

import os
from typing import Any, Optional, Protocol

from robot.logging_setup import StructuredLogger
from robot.u3_tracuuthue.captcha_solver import CaptchaError, CaptchaSolver


class TaxAuthorityError(Exception):
    """Lỗi khi thao tác với web Cục Thuế."""


class TaxAuthorityPort(Protocol):
    """Cổng trừu tượng tới web Cục Thuế (mock hoặc Playwright thật)."""

    def open(self) -> None:
        """Mở trang tra cứu tình trạng người nộp thuế."""
        ...

    def enter_mst(self, tax_code: str) -> None:
        """Nhập mã số thuế vào form."""
        ...

    def get_captcha_image(self) -> bytes:
        """Lấy ảnh captcha hiện tại (bytes)."""
        ...

    def submit(self, captcha_text: str) -> bool:
        """Submit với chuỗi captcha; trả True nếu captcha được chấp nhận.

        Trả False khi captcha sai (để client thử lại trong giới hạn số lần).
        """
        ...

    def has_result(self) -> bool:
        """Có kết quả tra cứu hay không (sau khi submit được chấp nhận)."""
        ...

    def export_pdf(self, output_path: str) -> str:
        """Export 'Tra cứu tình trạng người nộp thuế.pdf', trả đường dẫn file."""
        ...


class TaxLookupResult:
    """Kết quả tra cứu Cục Thuế cho một mã số thuế."""

    def __init__(self, found: bool, pdf_path: Optional[str]) -> None:
        self.found = found
        self.pdf_path = pdf_path


RESULT_PDF_NAME = "Tra cứu tình trạng người nộp thuế.pdf"


class TaxAuthorityClient:
    """Điều phối luồng tra cứu Cục Thuế qua TaxAuthorityPort + CaptchaSolver.

    Chỉ gọi với KHDN đã có mã số thuế (TaxAuthorityStage lo điều kiện KHCN/MST).
    """

    def __init__(
        self,
        port: TaxAuthorityPort,
        captcha_solver: CaptchaSolver,
        logger: StructuredLogger,
        output_dir: str,
    ) -> None:
        self.port = port
        self.captcha_solver = captcha_solver
        self.logger = logger
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def lookup(self, tax_code: str) -> TaxLookupResult:
        """Tra cứu một mã số thuế. Raise TaxAuthorityError khi lỗi/captcha fail."""
        try:
            self.port.open()
            
            def get_image_and_enter_mst() -> bytes:
                self.port.enter_mst(tax_code)
                return self.port.get_captcha_image()
                
            # Giải captcha, submit; sai thì CaptchaSolver thử lại trong giới hạn.
            self.captcha_solver.solve_with_retry(
                image_provider=get_image_and_enter_mst,
                verifier=self.port.submit,
            )
        except CaptchaError as exc:
            raise TaxAuthorityError(f"Captcha Cục Thuế lỗi: {exc}") from exc
        except Exception as exc:  # noqa: BLE001 - gom lỗi cổng thành TaxAuthorityError
            raise TaxAuthorityError(f"Tra cứu Cục Thuế lỗi: {exc}") from exc

        if not self.port.has_result():
            self.logger.info("Cục Thuế không có kết quả", tax_code=tax_code)
            return TaxLookupResult(found=False, pdf_path=None)

        pdf_path = self.port.export_pdf(os.path.join(self.output_dir, RESULT_PDF_NAME))
        self.logger.info("Cục Thuế có kết quả, đã in PDF", tax_code=tax_code)
        return TaxLookupResult(found=True, pdf_path=pdf_path)


class MockTaxAuthorityPort:
    """Mock TaxAuthorityPort cho test/dev: không chạm web thật.

    Cho phép mô phỏng: captcha được chấp nhận sau N lần, có/không có kết quả,
    hoặc ném lỗi thao tác.
    """

    def __init__(
        self,
        has_result: bool = True,
        accept_after: int = 1,
        fail_on: Optional[str] = None,
        captcha_image: bytes = b"captcha",
    ) -> None:
        self._has_result = has_result
        self._accept_after = max(1, int(accept_after))
        self._fail_on = fail_on
        self._captcha_image = captcha_image
        self._submit_count = 0

    def open(self) -> None:
        if self._fail_on == "open":
            raise RuntimeError("mở trang Cục Thuế thất bại")

    def enter_mst(self, tax_code: str) -> None:
        if self._fail_on == "enter_mst":
            raise RuntimeError("nhập MST thất bại")

    def get_captcha_image(self) -> bytes:
        if self._fail_on == "get_captcha_image":
            raise RuntimeError("lấy captcha thất bại")
        return self._captcha_image

    def submit(self, captcha_text: str) -> bool:
        if self._fail_on == "submit":
            raise RuntimeError("submit thất bại")
        self._submit_count += 1
        return self._submit_count >= self._accept_after

    def has_result(self) -> bool:
        return self._has_result

    def export_pdf(self, output_path: str) -> str:
        return output_path


class PlaywrightTaxAuthorityPort:
    """Hiện thực TaxAuthorityPort bằng Playwright cho web Cục Thuế thật.

    Dùng ở production, không trong test.
    """
    
    URL = "https://tracuunnt.gdt.gov.vn/tcnnt/mstdn.jsp"
    MST_SELECTOR = "[name='mst']"
    CAPTCHA_SELECTOR = "table img"
    CAPTCHA_INPUT_SELECTOR = "[name='captcha']"
    SUBMIT_SELECTOR = "[onclick='search();']"
    
    def __init__(self, config: Any, logger: StructuredLogger) -> None:
        self.config = config
        self.logger = logger
        self._browser: Any = None
        self._page: Any = None
        self._playwright: Any = None
        self._has_result_cache = False

    def _ensure_page(self) -> Any:
        if self._page is None:  # pragma: no cover
            from playwright.sync_api import sync_playwright  # type: ignore

            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(
                headless=False,
                args=["--start-maximized"]
            )
            context = self._browser.new_context(no_viewport=True)
            self._page = context.new_page()
        return self._page

    def open(self) -> None:  # pragma: no cover
        page = self._ensure_page()
        page.goto(self.URL, wait_until="load", timeout=30000)
        page.wait_for_selector(self.CAPTCHA_SELECTOR, timeout=30000)

    def enter_mst(self, tax_code: str) -> None:  # pragma: no cover
        page = self._ensure_page()
        page.fill(self.MST_SELECTOR, tax_code)

    def get_captcha_image(self) -> bytes:  # pragma: no cover
        page = self._ensure_page()
        element = page.wait_for_selector(self.CAPTCHA_SELECTOR, timeout=30000)
        if element is None:
            raise TaxAuthorityError("Không tìm thấy ảnh captcha")
        return element.screenshot()

    def submit(self, captcha_text: str) -> bool:  # pragma: no cover
        page = self._ensure_page()
        page.locator(self.CAPTCHA_INPUT_SELECTOR).press_sequentially(captcha_text, delay=100)
        page.locator(self.CAPTCHA_INPUT_SELECTOR).press("Tab")
        page.wait_for_timeout(2000)
        
        page.click(self.SUBMIT_SELECTOR)
        
        # Đợi trang bắt đầu xử lý request để tránh check quá nhanh
        page.wait_for_timeout(10000)
        
        # Wait for either result, error, or not_found
        import time
        deadline = time.monotonic() + 30.0
        while time.monotonic() < deadline:
            if page.get_by_text("Vui lòng nhập đúng mã xác nhận!", exact=False).is_visible():
                self.logger.info("Sai captcha, cần retry")
                # Reload page to get new captcha as in legacy
                page.goto(self.URL, wait_until="load", timeout=30000)
                return False
            if page.locator("xpath=//*[contains(text(), 'Too Many Requests')]").is_visible():
                self.logger.warning("Bị chặn 'Too Many Requests', chờ 5s...")
                page.wait_for_timeout(5000)
                page.goto(self.URL, wait_until="load", timeout=30000)
                return False
            if page.locator("#resultContainer table tbody tr:nth-child(2) td:nth-child(2)").is_visible():
                self._has_result_cache = True
                return True
            if page.get_by_text("Không tìm thấy người nộp thuế nào phù hợp", exact=False).is_visible() or \
               page.get_by_text("không hợp lệ!", exact=False).is_visible():
                self._has_result_cache = False
                return True
            page.wait_for_timeout(1000)
        
        raise TaxAuthorityError("Timeout khi đợi kết quả tra cứu")

    def has_result(self) -> bool:  # pragma: no cover
        return self._has_result_cache

    def export_pdf(self, output_path: str) -> str:  # pragma: no cover
        page = self._ensure_page()
        page.pdf(path=output_path)
        return output_path

    def close(self) -> None:  # pragma: no cover
        if self._browser is not None:
            self._browser.close()
        if self._playwright is not None:
            self._playwright.stop()
