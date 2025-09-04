# /home/buddyskincare/BuddySkincare/import_data.py
import os
import django
import pandas as pd
from decimal import Decimal

# Cấu hình môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuddyProject.settings')
django.setup()

# Import models sau khi đã setup Django
from BuddyApp.models import Product, Brand, Category, Tag, Gift
from django.db import IntegrityError

def import_products_from_excel(file_path):
    """
    Nhập dữ liệu sản phẩm từ file CSV vào database Django.
    """
    
    status_mapping = {
        'Used test': 'test',
        'Used 95%': '95',
        'New': 'new',
        'New rách tem': 'newrt',
        'New xước': 'newx',
        'New mất hộp': 'newmh',
        'Used 90%': '90',
        'New móp hộp nhẹ': 'newmn',
        # Không có mã 'newxn' trong PRODUCT_STATUS_CHOICES → ánh xạ về 'newx'
        'New xước nhẹ': 'newx',
        'Chiết': 'chiet',
        'new': 'new',
        'new rách tem': 'newrt',
    }

    # Đọc Excel thay vì CSV (file Sanpham.xlsx là Excel)
    try:
        print("Đang đọc file dữ liệu (Excel)...")
        df = pd.read_excel(file_path)
        print(f"Đã đọc thành công {len(df)} dòng dữ liệu từ Excel.")
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file tại đường dẫn: {file_path}")
        return
    except Exception as e:
        print(f"Đã xảy ra lỗi khi đọc file Excel: {e}")
        print("Vui lòng kiểm tra sheet, tên cột và định dạng file .xlsx.")
        return

    # Chuẩn hoá tên cột để tránh khác biệt hoa/thường/khoảng trắng
    normalized_columns = {str(c).strip().lower(): c for c in df.columns}

    def col(name_vn_lower: str):
        if name_vn_lower in normalized_columns:
            return normalized_columns[name_vn_lower]
        # Không tìm thấy cột → raise để báo rõ ràng
        raise KeyError(f"Thiếu cột bắt buộc trong Excel: '{name_vn_lower}'")

    def clean_int(value, default=0):
        try:
            if pd.isna(value):
                return default
            # Cho phép chuỗi có dấu phẩy/chấm
            if isinstance(value, str):
                digits = ''.join(ch for ch in value if ch.isdigit())
                return int(digits) if digits != '' else default
            if isinstance(value, (int, float)):
                return int(round(value))
            if isinstance(value, Decimal):
                return int(value)
            return default
        except Exception:
            return default

    # Lặp qua từng dòng để tạo hoặc cập nhật đối tượng Product
    for index, row in df.iterrows():
        try:
            # Lấy các đối tượng liên kết
            brand = Brand.objects.get(id=row[col('hãng')])
            category = Category.objects.get(id=row[col('danh mục')])
            
            # Xử lý các trường có thể bị rỗng
            stock_quantity = clean_int(row.get(col('số lượng kho'), 0), 0)
            sold_quantity = clean_int(row.get(col('đã bán'), 0), 0)
            # rating để dạng Decimal 1 chữ số thập phân theo model
            rating_val = row.get(col('số sao'), None)
            rating = Decimal(str(rating_val)) if pd.notna(rating_val) else Decimal('0.0')
            # Model dùng IntegerField (nghìn đồng) → ép về int
            import_price = clean_int(row.get(col('giá nhập'), 0), 0)
            original_price = clean_int(row.get(col('giá gốc'), 0), 0)
            discounted_price = clean_int(row.get(col('giá bán'), 0), 0)
            
            # Lấy các Tag
            tags = []
            if pd.notna(row.get(col('tag flash sale'))):
                tag_ids = str(row.get(col('tag flash sale'))).split(',')
                for tag_id in tag_ids:
                    if tag_id.strip():
                        tags.append(Tag.objects.get(id=int(tag_id)))
            
            # Lấy các Gift (nếu cột này tồn tại trong file CSV)
            gifts = []
            if 'quà tặng' in normalized_columns and pd.notna(row.get(col('quà tặng'))):
                gift_ids = str(row.get(col('quà tặng'))).split(',')
                for gift_id in gift_ids:
                    if gift_id.strip():
                        gifts.append(Gift.objects.get(id=int(gift_id)))

            # Chuyển đổi trạng thái
            status_raw = row.get(col('tình trạng'))
            status_key = status_mapping.get(str(status_raw).strip(), 'new')

            # Tạo đối tượng Product
            product = Product(
                name=row.get(col('tên')),
                description=row.get(col('mô tả')),
                image=row.get(col('ảnh 1')),
                brand=brand,
                category=category,
                stock_quantity=stock_quantity,
                sold_quantity=sold_quantity,
                rating=rating,
                import_price=import_price,
                original_price=original_price,
                discounted_price=discounted_price,
                status=status_key,
            )
            product.save()

            # Gán các trường ManyToMany
            product.tags.set(tags)
            product.gifts.set(gifts)

            print(f"✅ Đã nhập thành công sản phẩm: {product.name}")

        except KeyError as e:
            print(f"❌ Thiếu cột dữ liệu: {e}. Vui lòng kiểm tra lại tiêu đề cột trong Excel.")
        except ValueError as e:
            print(f"❌ Lỗi chuyển đổi dữ liệu cho sản phẩm '{row.get(col('tên'), 'Không rõ') if 'tên' in normalized_columns else 'Không rõ'}': {e}.")
        except Brand.DoesNotExist:
            print(f"❌ Lỗi: Không tìm thấy Brand với ID. Bỏ qua sản phẩm: {row.get(col('tên'), 'Không rõ')}")
        except Category.DoesNotExist:
            print(f"❌ Lỗi: Không tìm thấy Category với ID. Bỏ qua sản phẩm: {row.get(col('tên'), 'Không rõ')}")
        except Tag.DoesNotExist as e:
            print(f"❌ Lỗi: Không tìm thấy Tag với ID. Bỏ qua sản phẩm: {row.get(col('tên'), 'Không rõ')}")
        except Gift.DoesNotExist as e:
            print(f"❌ Lỗi: Không tìm thấy Gift với ID. Bỏ qua sản phẩm: {row.get(col('tên'), 'Không rõ')}")
        except IntegrityError as e:
            print(f"⚠️ Lỗi toàn vẹn dữ liệu cho sản phẩm {row.get(col('tên'), 'Không rõ')}: {e}. Có thể sản phẩm đã tồn tại.")
        except Exception as e:
            print(f"❌ Lỗi không xác định khi nhập sản phẩm: {e}")


# Chạy hàm chính
if __name__ == "__main__":
    # Mặc định tìm file trong thư mục static nếu chạy cục bộ
    file_name = os.environ.get('PRODUCT_IMPORT_FILE', 'static/Sanpham.xlsx')
    print(f"Nguồn dữ liệu: {file_name}")
    import_products_from_excel(file_name)