# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class EmagCrawlersPipeline:
    def process_item(self, item, spider):
        return item

import psycopg2
import json
import os
from itemadapter import ItemAdapter

class SaveToPSQL:
    def open_spider(self, spider):
        try:
            # Connect to PostgreSQL
            self.conn = psycopg2.connect(
                host="localhost",
                database="Scraped_data",
                user="postgres",
                password="123.qwe"
            )
            self.cursor = self.conn.cursor()
            spider.logger.info("[Postgres] Connected to database successfully")

            self.cursor.execute("CALL create_mouse_data_table(%s)", (None,))
            result = self.cursor.fetchone()
            self.table_name = result[0] if result else None
            self.conn.commit()
            
            if self.table_name:
                spider.logger.info(f"[Postgres] Created/Using table: {self.table_name}")
            else:
                raise Exception("Failed to get table name from procedure")

            # Verify if table exists
            self.cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (self.table_name,))
            table_exists = self.cursor.fetchone()[0]
            spider.logger.info(f"[Postgres] Table {self.table_name} exists: {table_exists}")

            self.failed_items_file = "failed_items.json"
            if not os.path.exists(self.failed_items_file):
                with open(self.failed_items_file, "w") as f:
                    json.dump([], f)

        except Exception as e:
            spider.logger.error(f"[Postgres] Failed to open DB connection: {e}")
            spider.logger.error(f"[Postgres] Exception type: {type(e).__name__}")
            raise e

    def close_spider(self, spider):
        try:
            self.cursor.close()
            self.conn.close()
        except Exception as e:
            spider.logger.error(f"[Postgres] Failed to close DB connection: {e}")

    def process_item(self, item, spider):
        insert_query = f"""
        INSERT INTO {self.table_name} (
            name, url, price, tip,
            interfata_mouse, interfata_receiver,
            tehnologie, culoare
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        try:
            price_str = str(item.get('price')) if item.get('price') is not None else None
            
            self.cursor.execute(insert_query, (
                item.get('name'),
                item.get('URL'),
                price_str,
                item.get('tip'),
                item.get('interfata_mouse'),
                item.get('interfata_receiver'),
                item.get('tehnologie'),
                item.get('culoare')
            ))
            self.conn.commit()
            spider.logger.info(f"[Postgres] Successfully inserted item: {item.get('name')}")

        except Exception as e:
            spider.logger.error(f"[Postgres] Failed to insert item: {e} | Item: {dict(item)}")
            self.conn.rollback()

            try:
                with open(self.failed_items_file, "r+") as f:
                    data = json.load(f)
                    data.append(dict(item))
                    f.seek(0)
                    json.dump(data, f, indent=4)
            except Exception as json_err:
                spider.logger.error(f"[Postgres] Failed to write failed item to JSON: {json_err}")

        return item