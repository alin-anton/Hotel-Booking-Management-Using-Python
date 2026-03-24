# Hotel Booking Management System

A Python-based application for managing hotel reservations using a MySQL database to store and process guest, room, and booking information.

## 🚀 Key Features

* **Guest Management**: Register new guests with detailed information including name, address, and phone number.
* **Reservation System**:
    * **Availability Check**: Automatically verifies if a room is occupied before allowing a new booking.
    * **Price Calculation**: Calculates the total cost based on the number of nights and the room's base price.
    * **Integrated Linking**: Links reservations to both guests and specific rooms in the database.
* **Room Management**:
    * View a detailed list of available rooms, including type, price, and occupancy limits.
    * **Status Automation**: Updates room status to "Occupied" (IsOcp = 1) upon booking.
    * **Cleanup**: Resets all room statuses to "Available" when the application is closed.

## 🛠️ Technologies Used

* **Python 3.x**
* **MySQL** (Database)
* **mysql-connector-python**

## 📋 Prerequisites & Installation

1.  **Install Dependencies**:
    ```bash
    pip install mysql-connector-python
    ```

2.  **Database Setup (Import)**:
    * Open your MySQL management tool (like MySQL Workbench, phpMyAdmin, or terminal).
    * Create a database named `hotel`:
      ```sql
      CREATE DATABASE hotel;
      ```
    * Import the provided `database.sql` file (or the SQL code provided) to create all necessary tables and structures.
    * Update the `config` dictionary in `DataBase.py` with your local credentials (host, user, password).

## 💻 Usage

To launch the application, run:
```bash
python DataBase.py
```
## 🏨 Main Menu Options:
* New Reservation: Starts the ClientExistent() flow, which checks if the user is a returning guest and processes the booking.

* List Available Rooms: Displays all rooms where IsOcp = 0.

* Exit: Resets room statuses to 0, closes the database connection, and exits the program.
