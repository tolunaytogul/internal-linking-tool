from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import logging

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Tüm domainlerden erişime izin veriyoruz, daha sonra sınırlandırabilirsiniz
CORS(app, origins=["*"])

def check_url(url):
    try:
        # Zaman aşımını arttıralım
        response = requests.get(url, allow_redirects=False, timeout=15)
        if response.status_code == 301:
            return {
                "url": url,
                "redirect_to": response.headers.get('Location', url),
                "status": 301,
                "note": "Çözüm İçin Danış"
            }
        elif response.status_code in range(300, 399):
            return {
                "url": url,
                "redirect_to": response.headers.get('Location', url),
                "status": response.status_code,
                "note": "Yönlendirme"
            }
        else:
            return {
                "url": url,
                "redirect_to": url,
                "status": response.status_code,
                "note": "" if response.status_code == 200 else "Çözüm İçin Danış"
            }
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout while checking URL: {url}")
        return {
            "url": url,
            "redirect_to": url,
            "status": "Zaman Aşımı",
            "note": "Çözüm İçin Danış"
        }
    except requests.exceptions.ConnectionError:
        logger.warning(f"Connection error while checking URL: {url}")
        return {
            "url": url,
            "redirect_to": url,
            "status": "Bağlantı Hatası",
            "note": "Çözüm İçin Danış"
        }
    except requests.exceptions.RequestException as e:
        logger.warning(f"Request exception for URL {url}: {str(e)}")
        return {
            "url": url,
            "redirect_to": url,
            "status": "Erişilemedi",
            "note": "Çözüm İçin Danış"
        }
    except Exception as e:
        logger.error(f"Unexpected error for URL {url}: {str(e)}")
        return {
            "url": url,
            "redirect_to": url,
            "status": "Hata",
            "note": "Çözüm İçin Danış"
        }

@app.route("/api/check-urls", methods=["POST"])
def check_urls():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "JSON verisi gerekli"}), 400
            
        urls = data.get("urls", [])
        if not urls:
            return jsonify({"error": "En az bir URL gerekli"}), 400
            
        results = [check_url(url) for url in urls[:100]]
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error in check_urls endpoint: {str(e)}")
        return jsonify({"error": "İstek işlenirken bir hata oluştu"}), 500

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "active",
        "service": "HTTP Status Checker API",
        "endpoints": {
            "/api/check-urls": "POST - URL durumlarını kontrol etmek için"
        },
        "usage": "POST isteği ile JSON formatında 'urls' listesi gönderin"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port) 
