import os
import re
import pytest
from playwright.sync_api import Page, expect

# Hàm bổ trợ để lấy đường dẫn file HTML chuẩn cho cả Windows và Linux (CI/CD)
def get_local_html_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    clean_path = current_dir.replace("\\", "/")
    file_path = os.path.join(clean_path, "index.html")
    return file_path

# --- TEST CASE 1: MOCK ĐĂNG NHẬP THÀNH CÔNG ---
def test_mock_login_success(page: Page):
    # Chặn đứng gọi API /login/ và trả về Token giả
    page.route("**/login/", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"access_token": "mock_token_123", "token_type": "bearer"}'
    ))

    page.goto(get_local_html_path())
    page.fill("#username", "admin")
    page.fill("#password", "any_password")
    page.click("#login-btn")

    # Kiểm tra: UI phải hiện phần nhập câu hỏi (vì đã login thành công giả)
    expect(page.locator("#question-section")).to_be_visible()
    print("\n✅ Mock Success: Đăng nhập thành công mà không cần Backend!")

# --- TEST CASE 2: MOCK LỖI SAI MẬT KHẨU (401) ---
def test_mock_login_unauthorized(page: Page):
    # Chặn và trả về lỗi 401
    page.route("**/login/", lambda route: route.fulfill(
        status=401,
        content_type="application/json",
        body='{"detail": "Tên đăng nhập hoặc mật khẩu không đúng"}'
    ))

    page.goto(get_local_html_path())
    page.click("#login-btn") # Bấm luôn không cần nhập

    # Kiểm tra: UI phải hiện thông báo lỗi

    expect(page.locator("#message")).to_contain_text("không đúng")
    print("✅ Mock 401: UI hiển thị đúng lỗi sai tài khoản.")

# --- TEST CASE 3: MOCK SERVER SẬP (500) ---
def test_mock_server_error(page: Page):
    # Chặn và trả về lỗi 500
    page.route("**/login/", lambda route: route.fulfill(
        status=500,
        content_type="application/json",
        body='{"detail": "Hệ thống đang bảo trì. Vui lòng thử lại sau."}'
    ))

    page.goto(get_local_html_path())
    page.click("#login-btn")

    # Kiểm tra: UI xử lý thế nào khi Server "ngỏm"
    expect(page.locator("#message")).to_contain_text("bảo trì")
    print("Mock 500: UI hiển thị đúng thông báo bảo trì.")

def test_ui_error_styling(page: Page):
    # Mock lỗi bất kỳ
    page.route("**/login/", lambda route: route.fulfill(status=401, body='{"detail":"error"}'))
    
    page.goto(get_local_html_path())
    page.click("#login-btn")

    # CHECK UI: Thông báo lỗi phải có nền đỏ và chữ đỏ (Tailwind classes)
    # Đây mới là test UI: Check xem CSS có hoạt động đúng không
    msg = page.locator("#message")
    expect(msg).to_have_class(re.compile(r"bg-red-100"))
    expect(msg).to_have_class(re.compile(r"text-red-700"))

def test_ui_interaction_lock(page: Page):
    # Mock lỗi 500 (Server sập)
    page.route("**/login/", lambda route: route.fulfill(status=500))
    
    page.goto(get_local_html_path())
    page.click("#login-btn")

    # CHECK UI: Phần "Tạo câu hỏi" vẫn phải bị mờ (opacity-50) 
    # và không cho phép click (pointer-events-none)
    question_section = page.locator("#question-section")
    expect(question_section).to_have_class(re.compile(r"opacity-50"))
    expect(question_section).to_have_class(re.compile(r"pointer-events-none"))
    
    print("✅ UI vẫn khóa đúng như thiết kế khi Server lỗi!")


def get_local_html_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    clean_path = current_dir.replace("\\", "/")
    return f"file:///{clean_path}/index.html"

# --- 1. TEST TÍNH TRỰC QUAN (MÀU SẮC & HIỂN THỊ) ---
def test_ui_error_feedback_styling(page: Page):
    """Kiểm tra xem khi lỗi, thông báo có hiện đúng màu Đỏ của Tailwind không"""
    page.route("**/login/", lambda route: route.fulfill(status=401, body='{"detail":"Lỗi"}'))
    page.goto(get_local_html_path())
    
    page.click("#login-btn")
    
    msg = page.locator("#message")
    # Kiểm tra class Tailwind: bg-red-100 (nền đỏ nhạt), text-red-700 (chữ đỏ đậm)
    expect(msg).to_have_class(re.compile(r"bg-red-100"))
    expect(msg).to_have_class(re.compile(r"text-red-700"))
    expect(msg).to_be_visible()

def test_ui_success_feedback_styling(page: Page):
    """Kiểm tra xem khi thành công, thông báo có hiện màu Xanh không"""
    page.route("**/login/", lambda route: route.fulfill(
        status=200, 
        body='{"access_token": "abc", "token_type": "bearer"}'
    ))
    page.goto(get_local_html_path())
    
    page.click("#login-btn")
    
    msg = page.locator("#message")
    expect(msg).to_have_class(re.compile(r"bg-green-100"))
    expect(msg).to_have_class(re.compile(r"text-green-700"))

# --- 2. TEST LOGIC KHÓA/MỞ GIAO DIỆN (INTERACTION STATES) ---
def test_ui_section_unlock_on_success(page: Page):
    """Quan trọng: Đăng nhập xong thì phần 'Tạo câu hỏi' phải hết mờ và cho bấm"""
    page.route("**/login/", lambda route: route.fulfill(
        status=200, body='{"access_token": "token123"}'
    ))
    page.goto(get_local_html_path())

    # Trước khi login: Phải có class làm mờ
    section = page.locator("#question-section")
    expect(section).to_have_class(re.compile(r"opacity-50"))

    page.click("#login-btn")

    # Sau khi login: Phải mất class opacity-50 và pointer-events-none
    expect(section).not_to_have_class(re.compile(r"opacity-50"))
    expect(section).not_to_have_class(re.compile(r"pointer-events-none"))

# --- 3. TEST TRẢI NGHIỆM NGƯỜI DÙNG (UX) ---
def test_ui_initial_state(page: Page):
    """Kiểm tra trạng thái ban đầu khi mới mở trang"""
    page.goto(get_local_html_path())
    
    # Message phải ẩn hoàn toàn (có class hidden)
    expect(page.locator("#message")).to_have_class(re.compile(r"hidden"))
    # Nút đăng nhập phải có màu xanh dương (blue-500)
    expect(page.locator("#login-btn")).to_have_class(re.compile(r"bg-blue-500"))

def test_ui_empty_fields_behavior(page: Page):
    """Test xem nếu để trống username/password mà bấm thì UI hiện gì (Edge case)"""
    # Giả sử Backend trả về lỗi 422 khi để trống
    page.route("**/login/", lambda route: route.fulfill(status=422, body='{"detail":"Missing fields"}'))
    page.goto(get_local_html_path())
    
    # Không điền gì, bấm luôn
    page.click("#login-btn")
    
    # UI phải hiện lỗi và vùng câu hỏi vẫn phải bị khóa
    expect(page.locator("#message")).to_be_visible()
    expect(page.locator("#question-section")).to_have_class(re.compile(r"opacity-50"))