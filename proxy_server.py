from flask import Flask, Response, request
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

app = Flask(__name__)

# HTML 页面代理 + 替换资源路径
@app.route('/proxy')
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return "Missing 'url' parameter", 400

    try:
        r = requests.get(target_url, timeout=5)
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')

        # 替换资源路径
        for tag in soup.find_all(['script', 'link', 'img']):
            attr = 'src' if tag.name != 'link' else 'href'
            if tag.has_attr(attr):
                original_path = tag[attr]
                new_url = f"/proxy/resource?base={target_url}&path={original_path}"
                tag[attr] = new_url

        return Response(str(soup), content_type='text/html')
    except Exception as e:
        return f"Error fetching target URL: {e}", 500


# 静态资源中转接口
@app.route('/proxy/resource')
def proxy_resource():
    base_url = request.args.get('base')
    path = request.args.get('path')
    if not base_url or not path:
        return "Missing base or path", 400

    full_url = urljoin(base_url, path)
    try:
        r = requests.get(full_url, timeout=5)
        return Response(r.content, content_type=r.headers.get('Content-Type', 'application/octet-stream'))
    except Exception as e:
        return f"Error fetching resource: {e}", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
