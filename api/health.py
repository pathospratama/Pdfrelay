from flask import jsonify

def handler(request):
    return jsonify({
        "status": "healthy",
        "service": "PDF Text Replacer",
        "version": "1.0"
    }), 200