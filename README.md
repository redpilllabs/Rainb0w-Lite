# Rainb0w Lite Proxy Installer

**اطلاعیه: استفاده از این نصاب یا هرگونه تعلقات آن برای حامیان رژیم جنایتکار و اشغالگر جمهوری اسلامی مطلقا ممنوع و شرعا حرام است!**

این اسکریپت به شما کمک می‌کند چندین پروتکل مختلف پروکسی که در مقابل سیستم فیلترینگ GFI/GFW کارایی دارند را  بر روی سرور لینوکس خود **بدون نیاز به دامنه** راه‌اندازی نمایید. به یاد کیان پیرفلک، مهندس کوچک و شهید انقلاب #زن_زندگی_آزادی .

## ویژگی ها

### 🚀 پروکسی

- VLESS REALITY [TCP]
- Hysteria [UDP]
- MTProto

### 🔑 امنیت و دسترسی

- حالت پارانوید: مسدود کردن تمام اتصالات ورودی به غیر از آی‌پی ایران برای مقابله با Active Probing
- جلوگیری از لو رفتن و مسدود شدن سرور با مسدود کردن اتصال خروجی به ایران و وبسایت های ایرانی هم از طریق آی‌پی و هم از طریق دامنه ir.
- امکان مسدود کردن وبسایت های پورنو گرافی

### 👥 مدیریت کاربران

- امکان حذف و اضافه کاربران از طریق ترمینال فقط با وارد کردن نام دلخواه و تولید تمام پارامترهای لازم بطور خودکار
- ارائه تمام لینک های اشتراکی برای هر کاربر و همچین ساختن  QR Code و فایل های JSON برای کلاینت ها
- امکان پشتیبان گیری از تنظیمات و فهرست کاربران

### 📐 بهینه سازی

- استفاده از Docker برای راه اندازی سریع و دستکاری حداقلی فایل های سیستمی
- مسدودسازی تبلیغات توسط AdGuard DNS روی تمام پروکسی ها بدون نیاز به نصب نرم افزار از جانب کاربر
- استفاده از آخرین نسخه ی ایمیج های رسمی داکر هر پروکسی

## نیازمندی ها

- یک سرور مجازی لینوکس با مشخصات حداقلی زیر

  - OS: Debian 11 or Ubuntu 20.04, 22.04
  - Memory: 256MB
  - Storage: 5GB NVME or SSD
  - Virtualization: KVM (OpenVZ and NAT servers are not supported)

## نحوه نصب

```
apt install git
git clone https://github.com/redpilllabs/Rainb0w-Lite.git
cd Rainb0w-Lite
./run.sh
```

برای راهنمای تصویری نصب به قسمت [ویکی](https://github.com/redpilllabs/Rainb0w-Lite/wiki) پروژه مراجعه نمایید.

# نکته مهم برای هیستریا

متاسفانه لینک های اشتراک هیستریا شامل تمام پارامتر های مورد نیاز برای استفاده نیستند و پس از اضافه کردن کانفیگ از طریق لینک یا کیو آر کد باید به تنظیمات کانفیگ رفته و مقادیر زیر رو بطور دستی اعمال کنید:

```
Authentication Type:  BASE64
Disable MTU Path Discovery: Enabled
Upload Speed:   YOUR REAL UPLOAD SPEED
Download Speed: YOUR REAL DOWNLOAD SPEED
QUIC Stream Receive Window: 1677768
QUIC Connection Receive Window: 4194304
```

## راه های ارتباطی

- طرح سوال ها در قسمت Discussion همین مخزن
- طرح مشکلات در قسمت Issues
