from flask import Flask, render_template

app = Flask(__name__)

# Пример данных для личного кабинета. Потом заменишь данными из БД / после логина.
SAMPLE_USER = {
    "name": "Name Surname",
    "initials": "NS",
    "email": "email@example.com",
    "phone": "+00 000 000 000",
    "city": "City",
    "since": "Month YYYY",
}
SAMPLE_ORDERS = [
    {"number": "#1042", "date": "2026-11-12", "items": "Studio headphones", "total": 459.00, "status": "Delivered"},
    {"number": "#1037", "date": "2026-10-28", "items": 'TV 55" 4K Ultra HD', "total": 2199.00, "status": "Shipped"},
    {"number": "#1019", "date": "2026-09-03", "items": "Mini drone for beginners", "total": 599.00, "status": "Delivered"},
]


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/shop")
def catalog():
    return render_template("index.html")


@app.route("/product/<int:product_id>")
def product(product_id):
    return render_template("product.html", product_id=product_id)


@app.route("/account")
def account():
    return render_template("account.html", user=SAMPLE_USER, orders=SAMPLE_ORDERS)


@app.route("/admin")
def admin():
    return render_template("admin.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
