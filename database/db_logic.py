import sqlite3

class DB_Manager:
    def __init__(self, database):
        self.database = database
        self.create_tables()

    # ! Почистить и расположить всё в DB_LOGIC
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
                                last_rob REAL DEFAULT 0,
                                container_count INTEGER DEFAULT 0)''')
            conn.execute("""CREATE TABLE IF NOT EXISTS role_shop (
                                role_id INTEGER PRIMARY KEY,
                                price INTEGER NOT NULL)""")
            conn.commit()

    # LOGIC: Запись пользователя в БД и получение его данных из БД
    async def ensure_user(self, user_id: int) -> bool:
        conn = None
        try:
            conn = sqlite3.connect(
                self.database,
                timeout=10
            )
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO user_balance (
                    user_id
                )
                VALUES (?)
            """, (user_id,))
            conn.commit()
            return True

        except sqlite3.Error as error:
            print(
                f"❌ Ошибка БД в ensure_user: "
                f"{type(error).__name__}: {error}"
            )
            return False
        except Exception as error:
            print(
                f"❌ Непредвиденная ошибка в ensure_user: "
                f"{type(error).__name__}: {error}"
            )
            return False
        finally:
            if conn is not None:
                conn.close()

    async def get_user_economic(self, user_id: int):
        conn = None
        try:
            # LOGIC: Гарантируем наличие пользователя в БД
            created = await self.ensure_user(user_id)
            if not created:
                return None
            
            conn = sqlite3.connect(
                self.database,
                timeout=10
            )
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    points,
                    last_claim,
                    last_water,
                    last_collect,
                    last_fish,
                    last_bonus,
                    last_rob,
                    container_count
                FROM user_balance
                WHERE user_id = ?
            """, (user_id,))

            row = cursor.fetchone()
            if row is None:
                print(
                    f"⚠️ Пользователь {user_id} "
                    f"не найден после ensure_user()."
                )
                return None
            return {
                "points": row["points"],
                "last_claim": row["last_claim"],
                "last_water": row["last_water"],
                "last_collect": row["last_collect"],
                "last_fish": row["last_fish"],
                "last_bonus": row["last_bonus"],
                "last_rob": row["last_rob"],
                "container_count": row["container_count"]
            }

        except sqlite3.Error as error:
            print(
                f"❌ Ошибка БД в get_user_economic: "
                f"{type(error).__name__}: {error}"
            )
            return None
        except Exception as error:
            print(
                f"❌ Непредвиденная ошибка в get_user_economic: "
                f"{type(error).__name__}: {error}"
            )
            return None
        finally:
            if conn is not None:
                conn.close()

    # ! Будет убрано в будущем, так как не используется
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

    # LOGIC: Добавление валюты пользователю
    async def add_points(self, user_id: int, points: int):
        conn = sqlite3.connect(self.database, timeout=10)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE user_balance
                SET points = points + ?
                WHERE user_id = ?
            """, (points, user_id))
            conn.commit()
        finally:
            conn.close()

    # LOGIC: Данные для контейнеров
    async def update_count_containers(self, user_id):
        conn = sqlite3.connect(self.database, timeout=10)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE user_balance
                SET container_count = container_count + 1
                WHERE user_id = ?
            """, (user_id,))
            conn.commit()
        finally:
            conn.close()

    def add_container_count_column(self):
            conn = sqlite3.connect(self.database, timeout=10)
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    ALTER TABLE user_balance
                    ADD COLUMN container_count INTEGER DEFAULT 0
                """)
                conn.commit()
            finally:
                conn.close()

    # LOGIC: Данные для магазина ролей
    async def shop_role_exists(self, role_id: int) -> bool:
        conn = sqlite3.connect(self.database, timeout=10)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM role_shop WHERE role_id = ?",
                (role_id,)
            )
            return cursor.fetchone() is not None
        finally:
            conn.close()

    async def can_add_shop_role(self, role_id: int):
        conn = sqlite3.connect(self.database, timeout=10)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM role_shop WHERE role_id = ?",
                (role_id,)
            )
            if cursor.fetchone():
                return "exists"
            cursor.execute("SELECT COUNT(*) FROM role_shop")
            count = cursor.fetchone()[0]
            if count >= 25:
                return "limit"
            return "success"
        finally:
            conn.close()

    async def add_shop_role(self, role_id: int, price: int):
        conn = sqlite3.connect(self.database, timeout=10)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO role_shop (role_id, price)
                VALUES (?, ?)
            """, (role_id, price))
            conn.commit()
        finally:
            conn.close()

    async def remove_shop_role(self, role_id: int) -> bool:
        conn = sqlite3.connect(self.database, timeout=10)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM role_shop
                WHERE role_id = ?
            """, (role_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
        finally:
            conn.close()

    async def get_shop_roles(self):
        conn = sqlite3.connect(self.database, timeout=10)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role_id, price
                FROM role_shop
                ORDER BY price ASC
            """)
            rows = cursor.fetchall()
            if not rows:
                return None
            return rows
        finally:
            conn.close()

    async def buy_shop_role(self, user_id: int, role_id: int):
        conn = sqlite3.connect(self.database, timeout=10)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT price
                FROM role_shop
                WHERE role_id = ?
            """, (role_id,))
            role_data = cursor.fetchone()
            if role_data is None:
                return {
                    "success": False,
                    "reason": "role_not_found",
                }
            price = role_data[0]
            cursor.execute("""
                SELECT points
                FROM user_balance
                WHERE user_id = ?
            """, (user_id,))
            user_data = cursor.fetchone()
            if user_data is None:
                return {
                    "success": False,
                    "reason": "user_not_found",
                }
            points = user_data[0]
            if points < price:
                return {
                    "success": False,
                    "reason": "not_enough_points",
                    "points": points,
                    "price": price,
                }
            # Сколько потратил пользователь
            points_spent = price
            # Сколько валюты осталось
            new_points = points - points_spent
            cursor.execute("""
                UPDATE user_balance
                SET points = ?
                WHERE user_id = ?
            """, (new_points, user_id))
            conn.commit()
            return {
                "success": True,
                "points_spent": points_spent,
                "new_points": new_points,
            }
        except sqlite3.Error as error:
            conn.rollback()
            print(
                f"❌ Ошибка покупки роли: "
                f"{type(error).__name__}: {error}"
            )
            return {
                "success": False,
                "reason": "database_error",
            }
        finally:
            conn.close()

    # LOGIC: Данные лидерборда
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
