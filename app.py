
import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
import jdatetime

class StoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("مدیریت فروشگاه پیشرفته")
        self.root.geometry("950x600")
        
        # اتصال به دیتابیس
        try:
            self.conn = psycopg2.connect(
                dbname="mystore",
                user="postgres",
                password="mehrsimakamandloo1381", # لطفاً رمز عبور خود را وارد کنید
                host="127.0.0.1"
            )
            #self.create_tables()
        except Exception as e:
            messagebox.showerror("خطای اتصال به دیتابیس", f"اتصال به دیتابیس ناموفق بود: {e}")
            self.root.destroy()
            return

        self.create_widgets()
        self.load_products()

    def create_tables(self):
        """ایجاد جداول اگر وجود ندارند"""
        cur = self.conn.cursor()
        # ابتدا جداول وابسته و سپس جداول اصلی حذف می‌شوند
        cur.execute("DROP TABLE IF EXISTS sales;")
        cur.execute("DROP TABLE IF EXISTS products;")
        cur.execute("DROP TABLE IF EXISTS categories;")
        
        cur.execute("""
        CREATE TABLE categories (
            category_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT
        );
        """)
        cur.execute("""
        CREATE TABLE products (
            product_id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            stock INTEGER NOT NULL,
            category_id INTEGER REFERENCES categories(category_id)
        );
        """)
        # --- تغییرات در جدول فروش ---
        cur.execute("""
        CREATE TABLE sales (
            id SERIAL PRIMARY KEY,
            product_id INTEGER REFERENCES products(product_id),
            quantity INTEGER NOT NULL,
            buyer_name VARCHAR(100) NOT NULL,
            buyer_family VARCHAR(100) NOT NULL,
            buyer_address TEXT,
            sale_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # درج داده‌های نمونه
        cur.execute("""
        INSERT INTO categories (name, description) VALUES 
        ('موبایل', 'گوشی‌های هوشمند'),
        ('لپ‌تاپ', 'لپ‌تاپ‌های اداری و گیمینگ');
        """)

        cur.execute("""
        INSERT INTO products (name, price, stock, category_id) VALUES
        ('گوشی شیائومی', 8000000, 50, 1),
        ('لپ‌تاپ ایسوس', 45000000, 15, 2);
        """)

        self.conn.commit()
        cur.close()

    def create_widgets(self):
        """ایجاد رابط کاربری"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(main_frame, columns=('ID', 'Name', 'Price', 'Stock'), show='headings')
        self.tree.heading('ID', text='شناسه')
        self.tree.heading('Name', text='نام محصول')
        self.tree.heading('Price', text='قیمت (تومان)')
        self.tree.heading('Stock', text='موجودی')
        self.tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="بارگذاری مجدد", command=self.load_products).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="افزودن محصول", command=self.add_product_dialog).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="ثبت فروش", command=self.sale_dialog).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="گزارش فروش", command=self.show_sales_report).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="خروج", command=self.root.quit).pack(side=tk.LEFT)

    def load_products(self):
        """بارگذاری محصولات از دیتابیس"""
        for item in self.tree.get_children():


            self.tree.delete(item)
       
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT product_id, name, price, stock FROM products ORDER BY product_id")
            for product in cur.fetchall():
                self.tree.insert('', tk.END, values=product)
            cur.close()
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در بارگذاری محصولات: {e}")

    def add_product_dialog(self):
        """پنجره افزودن محصول جدید"""
        self.dialog = tk.Toplevel(self.root)
        self.dialog.title("افزودن محصول جدید")
        self.dialog.resizable(False, False)

        ttk.Label(self.dialog, text="نام محصول:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.name_entry = ttk.Entry(self.dialog, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.dialog, text="قیمت:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.price_entry = ttk.Entry(self.dialog, width=30)
        self.price_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.dialog, text="موجودی اولیه:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.stock_entry = ttk.Entry(self.dialog, width=30)
        self.stock_entry.grid(row=2, column=1, padx=5, pady=5)

        btn_frame = ttk.Frame(self.dialog)
        btn_frame.grid(row=3, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="ذخیره", command=self.save_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="انصراف", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def save_product(self):
        """ذخیره محصول جدید در دیتابیس"""
        try:
            name = self.name_entry.get()
            price = float(self.price_entry.get())
            stock = int(self.stock_entry.get()) if self.stock_entry.get() else 0

            if not name:
                raise ValueError("نام محصول نمی‌تواند خالی باشد")

            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO products (name, price, stock, category_id) VALUES (%s, %s, %s, %s)",
                (name, price, stock, 1) # category_id به صورت نمونه 1 در نظر گرفته شده
            )
            self.conn.commit()
            self.load_products()
            self.dialog.destroy()
            messagebox.showinfo("موفق", "محصول با موفقیت اضافه شد!")
        except ValueError as e:
            messagebox.showerror("خطا", f"مقدار نامعتبر: {e}")
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("خطا", f"مشکل در ذخیره محصول: {e}")

    def sale_dialog(self):
        """پنجره ثبت فروش با اطلاعات خریدار"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("اخطار", "لطفاً یک محصول را انتخاب کنید")
            return

        product_id, name, price, stock = self.tree.item(selected[0])['values']
        
        self.sale_win = tk.Toplevel(self.root)
        self.sale_win.title(f"ثبت فروش برای {name}")
        
        frame = ttk.Frame(self.sale_win, padding="10")
        frame.pack(padx=10, pady=10)

        # اطلاعات محصول
        ttk.Label(frame, text=f"محصول: {name}").grid(row=0, column=0, columnspan=2, pady=2, sticky=tk.E)
        ttk.Label(frame, text=f"موجودی فعلی: {stock}").grid(row=1, column=0, columnspan=2, pady=2, sticky=tk.E)

        # --- فیلدهای جدید برای اطلاعات خریدار ---
        ttk.Label(frame, text="تعداد فروش:").grid(row=2, column=0, pady=5, sticky=tk.W)
        self.quantity_entry = ttk.Entry(frame)
        self.quantity_entry.grid(row=2, column=1, pady=5)

        ttk.Label(frame, text="نام خریدار:").grid(row=3, column=0, pady=5, sticky=tk.W)
        self.buyer_name_entry = ttk.Entry(frame)
        self.buyer_name_entry.grid(row=3, column=1, pady=5)

        ttk.Label(frame, text="نام خانوادگی خریدار:").grid(row=4, column=0, pady=5, sticky=tk.W)
        self.buyer_family_entry = ttk.Entry(frame)
        self.buyer_family_entry.grid(row=4, column=1, pady=5)


        ttk.Label(frame, text="آدرس:").grid(row=5, column=0, pady=5, sticky=tk.W)
        self.buyer_address_entry = ttk.Entry(frame)
        self.buyer_address_entry.grid(row=5, column=1, pady=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=6, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="ثبت فروش", 
                 command=lambda: self.record_sale(product_id)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="انصراف", 
                 command=self.sale_win.destroy).pack(side=tk.LEFT, padx=5)

    def record_sale(self, product_id):
        """ثبت فروش در دیتابیس با اطلاعات خریدار"""
        try:
            quantity = int(self.quantity_entry.get())
            buyer_name = self.buyer_name_entry.get()
            buyer_family = self.buyer_family_entry.get()
            buyer_address = self.buyer_address_entry.get()

            if quantity <= 0:
                raise ValueError("تعداد باید بیشتر از صفر باشد")
            if not buyer_name or not buyer_family:
                raise ValueError("نام و نام خانوادگی خریدار الزامی است")

            cur = self.conn.cursor()
            
            cur.execute("SELECT stock FROM products WHERE product_id = %s FOR UPDATE", (product_id,))
            stock = cur.fetchone()[0]
            
            if quantity > stock:
                raise ValueError("موجودی کافی نیست")
            
            # --- به‌روزرسانی دستور INSERT برای جدول sales ---
            cur.execute(
                """INSERT INTO sales (product_id, quantity, buyer_name, buyer_family, buyer_address) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (product_id, quantity, buyer_name, buyer_family, buyer_address)
            )
            
            cur.execute(
                "UPDATE products SET stock = stock - %s WHERE product_id = %s",
                (quantity, product_id)
            )
            
            self.conn.commit()
            self.sale_win.destroy()
            self.load_products()
            messagebox.showinfo("موفق", "فروش با موفقیت ثبت شد!")
            
        except ValueError as e:
            messagebox.showerror("خطا", f"مقدار نامعتبر: {e}")
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("خطا", f"مشکل در ثبت فروش: {e}")
        finally:
            if 'cur' in locals() and not cur.closed:
                cur.close()

    def show_sales_report(self):
        """نمایش گزارش دقیق فروش با اطلاعات خریدار"""
        report_win = tk.Toplevel(self.root)
        report_win.title("گزارش جامع فروش")
        report_win.geometry("900x400")
        
        try:
            cur = self.conn.cursor()
            # --- کوئری برای گزارش دقیق ---
            cur.execute("""
                SELECT 
                    s.id,
                    p.name, 
                    s.quantity, 
                    p.price,
                    (s.quantity * p.price) as total,
                    s.buyer_name,
                    s.buyer_family,
                    s.sale_date
                FROM sales s
                JOIN products p ON s.product_id = p.product_id
                ORDER BY s.sale_date DESC
            """)
            sales_data = cur.fetchall()

            cols = ('ID', 'Product', 'Quantity', 'Price', 'Total', 'BuyerName', 'BuyerFamily', 'SaleDate')
            tree = ttk.Treeview(report_win, columns=cols, show='headings')
            
            tree.heading('ID', text='کد فروش')
            tree.heading('Product', text='محصول')
            tree.heading('Quantity', text='تعداد')
            tree.heading('Price', text='قیمت واحد')
            tree.heading('Total', text='مبلغ کل')
            tree.heading('BuyerName', text='نام خریدار')
            tree.heading('BuyerFamily', text='فامیلی خریدار')
            tree.heading('SaleDate', text='تاریخ و ساعت فروش')

            tree.column('ID', width=60)
            tree.column('Quantity', width=50, anchor=tk.CENTER)
            
            for row in sales_data:
                # تبدیل تاریخ میلادی به شمسی
                sale_datetime_utc = row[7]
                jalali_date = jdatetime.datetime.fromgregorian(datetime=sale_datetime_utc)
                formatted_date = jalali_date.strftime('%Y/%m/%d %H:%M:%S')
                
                # ایجاد یک تاپل جدید با تاریخ فرمت‌شده
                display_row = row[:-1] + (formatted_date,)
                tree.insert('', tk.END, values=display_row)

            tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        except Exception as e:
            messagebox.showerror("خطا", f"مشکل در دریافت گزارش: {e}")
        finally:
            if 'cur' in locals() and not cur.closed:
                cur.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = StoreApp(root)
    root.mainloop()
if __name__ == "__main__":
    print("برنامه در حال شروع است")
root = tk.Tk()
app = StoreApp(root)
print("پنجره باید نمایش داده شود")
root.mainloop()
print("برنامه بسته شد")

