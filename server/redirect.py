from flask import Flask, request, redirect

app = Flask(__name__)

@app.before_request
def before_request():
    return redirect("https://projectargos.ga", code=301)
    """
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
