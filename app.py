from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your_secret_key'

mysql = MySQL(app)


@app.route('/')
def index():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM Movies')
    movies = cursor.fetchall()
    cursor.close()
    return render_template('index.html', movies=movies)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM Users WHERE username = %s', (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return render_template('register.html', error="Пользователь уже существует.")

        cursor.execute('INSERT INTO Users (username, password) VALUES (%s, %s)', (username, password))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/movie/<int:movie_id>')
def movie(movie_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, title, description, image FROM movies WHERE id = %s", (movie_id,))
    movie = cursor.fetchone()
    cursor.close()

    if movie:
        movie_data = {
            'id': movie[0],
            'title': movie[1],
            'description': movie[2],
            'image': movie[3],  # Здесь мы используем поле image для постера
        }
        return render_template('movie.html', movie=movie_data)
    else:
        return "Фильм не найден", 404


@app.route('/booking/<int:movie_id>', methods=['GET', 'POST'])
def booking(movie_id):
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('register'))

    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        # Получаем выбранные места из скрытого поля
        selected_seats = request.form['seats'].split(',')  # Разделяем номера мест
        for seat in selected_seats:
            cursor.execute('INSERT INTO Bookings (user_id, movie_id, seats) VALUES (%s, %s, %s)',
                           (user_id, movie_id, seat))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('confirm_booking', movie_id=movie_id))

    # Получаем уже забронированные места для данного фильма
    cursor.execute('SELECT seats FROM Bookings WHERE movie_id = %s', (movie_id,))
    booked_seats = cursor.fetchall()
    booked_seats = [seat[0] for seat in booked_seats]  # Получаем список забронированных мест, как список

    cursor.close()
    return render_template('book_seats.html', movie_id=movie_id, booked_seats=booked_seats)


@app.route('/get_booked_seats/<int:movie_id>')
def get_booked_seats(movie_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT seats FROM Bookings WHERE movie_id = %s', (movie_id,))
        booked_seats = cursor.fetchall()
        booked_seats = [seat[0] for seat in booked_seats]  # Преобразуем в простой список
        cursor.close()
        return jsonify(booked_seats)  # Возвращаем данные в формате JSON
    except Exception as e:
        cursor.close()  # Закрываем курсор в случае ошибки
        return jsonify({"error": str(e)}), 500  # Возвращаем ошибку с кодом 500


@app.route('/confirm_booking/<int:movie_id>', methods=['GET', 'POST'])
def confirm_booking(movie_id):
    if request.method == 'POST':
        # Получение выбранных мест из формы
        selected_seats = request.form.get('seats')

        if selected_seats:  # Проверяем, выбраны ли места
            # Здесь должен быть код для сохранения выбранных мест в профиль пользователя или на сервере
            # ...

            return jsonify({"success": True, "seats": selected_seats.split(",")})  # Отправляем выбранные места обратно
        else:
            return jsonify({"success": False, "error": "Вы не выбрали никаких мест."}), 400

    return redirect(url_for('index'))






@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    cursor = mysql.connection.cursor()
    cursor.execute(
        'SELECT Bookings.id, Movies.title, Bookings.seats FROM Bookings JOIN Movies ON Bookings.movie_id = Movies.id WHERE Bookings.user_id = %s',
        (user_id,))
    bookings = cursor.fetchall()
    cursor.close()
    return render_template('profile.html', bookings=bookings)


@app.route('/login', methods=['GET', 'POST'])
def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            cursor = mysql.connection.cursor()
            cursor.execute('SELECT id FROM Users WHERE username = %s AND password = %s', (username, password))
            user = cursor.fetchone()

            if user:
                session['user_id'] = user[0]
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error="Неверное имя пользователя или пароль.")

        return render_template('login.html')


@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    cursor = mysql.connection.cursor()

    # Удаляем запись о бронировании из базы данных
    cursor.execute('DELETE FROM Bookings WHERE id = %s', (booking_id,))
    mysql.connection.commit()  # Подтверждаем изменения в базе данных
    cursor.close()

    return redirect(url_for('profile'))  # Перенаправление обратно на страницу профиля


@app.route('/logout')
def logout():
    session.clear()  # Очистим сессию
    return redirect(url_for('index'))


@app.route('/posters')
def posters():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT id, title, image FROM Movies')  # Или любой нужный вам запрос
    movies = cursor.fetchall()
    cursor.close()
    return render_template('posters.html', movies=movies)


if __name__ == '__main__':
    app.run(debug=True)


