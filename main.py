from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler, ApplicationBuilder, CommandHandler, ContextTypes,  CallbackContext
import requests
from io import BytesIO  # PDF faylni yuklash uchun
from config import BASE_URL, BOT_TOKEN
from api import user_create


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Foydalanuvchini ro‘yxatdan o‘tkazish va salomlashish"""
    user = update.effective_user
    new_user = user_create(
        chat_id=user.id,
        username=user.username,
        full_name=user.full_name
    )
    print(new_user)
    await update.message.reply_text(f'Assalomu alaykum, {user.first_name}! 📚\nDarslik yuklash uchun /darslik buyrug‘ini bosing.')


async def textbooks_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchiga sinflar bo‘yicha darslik tanlash tugmalarini chiqarish"""
    keyboard = [
        [InlineKeyboardButton(f"{i}-sinf 📖", callback_data=f"class_{i}"),
         InlineKeyboardButton(f"{i + 1}-sinf 📖", callback_data=f"class_{i + 1}")]
        for i in range(1, 10, 2)
    ]
    keyboard.append([InlineKeyboardButton("11-sinf 📖", callback_data="class_11")])  # 12-sinfni chiqarib tashladik
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📚 Qaysi sinf darsliklarini yuklamoqchisiz?", reply_markup=reply_markup)


async def show_textbooks(update: Update, context: CallbackContext):
    """Tanlangan sinfga mos darsliklarni chiqarish"""
    query = update.callback_query
    await query.answer()

    class_number = query.data.split("_")[1]  # "class_7" -> "7"
    print(f"Tanlangan sinf: {class_number}")  # Diagnostika uchun

    response = requests.get(f"{BASE_URL}/textbooks/?grade={class_number}")
    print(f"API so‘rovi: {response.url}")  # So‘rov URL'ini tekshirish
    print(f"API javobi: {response.status_code}, {response.json()}")  # API javobi

    if response.status_code == 200:
        textbooks = response.json()

        if isinstance(textbooks, list) and textbooks:
            keyboard = [[InlineKeyboardButton(book["subject"], callback_data=f"textbook_{book['id']}")]
                        for book in textbooks if str(book.get("grade")) == class_number]

            if keyboard:
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(f"{class_number}-sinf darsliklari:", reply_markup=reply_markup)
            else:
                await query.edit_message_text(f"❌ {class_number}-sinf uchun darslik topilmadi.")
        else:
            await query.edit_message_text("❌ Bu sinf uchun darsliklar mavjud emas.")
    else:
        await query.edit_message_text("❌ Xatolik yuz berdi, keyinroq urinib ko‘ring.")
async def send_textbooks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tanlangan darslik PDF faylini yuborish"""
    query = update.callback_query
    await query.answer()

    book_id = query.data.split("_")[1]  # "textbook_5" -> "5"

    response = requests.get(f"{BASE_URL}/textbooks/{book_id}/")  # ID bo‘yicha so‘rov yuboriladi

    print(f"APIga so‘rov yuborildi: {BASE_URL}/textbooks/{book_id}/")  # Diagnostika uchun
    print(f"API javobi: {response.status_code}, {response.text}")  # API natijalarini ko‘rish

    if response.status_code == 200:
        book = response.json()
        pdf_url = book.get("file")  # PDF fayl URL
        subject = book.get("subject", "Noma’lum fan")

        if pdf_url:
            # PDF faylni yuklab olish
            pdf_response = requests.get(pdf_url)
            if pdf_response.status_code == 200 and "application/pdf" in pdf_response.headers.get("Content-Type", ""):
                pdf_data = BytesIO(pdf_response.content)
                pdf_data.name = f"{subject}.pdf"

                await query.message.reply_document(document=pdf_data, caption=f"{subject} 📘")
            else:
                await query.message.reply_text(f"{subject} PDF faylini yuklab bo‘lmadi. URL: {pdf_url}")
        else:
            await query.message.reply_text(f"{subject} PDF fayli mavjud emas.")
    else:
        await query.message.reply_text("❌ Xatolik yuz berdi, keyinroq urinib ko‘ring.")



DJANGO_API_URL = "http://127.0.0.1:8000/api/books/"

response = requests.get(DJANGO_API_URL)
if response.status_code == 200:
    books = response.json()
    print("Darsliklar:", books)
else:
    print("Django API bilan bog‘lanishda xatolik:", response.status_code)


def main():
    """Botni ishga tushiruvchi asosiy funksiya"""
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    print("✅ Bot ishga tushdi!")

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("darslik", textbooks_handler))
    app.add_handler(CallbackQueryHandler(show_textbooks, pattern=r"^class_\d+$"))
    app.add_handler(CallbackQueryHandler(send_textbooks, pattern=r"^textbook_\d+$"))

    app.run_polling()


if __name__ == "__main__":
    main()

