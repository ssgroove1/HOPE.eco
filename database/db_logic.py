import sqlite3

class DB_Manager:
    def __init__(self, database):
        self.database = database
        self.create_tables()

    def create_tables(self):
        conn = sqlite3.connect(self.database, timeout=10)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS user_balance (
                                user_id INTEGER PRIMARY KEY,
                                points INTEGER DEFAULT 0,
                                last_claim REAL DEFAULT 0,
                                last_water REAL DEFAULT 0,
                                last_collect REAL DEFAULT 0,
                                last_fish REAL DEFAULT 0,
                                last_bonus REAL DEFAULT 0,
                                last_rob REAL DEFAULT 0)''')
            conn.commit()

    # The Economic
    async def get_user_economic(self, user_id):
        conn = None
        try:
            conn = sqlite3.connect(self.database, timeout=5)
            conn.execute("PRAGMA journal_mode=WAL")
            cursor = conn.cursor()
            cursor.execute("SELECT points, last_claim, last_water, last_collect, last_fish, last_bonus, last_rob FROM user_balance WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row is None:
                cursor.execute("INSERT INTO user_balance (user_id) VALUES (?)", (user_id,))
                conn.commit()
                row = (0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
            conn.close()
            return {
                "points": row[0], 
                "last_claim": row[1],
                "last_water": row[2],
                "last_collect": row[3],
                "last_fish": row[4],
                "last_bonus": row[5],
                "last_rob": row[6]
            }
        except sqlite3.OperationalError as e:
            print(f"⚠️ Ошибка БД в get_user_economic: {e}")
            return None
        except Exception as e:
            print(f"❌ Другая ошибка: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    async def update_user_economic(self, user_id, points, last_claim, last_water, last_collect, last_fish, last_bonus, last_rob):
        conn = sqlite3.connect(self.database, timeout=10)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE user_balance 
            SET points = ?, last_claim = ?, last_water = ?, last_collect = ?, last_fish = ?, last_bonus = ?, last_rob = ?
            WHERE user_id = ?
        """, (points, last_claim, last_water, last_collect, last_fish, last_bonus, last_rob, user_id))
        conn.commit()
        conn.close()

    def get_leaderboard(self, limit=10):
        conn = sqlite3.connect(self.database, timeout=10)
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT user_id, points 
            FROM user_balance 
            WHERE points > 0 
            ORDER BY points DESC 
            LIMIT ?""",
            (limit,)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        return rows

    def get_user_rank(self, user_id):
        conn = sqlite3.connect(self.database, timeout=10)

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*)
                FROM user_balance
                WHERE points > 0
                AND (
                    points > (
                        SELECT points
                        FROM user_balance
                        WHERE user_id = ?
                    )
                    OR (
                        points = (
                            SELECT points
                            FROM user_balance
                            WHERE user_id = ?
                        )
                        AND user_id < ?
                    )
                )
            """, (user_id, user_id, user_id))

            rank = cursor.fetchone()[0]

            # Пользователь не найден или у него 0 валюты
            cursor.execute(
                "SELECT points FROM user_balance WHERE user_id = ?",
                (user_id,)
            )

            row = cursor.fetchone()

            if row is None or row[0] <= 0:
                return None

            return rank + 1

        finally:
            conn.close()

if __name__ == '__main__':
    manager = DB_Manager('database\\econ_hope.db')