import os
import telebot 
import requests
from decouple import config

KEY = config('YOUR_API_KEY')
API_KEY = config('YOUR_X_API_KEY')

def run_query(query):    
    headers = {'X-API-KEY': API_KEY}
    request = requests.post('https://graphql.bitquery.io/',
                            json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception('Query failed and return code is {}.      {}'.format(request.status_code,
                        query))


# The GraphQL query
query = """
{
  ethereum(network: bsc) {
    dexTrades(
      baseCurrency: {is: "0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82"}
      quoteCurrency: {is: "0x55d398326f99059ff775485246999027b3197955"}
      options: {desc: ["block.height", "transaction.index"], limit: 1}
    ) {
      block {
        height
        timestamp {
          time(format: "%Y-%m-%d %H:%M:%S")
        }
      }
      transaction {
        index
      }
      baseCurrency {
        symbol
      }
      quoteCurrency {
        symbol
      }
      quotePrice
    }
  }
}
"""
result = run_query(query)  
quotePrice = result.get('data').get('ethereum').get('dexTrades')[0].get('quotePrice') 

# Telegram Bot instance
bot = telebot.TeleBot(KEY)

def greeting(message):
	request = message.text.split()
	if len(request) < 2 and request[0].lower() in "hello" or request[0].lower() in "hi" or request[0].lower() in "hey":
		return True
	else:
		return False
		
def updated_price(message):
	request = message.text.split()
	if len(request) == 2 and request[0].lower() in "get" and request[1].lower() in "price":
		return True
	else:
		return False

def thanks(message):
	request = message.text.split()
	if len(request) <= 4 and request[0].lower() in "thanks" or request[0].lower() in "thnx" or request[0].lower() in "thank":
		return True
	else:
		return False


@bot.message_handler(func=greeting)
def send_message(message):
	bot.send_message(message.chat.id, "Hey! Glad to see your. I am Bitquery Updated Coin Price Bot. Please type GET PRICE to see the latest Ethereum blockchain price.")

@bot.message_handler(func=updated_price)
def send_updated_price(message):
	bot.send_message(message.chat.id, str(quotePrice))

@bot.message_handler(func=thanks)
def send_thank_you(message):
	bot.reply_to(message, "It was a pleasure to help you.")

print("Bitquery Bot running...")

bot.polling()