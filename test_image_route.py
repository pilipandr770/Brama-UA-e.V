from app import app

with app.test_client() as client:
    response = client.get('/block-images/8')
    print(f'Status: {response.status_code}')
    print(f'Content-Type: {response.content_type}')
    print(f'Content-Length: {len(response.data) if response.data else 0}')
    if response.status_code == 302:  # redirect
        print(f'Redirect to: {response.headers.get("Location")}')