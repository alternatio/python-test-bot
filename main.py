from datetime import datetime
from telegram import ReplyKeyboardMarkup, Update
import telegram
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import openmeteo_requests
import requests_cache
from retry_requests import retry
import requests

# tokens
token = '7196211677:AAGOOhXfXz1YKECq7-9jHzz_xYQxmeR6qDs'
weatherText = 'Получить текущую погоду в моём городе'

# api data
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# изменение формата даты
def change_date_format(iso_date):
  date_object = datetime.fromisoformat(iso_date)
  return date_object.strftime("%d.%m %H:%M")

# получение погоды
async def getWeather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  # запрос
  url = "https://api.open-meteo.com/v1/forecast"
  params = {
    "latitude": 54.9924,
    "longitude": 73.3686,
    "hourly": "temperature_2m",
  }
  response = requests.get(url, params)
  preparedResponse = response.json()

  # обработка запроса
  temperatureUnit = preparedResponse['hourly_units']['temperature_2m']
  preparedResponse['hourly']['time'] = [change_date_format(date) for date in preparedResponse['hourly']['time']]
  
  result = 'Вот сегодняшняя погода в Омске:\n\n`'
  for i in range(24):
    result += f'{preparedResponse['hourly']['time'][i]}      '
    result += f'{preparedResponse['hourly']['temperature_2m'][i]} {temperatureUnit}\n'
  result += '`'

  # вывод
  await update.message.reply_text(
    f'{result}',
    parse_mode=telegram.constants.ParseMode.MARKDOWN_V2
  )

# start
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  keyboard = [
    [weatherText],
  ]
  reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
  
  await update.message.reply_text(
    f'Привет, {update.effective_user.first_name}, я могу предоставить вам информацию о текущей погоде в вашем городе!',
    reply_markup=reply_markup
  )


app = ApplicationBuilder().token(token).build()
app.add_handler(CommandHandler("start", hello))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex(f'^{weatherText}$'), getWeather))
app.run_polling()