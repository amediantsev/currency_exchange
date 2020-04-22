import requests
import os



def send_tel_message():
	bot_api_key = os.environ['TELEGRAM_BOT_API_KEY']
	channel_name = '@CurrencyExchangeBotHillel2'
	message = 'Hello world'

	url = f'https://api.telegram.org/bot{bot_api_key}/sendMessage?chat_id={channel_name}&text={message}'

	params = {
		'chat_id': channel_name,
		'text': message

	}

	return requests.get(url, params=params).json()

if __name__ == '__main__':
	print(send_tel_message())
