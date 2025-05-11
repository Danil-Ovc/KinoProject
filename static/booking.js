const selectedSeats = [];

function toggleSeat(seat) {
    const seatElement = document.getElementById(seat);

    // Проверяем, забронировано ли место
    if (seatElement.classList.contains('booked')) {
        alert('Это место уже забронировано.');
        return; // Не можем выбрать забронированное место
    }

    // Добавляем или убираем выбранное состояние
    seatElement.classList.toggle('selected');

    if (selectedSeats.includes(seat)) {
        selectedSeats.splice(selectedSeats.indexOf(seat), 1); // Убираем из выбранных
    } else {
        selectedSeats.push(seat); // Добавляем в выбранные
    }

    // Обновляем скрытое поле и отображаем выбранные места
    document.getElementById('hidden_seats').value = selectedSeats.join(',');
    document.getElementById('selected_seats').innerText = selectedSeats.join(', ');
}

function updateBookedSeats(movieId) {
    console.log("Updating booked seats for movie ID:", movieId);

    fetch(`/get_booked_seats/${movieId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(bookedSeats => {
            const uniqueBookedSeats = [...new Set(bookedSeats)]; // Убираем дубликаты
            console.log("Unique booked seats:", uniqueBookedSeats);

            document.querySelectorAll('.seat').forEach(seat => {
                seat.classList.remove('booked');
                // Проверяем, если текущий ID места есть в забронированных местах
                if (uniqueBookedSeats.includes(String(seat.id))) {
                    seat.classList.add('booked');
                }
            });
        })
        .catch(error => console.error('Error fetching booked seats:', error));
}

// Обновление мест при загрузке страницы и каждые 5 секунд
document.addEventListener("DOMContentLoaded", function() {
    const movieIdElement = document.getElementById('movie_id');

    if (!movieIdElement) {
        console.error("Element with id 'movie_id' not found!");
        return;
    }

    const movieId = movieIdElement.value;
    updateBookedSeats(movieId); // Вызовете функцию здесь

    setInterval(() => updateBookedSeats(movieId), 5000); // Обновляем места каждые 5 секунд
});







