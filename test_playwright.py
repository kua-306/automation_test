import pytest
import random

# Cấu hình URL cơ sở
BASE_URL = "http://127.0.0.1:8000"

@pytest.fixture
def api_request(playwright):
    """Fixture tạo request context để gọi API trực tiếp"""
    request_context = playwright.request.new_context(base_url=BASE_URL)
    yield request_context
    request_context.dispose()

@pytest.fixture
def auth_token(api_request):
    """Fixture tự động đăng ký và đăng nhập để lấy Token"""
    # Tạo user ngẫu nhiên để tránh lỗi 'User already exists'
    user_id = random.randint(1000, 9999)
    username = f"user_{user_id}"
    password = "password123"

    # 1. Đăng ký (Signup)
    signup_res = api_request.post("/create-user/", json={
        "username": username,
        "password": password
    })
    # Nếu user đã tồn tại (200/201 đều OK, hoặc lỗi 400 thì vẫn tiếp tục login)
    
    # 2. Đăng nhập (Login)
    login_res = api_request.post("/login/", data={
        "username": username,
        "password": password
    })
    
    assert login_res.status == 200, f"Login failed: {login_res.text()}"
    token = login_res.json()["access_token"]
    return token

@pytest.fixture
def create_question(api_request, auth_token):
    """Fixture tạo một câu hỏi mẫu và trả về ID"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = api_request.post(
        "/create-question/",
        headers=headers,
        json={"question": "Python là gì?", "answer": "Một ngôn ngữ lập trình"}
    )
    assert response.status in [200, 201]
    return response.json()["id"]

# --- CÁC BÀI TEST CHÍNH ---

def test_get_question(api_request, auth_token, create_question):
    headers = {"Authorization": f"Bearer {auth_token}"}
    # Gọi API Get trực tiếp bằng ID
    response = api_request.get(f"/get-question/{create_question}", headers=headers)
    
    assert response.status == 200
    assert response.json()["id"] == create_question
    print(f"✅ Get Question {create_question} thành công!")

def test_patch_question(api_request, auth_token, create_question):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = api_request.patch(
        f"/update-question/{create_question}",
        headers=headers,
        json={"question": "What is Python?", "answer": "Programming Language"}
    )
    
    assert response.status == 200
    assert response.json()["question"] == "What is Python?"

def test_delete_question(api_request, auth_token, create_question):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = api_request.delete(f"/delete-question/{create_question}", headers=headers)
    
    assert response.status == 200
    assert "deleted" in response.json()["message"].lower()

def test_login_fail(api_request):
    """Test trường hợp đăng nhập sai"""
    response = api_request.post("/login/", data={
        "username": "wrong_user",
        "password": "wrong_password"
    })
    
    assert response.status == 400 # Hoặc 401 tùy Backend
    assert "incorrect" in response.json()["detail"].lower()