import mysql.connector
from datetime import datetime

config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'hotel'
}


def IsAvailable(room_number):
    try:
        cursor.execute("SELECT IsOcp FROM room WHERE RoomNumber = %s", (room_number,))
        result = cursor.fetchone()
        if not result:
            print("Camera nu există!")
            return False
        if result[0]:
            print("Camera este deja ocupată!")
            return False
        return True
    except mysql.connector.Error as err:
        print(f"Eroare la verificarea disponibilității: {err}")
        return False


def Close():
    try:
        cursor.execute("UPDATE room SET IsOcp = 0")
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Eroare la resetarea stării camerelor: {err}")
    finally:
        if 'conn' in globals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Conexiunea la baza de date a fost închisă.")



try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    print("Conectat cu succes la baza de date!")
except mysql.connector.Error as err:
    print(f"Eroare: {err}")
    exit(1)


def MainMenu():
    while True:
        print("\n-* Bun venit la PythonHotel *-")
        print("1.Rezervare noua.")
        print("2.Lista camere disponibile.")
        print("0.Iesire.")
        mainmenu = input("Introduceti cifra corespunzatoare serviciului: ")

        if mainmenu == "1":
            ClientExistent()
        elif mainmenu == "2":
            AvailableRooms()
        elif mainmenu == "0":
            Close()
            break
        else:
            print("Optiune invalida!")


def InsertGuest():
    try:
        prenume = input("Prenume: ")
        nume = input("Nume: ")
        add_guest = ("INSERT INTO guest "
                     "(FirstName,LastName,Street, City,Country,Zip,Phone) "
                     "VALUES (%s, %s, %s, %s, %s, %s, %s)")
        data_guest = (prenume, nume, input("Strada: "), input("Oras:"),
                      input("Tara:"), input("Cod postal:"), input("Nr. tel:"))
        cursor.execute(add_guest, data_guest)
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Eroare la inserarea oaspetelui: {err}")
        return False


def TotalCalculator(room_number, check_in, check_out):
    try:
        cursor.execute("SELECT BasePrice FROM room WHERE RoomNumber = %s", (room_number,))
        result = cursor.fetchone()
        if not result:
            print("Camera nu există!")
            return None

        base_price = result[0]
        date_in = datetime.strptime(check_in, "%Y-%m-%d").date()
        date_out = datetime.strptime(check_out, "%Y-%m-%d").date()
        nights = (date_out - date_in).days

        if nights <= 0:
            print("Data de check-out trebuie să fie după data de check-in!")
            return None

        total_price = base_price * nights
        return total_price, nights, base_price

    except mysql.connector.Error as err:
        print(f"Eroare la calcularea prețului: {err}")
        return None


def InsertReservation():
    try:
        room_number = int(input("Număr cameră: "))
        if not IsAvailable(room_number):
            return False

        adults = int(input("Nr. adulți: "))
        children = int(input("Nr. copii: "))
        check_in_date = input("Data check-in (YYYY-MM-DD): ")
        check_out_date = input("Data check-out (YYYY-MM-DD): ")

        price_calc = TotalCalculator(room_number, check_in_date, check_out_date)
        if not price_calc:
            return False

        total, nights, price_per_night = price_calc
        print(f"\nDetalii rezervare:")
        print(f"Preț pe noapte: {price_per_night} RON")
        print(f"Număr nopți: {nights}")
        print(f"Total de plată: {total} RON")

        if input("\nConfirmați rezervarea (da/nu): ").lower() != 'da':
            return False

        add_reservation = ("INSERT INTO reservation "
                           "(Adults, Children, CheckInDate, CheckOutDate, Total) "
                           "VALUES (%s, %s, %s, %s, %s)")
        data_reservation = (adults, children, check_in_date, check_out_date, total)

        cursor.execute(add_reservation, data_reservation)
        conn.commit()
        return True

    except ValueError:
        print("Format invalid pentru date sau numere!")
        return False
    except mysql.connector.Error as err:
        print(f"Eroare la inserarea rezervării: {err}")
        conn.rollback()
        return False


