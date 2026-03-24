-- Crearea bazei de date
CREATE DATABASE IF NOT EXISTS hotel;
USE hotel;

-- Tabelul pentru oaspeți (extras din InsertGuest)
CREATE TABLE IF NOT EXISTS guest (
    GuestId INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Street VARCHAR(100),
    City VARCHAR(50),
    Country VARCHAR(50),
    Zip VARCHAR(20),
    Phone VARCHAR(20)
);

-- Tabelul pentru camere (extras din AvailableRooms și IsAvailable)
CREATE TABLE IF NOT EXISTS room (
    RoomNumber INT PRIMARY KEY,
    RoomType VARCHAR(50),
    BasePrice DECIMAL(10, 2),
    StandardOccupancy INT,
    IsOcp TINYINT(1) DEFAULT 0
);

-- Tabelul pentru rezervări (extras din InsertReservation)
CREATE TABLE IF NOT EXISTS reservation (
    ReservationId INT AUTO_INCREMENT PRIMARY KEY,
    Adults INT,
    Children INT,
    CheckInDate DATE,
    CheckOutDate DATE,
    Total DECIMAL(10, 2)
);

-- Tabel de legătură Oaspeți - Rezervări (extras din LinkReservationToGuest)
CREATE TABLE IF NOT EXISTS guestreservation (
    GuestId INT,
    ReservationId INT,
    PRIMARY KEY (GuestId, ReservationId),
    FOREIGN KEY (GuestId) REFERENCES guest(GuestId),
    FOREIGN KEY (ReservationId) REFERENCES reservation(ReservationId)
);

-- Tabel de legătură Camere - Rezervări (extras din LinkRoomToReservation)
CREATE TABLE IF NOT EXISTS roomreservation (
    RoomNumber INT,
    ReservationId INT,
    PRIMARY KEY (RoomNumber, ReservationId),
    FOREIGN KEY (RoomNumber) REFERENCES room(RoomNumber),
    FOREIGN KEY (ReservationId) REFERENCES reservation(ReservationId)
);

-- Activarea Scheduler-ului pentru evenimentele de check-out (folosit în RoomStatus)
SET GLOBAL event_scheduler = ON;

-- Exemplu de inserare date inițiale pentru camere (opțional)
INSERT INTO room (RoomNumber, RoomType, BasePrice, StandardOccupancy, IsOcp) VALUES 
(101, 'Single', 150.00, 1, 0),
(102, 'Double', 250.00, 2, 0),
(201, 'Suite', 500.00, 4, 0);