def LinkReservationToGuest():
    try:
        prenume = input("Prenume: ")
        nume = input("Nume: ")

        cursor.execute("SELECT GuestId FROM guest WHERE FirstName = %s AND LastName = %s", (prenume, nume))
        guest_result = cursor.fetchall()
        if not guest_result:
            print("Oaspetele nu a fost găsit!")
            return False

        gid = guest_result[0][0]

        cursor.execute("SELECT MAX(ReservationID) FROM reservation")
        reservation_result = cursor.fetchall()
        if not reservation_result or reservation_result[0][0] is None:
            print("Nu există nicio rezervare!")
            return False

        rid = reservation_result[0][0]

        cursor.execute("INSERT INTO guestreservation (GuestId, ReservationId) VALUES (%s, %s)", (gid, rid))
        cursor.fetchall()
        conn.commit()

        print("Rezervarea a fost legată cu succes de oaspete!")
        return True

    except mysql.connector.Error as err:
        print(f"Eroare la legarea rezervării de oaspete: {err}")
        conn.rollback()
        return False


def ReservationDates(reservation_id):
    try:
        cursor.execute("""
            SELECT CheckInDate, CheckOutDate 
            FROM reservation 
            WHERE ReservationId = %s
        """, (reservation_id,))
        return cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Eroare la obținerea datelor rezervării: {err}")
        return None


def RoomStatus(room_number, reservation_id):
    try:
        dates = ReservationDates(reservation_id)
        if not dates:
            return False

        check_in_date, check_out_date = dates

        cursor.execute("UPDATE room SET IsOcp = 1 WHERE RoomNumber = %s", (room_number,))

        cursor.execute("""
            CREATE EVENT IF NOT EXISTS room_checkout_%s_%s
            ON SCHEDULE AT %s
            DO
            UPDATE room SET IsOcp = 0 WHERE RoomNumber = %s
        """, (room_number, reservation_id, check_out_date, room_number))

        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Eroare la programarea actualizării stării camerei: {err}")
        conn.rollback()
        return False


def LinkRoomToReservation():
    try:
        camera = int(input("Nr. camera: "))

        if not IsAvailable(camera):
            return False

        cursor.execute("SELECT MAX(ReservationID) FROM reservation")
        reservation_result = cursor.fetchone()
        if not reservation_result or reservation_result[0] is None:
            print("Nu există nicio rezervare!")
            return False
        rid = reservation_result[0]

        cursor.execute("INSERT INTO roomreservation (RoomNumber, ReservationId) VALUES (%s, %s)",
                       (camera, rid))

        if not RoomStatus(camera, rid):
            conn.rollback()
            return False

        conn.commit()
        print("Rezervarea a fost legată cu succes de camera!")
        return True

    except mysql.connector.Error as err:
        print(f"Eroare la legarea rezervării de camera: {err}")
        conn.rollback()
        return False
    except ValueError:
        print("Numărul camerei trebuie să fie un număr întreg!")
        return False


def ClientExistent():
    raspuns = input("Ati mai facut rezervari la noi? (da/nu): ").lower()
    if raspuns == 'nu':
        if InsertGuest() and InsertReservation():
            LinkReservationToGuest()
            LinkRoomToReservation()
    elif raspuns == 'da':
        if InsertReservation():
            LinkReservationToGuest()
            LinkRoomToReservation()
    else:
        print("Raspuns invalid!")


def AvailableRooms():
    try:
        cursor.execute("""
            SELECT RoomNumber, RoomType, BasePrice, StandardOccupancy 
            FROM room 
            WHERE IsOcp = 0 
            ORDER BY RoomNumber
        """)
        rooms = cursor.fetchall()

        if not rooms:
            print("Nu există camere disponibile momentan!")
            return

        print("\nCamere disponibile:")
        print("Nr. Camera | Tip Camera | Preț | Capacitate")
        print("-" * 45)

        for room in rooms:
            print(f"{room[0]:^10} | {room[1]:^10} | {room[2]:^6.2f} | {room[3]:^10}")

    except mysql.connector.Error as err:
        print(f"Eroare la obținerea listei de camere: {err}")


MainMenu()
